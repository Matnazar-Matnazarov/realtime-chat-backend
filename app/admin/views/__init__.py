"""
Admin views exports.
"""

from app.admin.views.contact import ContactAdmin
from app.admin.views.group import GroupAdmin, GroupMemberAdmin
from app.admin.views.message import MessageAdmin
from app.admin.views.user import UserAdmin

__all__ = [
    "UserAdmin",
    "MessageAdmin",
    "GroupAdmin",
    "GroupMemberAdmin",
    "ContactAdmin",
]
