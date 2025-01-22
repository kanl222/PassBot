from __future__ import annotations

import asyncio
import json
import logging
import pickle
from typing import Any, Dict, Optional

import aiosqlite
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey

logger = logging.getLogger(__name__)


class SQLStorage(BaseStorage):
    """FSM storage using an SQLite database with asyncio support."""

    def __init__(self, db_path: str = "fsm_storage.db", serialization_method: str = "json"):
        """Initialize the storage."""
        self.db_path = db_path
        self.serialization_method = serialization_method
        self._connection: Optional[aiosqlite.Connection] = None 

    async def _get_connection(self) -> aiosqlite.Connection:
        """Get or create a database connection."""
        if self._connection is None:
            try:
                self._connection = await aiosqlite.connect(self.db_path)
                await self._connection.execute(
                    "CREATE TABLE IF NOT EXISTS fsm_data (key TEXT PRIMARY KEY, state TEXT, data BLOB)"
                )
                await self._connection.commit()
                logger.debug(f"Opened FSM storage database: {self.db_path}")
            except Exception as e:
                logger.error(f"Error opening database: {e}")
                raise  
        return self._connection

    def _serialize(self, data: Optional[Dict[str, Any]]) -> bytes:
        """Serialize data using the chosen method."""
        if self.serialization_method == "json":
            return json.dumps(data).encode()
        elif self.serialization_method == "pickle":
            return pickle.dumps(data)
        else:
            raise ValueError(f"Unknown serialization method: {self.serialization_method}")

    def _deserialize(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Deserialize data using the chosen method."""
        if self.serialization_method == "json":
            return json.loads(data.decode())
        elif self.serialization_method == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unknown serialization method: {self.serialization_method}")

    async def set_state(self, key: StorageKey, state: Optional[State] = None) -> None:
        """Set the state for the given key."""
        conn = await self._get_connection()
        state_str = state.state if state else None
        await conn.execute(
            "INSERT OR REPLACE INTO fsm_data (key, state, data) VALUES (?, ?, (SELECT data FROM fsm_data WHERE key = ?))",
            (self._key(key), state_str, self._key(key)),
        )
        await conn.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Get the state for the given key."""
        conn = await self._get_connection()
        row = await conn.execute("SELECT state FROM fsm_data WHERE key = ?", (self._key(key),))
        state = await row.fetchone()
        return state[0] if state else None

    async def set_data(self, key: StorageKey, data: Optional[Dict[str, Any]]) -> None:
        """Set the data for the given key."""
        conn = await self._get_connection()
        serialized_data = self._serialize(data)
        await conn.execute(
            "INSERT OR REPLACE INTO fsm_data (key, state, data) VALUES (?, (SELECT state FROM fsm_data WHERE key = ?), ?)",
            (self._key(key), self._key(key), serialized_data),
        )
        await conn.commit()

    async def get_data(self, key: StorageKey) -> Optional[Dict[str, Any]]:
        """Get the data for the given key."""
        conn = await self._get_connection()
        row = await conn.execute("SELECT data FROM fsm_data WHERE key = ?", (self._key(key),))
        data = await row.fetchone()
        return self._deserialize(data[0]) if data else None

    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update the data for the given key."""
        current_data = await self.get_data(key) or {}
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data

    async def close(self):
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug(f"Closed FSM storage database: {self.db_path}")

    def _key(self, key: StorageKey) -> str:
        """Generate a unique key for the given StorageKey."""
        return f"{key.bot_id}:{key.chat_id}:{key.user_id}"

