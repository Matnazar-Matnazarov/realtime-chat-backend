"""
Admin panel setup.
"""

# Import admin views to register them via @register decorator
from app.admin.admin import setup_admin
from app.admin.views import (  # noqa: F401
    ContactAdmin,
    GroupAdmin,
    GroupMemberAdmin,
    MessageAdmin,
    UserAdmin,
)

__all__ = ["setup_admin"]
