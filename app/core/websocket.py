"""
WebSocket connection manager for real-time communication.
"""

import json
from typing import Any
from uuid import UUID

from fastapi import WebSocket
from redis.asyncio import Redis

from app.core.config import settings


class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""

    def __init__(self, redis: Redis | None = None):
        """Initialize connection manager."""
        # In-memory storage: user_id -> WebSocket
        self.active_connections: dict[UUID, WebSocket] = {}
        # Group rooms: group_id -> set of user_ids
        self.group_rooms: dict[UUID, set[UUID]] = {}
        # Redis for pub/sub (optional, for scaling)
        self.redis = redis
        self.pubsub = None
        if redis:
            self.pubsub = redis.pubsub()

    async def connect(self, websocket: WebSocket, user_id: UUID) -> None:
        """Store WebSocket connection (websocket should already be accepted)."""
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, user_id: UUID) -> None:
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
        # Remove from all group rooms
        for group_id in list(self.group_rooms.keys()):
            self.group_rooms[group_id].discard(user_id)
            if not self.group_rooms[group_id]:
                del self.group_rooms[group_id]

    async def join_group(self, user_id: UUID, group_id: UUID) -> None:
        """Add user to group room."""
        if group_id not in self.group_rooms:
            self.group_rooms[group_id] = set()
        self.group_rooms[group_id].add(user_id)

    async def leave_group(self, user_id: UUID, group_id: UUID) -> None:
        """Remove user from group room."""
        if group_id in self.group_rooms:
            self.group_rooms[group_id].discard(user_id)
            if not self.group_rooms[group_id]:
                del self.group_rooms[group_id]

    async def send_personal_message(self, message: dict[str, Any], receiver_id: UUID) -> bool:
        """Send message to specific user."""
        if receiver_id in self.active_connections:
            websocket = self.active_connections[receiver_id]
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                print(f"Error sending WebSocket message to {receiver_id}: {e}")
                await self.disconnect(receiver_id)
                return False
        else:
            active_connections = list(self.active_connections.keys())
            print(f"User {receiver_id} is not connected. Active connections: {active_connections}")
        return False

    async def broadcast_to_group(
        self, message: dict[str, Any], group_id: UUID, exclude_user_id: UUID | None = None
    ) -> int:
        """Broadcast message to all users in a group."""
        if group_id not in self.group_rooms:
            return 0

        sent_count = 0
        disconnected_users = []

        for user_id in self.group_rooms[group_id]:
            if exclude_user_id and user_id == exclude_user_id:
                continue

            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                try:
                    await websocket.send_json(message)
                    sent_count += 1
                except Exception:
                    disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.disconnect(user_id)

        # If Redis is available, publish to Redis for other instances
        if self.redis:
            await self.redis.publish(
                f"{settings.REDIS_PUBSUB_CHANNEL}:{group_id}",
                json.dumps(message),
            )

        return sent_count

    async def broadcast_online_status(
        self, user_id: UUID, is_online: bool, exclude_user_id: UUID | None = None
    ) -> None:
        """Broadcast user online status to all connected users."""
        message = {
            "type": "online_status",
            "user_id": str(user_id),
            "is_online": is_online,
        }

        for uid, websocket in list(self.active_connections.items()):
            if exclude_user_id and uid == exclude_user_id:
                continue
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(uid)

    def is_connected(self, user_id: UUID) -> bool:
        """Check if user is connected."""
        return user_id in self.active_connections

    def get_online_users(self) -> list[UUID]:
        """Get list of online user IDs."""
        return list(self.active_connections.keys())


# Global connection manager instance (will be initialized in main.py with Redis)
manager: ConnectionManager | None = None


async def get_manager() -> ConnectionManager:
    """Get or create connection manager."""
    global manager
    if manager is None:
        from app.core.redis import get_redis

        try:
            redis = await get_redis()
            manager = ConnectionManager(redis=redis)
        except Exception:
            # Fallback to in-memory if Redis unavailable
            manager = ConnectionManager()
    return manager
