from unittest.mock import AsyncMock, patch

import pytest

from app.models.user import Base

import app.core.database as database_module


class TestInitDB:
    async def test_init_db_calls_create_all(self):
        mock_conn = AsyncMock()
        mock_begin_ctx = AsyncMock()
        mock_begin_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin_ctx.__aexit__ = AsyncMock(return_value=None)

        with patch.object(database_module, "engine") as mock_engine:
            mock_engine.begin.return_value = mock_begin_ctx
            await database_module.init_db()

        mock_conn.run_sync.assert_called_once()
        callback = mock_conn.run_sync.call_args[0][0]
        assert callback == Base.metadata.create_all
