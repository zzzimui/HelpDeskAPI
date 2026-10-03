import psycopg
import pytest


DATABASE_URL = "postgresql://eu_usuario:123456@localhost:5432/helpdesk_db"

# Obtenha a URL de conexão das variáveis de ambiente ou defina uma padrão de teste
def test_database_connection():
    """Testa se é possível conectar ao PostgreSQL e executar um comando simples."""
    try:
        # Tenta estabelecer a conexão com o banco
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # Executa uma query leve para validar a resposta do banco
                cur.execute("SELECT 1;")
                resultado = cur.fetchone()
                
                # Valida se o retorno da consulta foi o esperado (1)
                assert resultado[0] == 1
    except psycopg.OperationalError as e:
        pytest.fail(f"A conexão com o PostgreSQL falhou: {e}")