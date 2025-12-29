"""
WebSocket API routes for real-time communication.
"""

import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_user_id_from_token
from app.core.websocket import get_manager
from app.db.base import AsyncSessionLocal, get_db
from app.models.user import User

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: UUID,
) -> None:
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()

    # Get token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    # Verify token and get user_id
    token_user_id = get_user_id_from_token(token, is_refresh=False)
    if not token_user_id or str(token_user_id) != str(user_id):
        await websocket.close(code=1008, reason="Invalid token")
        return

    manager = await get_manager()
    await manager.connect(websocket, user_id)

    # Update user online status
    from datetime import datetime

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_online = True
            user.last_seen = None
            await session.commit()
            # Broadcast online status
            await manager.broadcast_online_status(user_id, True, exclude_user_id=user_id)

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
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.is_online = False
                user.last_seen = datetime.now(settings.TZ_INFO)
                await session.commit()
                # Broadcast offline status
                await manager.broadcast_online_status(user_id, False)
