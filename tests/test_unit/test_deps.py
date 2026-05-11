import pytest
from unittest.mock import AsyncMock, patch

from app.api.deps import get_db


class TestGetDB:
    async def test_get_db_normal_flow(self):
        mock_session = AsyncMock()
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch("app.api.deps.async_session_factory", return_value=mock_ctx):
            gen = get_db()
            session = await gen.__anext__()
            assert session is mock_session

            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()

            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    async def test_get_db_rollback_on_commit_error(self):
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock(side_effect=RuntimeError("commit failed"))
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch("app.api.deps.async_session_factory", return_value=mock_ctx):
            gen = get_db()
            await gen.__anext__()

            with pytest.raises(RuntimeError, match="commit failed"):
                with pytest.raises(StopAsyncIteration):
                    await gen.__anext__()

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    async def test_get_db_rollback_on_handler_exception(self):
        mock_session = AsyncMock()
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch("app.api.deps.async_session_factory", return_value=mock_ctx):
            gen = get_db()
            await gen.__anext__()

            with pytest.raises(ValueError, match="handler error"):
                await gen.athrow(ValueError("handler error"))

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
