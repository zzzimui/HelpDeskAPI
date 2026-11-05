from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.database.integrity import translate_integrity_error
from app.exceptions.database import ForeignKeyViolationError
from app.modules.users.exceptions import UserHasAssociatedRecordsError
import app.modules.users.service as user_service


@pytest.mark.asyncio
async def test_delete_user_blocks_when_support_records_exist(monkeypatch):
    session = AsyncMock()
    session.scalar.return_value = True
    remove = AsyncMock()
    monkeypatch.setattr(user_service.crud_user, "remove", remove)
    user = SimpleNamespace(id=uuid4())

    with pytest.raises(UserHasAssociatedRecordsError):
        await user_service.delete_user(session, user)

    remove.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_user_removes_user_without_support_records(monkeypatch):
    session = AsyncMock()
    session.scalar.return_value = False
    remove = AsyncMock(return_value="deleted")
    monkeypatch.setattr(user_service.crud_user, "remove", remove)
    user = SimpleNamespace(id=uuid4())

    result = await user_service.delete_user(session, user)

    assert result == "deleted"
    remove.assert_awaited_once_with(db=session, id=user.id)


@pytest.mark.asyncio
async def test_delete_user_maps_foreign_key_race_to_conflict(monkeypatch):
    session = AsyncMock()
    session.scalar.return_value = False
    remove = AsyncMock(side_effect=ForeignKeyViolationError())
    monkeypatch.setattr(user_service.crud_user, "remove", remove)
    user = SimpleNamespace(id=uuid4())

    with pytest.raises(UserHasAssociatedRecordsError):
        await user_service.delete_user(session, user)


def test_integrity_translator_maps_postgres_foreign_key_violation():
    original_error = SimpleNamespace(sqlstate="23503")
    integrity_error = IntegrityError("DELETE", {}, original_error)

    translated_error = translate_integrity_error(integrity_error)

    assert isinstance(translated_error, ForeignKeyViolationError)
