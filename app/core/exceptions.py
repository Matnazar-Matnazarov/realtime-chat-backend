"""
Custom exceptions.
"""

from fastapi import HTTPException, status


class ChatException(HTTPException):
    """Base exception for chat application."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundError(ChatException):
    """User not found exception."""

    def __init__(self, user_id: str):
        super().__init__(
            detail=f"User with ID {user_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class GroupNotFoundError(ChatException):
    """Group not found exception."""

    def __init__(self, group_id: str):
        super().__init__(
            detail=f"Group with ID {group_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedError(ChatException):
    """Unauthorized exception."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(ChatException):
    """Forbidden exception."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )
