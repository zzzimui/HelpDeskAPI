import jwt
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.datetime import get_utc
from uuid import uuid4
from sqlalchemy import select

# Exceptions
from pydantic import ValidationError
from app.modules.refresh_tokens.exceptions import InvalidRefreshTokenError
from jwt.exceptions import InvalidTokenError

# Core
from app.core import security
from app.core.config import settings

# Models
from app.modules.users.models import User
from app.modules.refresh_tokens.models import RefreshToken

# Schemas
from app.modules.refresh_tokens.schema import RefreshTokenPayload
from app.modules.auth.schema import TokenPair


# Padrões de seguranca aplicados:
    # 1: Hash do token no banco → vazamento do DB não compromete sessões.
    # 2: Rotação de refresh tokens → cada uso invalida o anterior (detecta roubo).
    # 3: Secrets separados para access e refresh.
    # 4: Validação em profundidade: JWT (exp, assinatura) + banco (revoked_at, expires_at, user_id).
    # 5: Transação atômica no refresh (revogar + emitir juntos).
    # 6: Erros genéricos (InvalidRefreshTokenError) para não vazar informação.
    # 7: Revogação idempotente no logout.

# Fluxo típico 

# Login  ──► issue()  ──► (access, refresh)  ──► cliente
#                             │
#                             ▼
# Cliente usa access até expirar
#                             │
#                             ▼
# refresh() ──► valida ──► revoga antigo ──► emite novo par
#                             │
#                             ▼
# Logout ──► revoke() ──► marca revoked_at


REFRESH_TOKEN_EXPIRES = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


async def _issue(db: AsyncSession, user: User, *, commit: bool = True) -> str:
    # O _ no início indica que é uso interno do módulo.
    # O commit=True por padrão permite reaproveitar essa função em transações maiores (como veremos em refresh)

    # token_id: identificador único do token (jti). Serve para localizá-lo no banco depois.
    token_id = uuid4()
    # now: timestamp atual em UTC, usado tanto para created_at quanto para calcular expires_at.
    now = get_utc()

    # Gera o JWT assinado contendo:
        # sub (subject) = ID do usuário
        # exp = data de expiração
        # jti = token_id
    encoded_token = security.create_refresh_token(
        subject=user.id,
        expires_delta=REFRESH_TOKEN_EXPIRES,
        token_id=token_id,
    )

    # O token não é armazenado em texto puro no banco:
        # Cria o registro no banco. Guardamos apenas o hash do token — se o banco vazar, ninguém consegue usar os tokens.
        # expires_at também é armazenado (dupla checagem: JWT já tem exp, mas o banco também valida).
    refresh_obj = RefreshToken(
        id=token_id,
        user_id=user.id,
        token_hash=security.hash_token(encoded_token),
        expires_at=now + REFRESH_TOKEN_EXPIRES,
        created_at=now,
    )
    
    db.add(refresh_obj)
    
    # Se commit=True, salva e atualiza o objeto (para ter o estado final do banco).
    # Retorna o token em texto puro — este é o único momento em que ele existe fora do hash.
    if commit:
        await db.commit()
        await db.refresh(refresh_obj)
    return encoded_token


async def issue(db: AsyncSession, user: User) -> str:
    """
    API pública para emitir token
    
    Emitir (issue) um refresh token (token de atualização) significa gerar 
    e entregar uma credencial de longa duração para um usuário ou aplicativo 
    cliente logo após a autenticação bem-sucedida

    - Wrapper público. Só delega para _issue() com commit=True (padrão).
    """
    return await _issue(db, user)


async def refresh(db: AsyncSession, token: str) -> TokenPair:
    """
    refresh() — o coração da rotação de tokens

    Recebe um refresh token, valida, revoga o antigo e emite um novo par (access + refresh). 
    Esse padrão é chamado refresh token rotation.
    """

    # Decodificar e validar o JWT
    try:
        # jwt.decode verifica assinatura e expiração.
        # RefreshTokenPayload(**...) valida o formato do payload via Pydantic (ex.: sub, jti obrigatórios).
        payload = RefreshTokenPayload(**jwt.decode(
            token,
            # Aqui usamos REFRESH_SECRET_KEY (separado do secret do access token). Se um vazar, o outro continua seguro.
            settings.REFRESH_SECRET_KEY,
            algorithms=[security.ALGORITHM],
        ))

    # Qualquer erro é convertido para InvalidRefreshTokenError — a camada de cima não precisa saber se o problema foi assinatura ou schema.
    except (InvalidTokenError, ValidationError):
        raise InvalidRefreshTokenError()

    # Buscar o token no banco
    refresh_obj = await db.scalar(
        select(RefreshToken).where(
            # Busca pelo id (= jti do payload) e pelo hash do token recebido.
            RefreshToken.id == payload.jti,
            # Comparar o hash é essencial: garante que o token apresentado é exatamente o que foi emitido (não basta ter o mesmo jti).
            RefreshToken.token_hash == security.hash_token(token),
        )
    )

    # Validar estado do token
    now = get_utc()

    # Cinco checagens de segurança: 
    if (
        # Token não existe no banco (nunca foi emitido ou foi deletado).
        refresh_obj is None
        # Inconsistência entre banco e JWT (possível adulteração)
        or refresh_obj.user_id != payload.sub
        # Token já foi usado/revogado (proteção contra replay).
        or refresh_obj.revoked_at is not None
        # Expirou no banco (redundante com o JWT, mas é defesa em profundidade).
        or refresh_obj.expires_at <= now
    ):
        raise InvalidRefreshTokenError()

    # Validar o usuário
    # Usuário pode ter sido deletado ou desativado. Nesses casos, não renovamos.
    user = await db.get(User, payload.sub)

    if user is None or not user.is_active:
        # Erro genérico InvalidRefreshTokenError para não vazar informação (ex.: "usuário inativo").
        raise InvalidRefreshTokenError()

    # Rotacionar o token
    # Revoga o token antigo (revoked_at = now). Assim, se alguém tentar reusá-lo, cai no passo 3 (validar estado do token: linha 115).
    refresh_obj.revoked_at = now
    # Emite um novo com commit=False, para que a revogação e a criação aconteçam na mesma transação. Se algo falhar, nada é salvo.
    new_refresh_token = await _issue(db, user, commit=False)
    # await db.commit() confirma as duas operações atomicamente. 
    await db.commit()
    # Esse é o ponto-chave do refresh token rotation: cada uso gera um novo token e invalida o anterior. 
    # Se um token roubado for usado, o legítimo falhará — sinal de comprometimento.


    # Retornar o par de tokens
    return TokenPair(
        # O access token é de curta duração (minutos) e não é persistido.
        access_token=security.create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        # O refresh token é de longa duração (dias) e é persistido (hash).
        refresh_token=new_refresh_token,
    )

#  logout / revogação
async def revoke(db: AsyncSession, token: str) -> None:
    # Busca apenas pelo hash (não precisa decodificar o JWT).
    refresh_obj = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == security.hash_token(token),
        )
    )

    # Se encontrado e ainda ativo, marca revoked_at.
    if refresh_obj is not None and refresh_obj.revoked_at is None:
        refresh_obj.revoked_at = get_utc()
        await db.commit()
    # Idempotente: chamar duas vezes não gera erro nem altera nada na segunda.
    # Não levanta exceção se o token não existir — útil para logout (não queremos vazar se o token era válido).