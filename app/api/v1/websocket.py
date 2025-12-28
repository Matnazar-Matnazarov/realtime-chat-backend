"""
WebSocket API routes for real-time communication.
"""

import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.websocket import get_manager
from app.models.user import User

router = APIRouter(prefix="/ws", tags=["websocket"])


async def get_user_from_token(websocket: WebSocket) -> User | None:
    """Get user from WebSocket token (simplified - in production use proper auth)."""
    # In production, extract token from query params or headers
    # For now, we'll use query params: ?token=...
    token = websocket.query_params.get("token")
    if not token:
        return None

    # Decode token and get user (simplified)
    # In production, use proper JWT verification
    from app.core.security import decode_access_token

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Get user from database
    from sqlalchemy import select

    from app.db.base import AsyncSessionLocal
    from app.models.user import User

    async for session in AsyncSessionLocal():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    return None


@router.websocket("/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
) -> None:
    """WebSocket endpoint for real-time chat."""
    # In production, verify user from token
    # For now, we'll accept user_id from path (not secure, but works for development)
    # You should verify the token matches the user_id

    manager = await get_manager()
    await manager.connect(websocket, user_id)

    # Update user online status
    from datetime import datetime

    from sqlalchemy import select

    from app.db.base import AsyncSessionLocal
    from app.models.user import User

    async for session in AsyncSessionLocal():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_online = True
            user.last_seen = None
            await session.commit()
            # Broadcast online status
            await manager.broadcast_online_status(user_id, True, exclude_user_id=user_id)
        break

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type")

                if message_type == "join_group":
                    # Join a group room
                    group_id = UUID(message_data.get("group_id"))
                    await manager.join_group(user_id, group_id)

                elif message_type == "leave_group":
                    # Leave a group room
                    group_id = UUID(message_data.get("group_id"))
                    await manager.leave_group(user_id, group_id)

                elif message_type == "ping":
                    # Heartbeat
                    await websocket.send_json({"type": "pong"})

            except (json.JSONDecodeError, ValueError, KeyError) as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        await manager.disconnect(user_id)

        # Update user offline status
        async for session in AsyncSessionLocal():
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.is_online = False
                user.last_seen = datetime.now(settings.TZ_INFO)
                await session.commit()
                # Broadcast offline status
                await manager.broadcast_online_status(user_id, False)
            break
