"""
API v1 router.
"""

from fastapi import APIRouter

from app.api.v1 import auth, contacts, groups, messages, oauth, upload, users, websocket

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])

# API routes
api_router.include_router(users.router)
api_router.include_router(messages.router)
api_router.include_router(groups.router)
api_router.include_router(contacts.router)
api_router.include_router(websocket.router)
api_router.include_router(upload.router)
