"""
API v1 router.
"""

from fastapi import APIRouter

from app.api.v1 import contacts, groups, messages, upload, users, websocket

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(messages.router)
api_router.include_router(groups.router)
api_router.include_router(contacts.router)
api_router.include_router(websocket.router)
api_router.include_router(upload.router)
