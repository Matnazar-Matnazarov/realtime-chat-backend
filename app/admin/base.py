"""
Base admin view with common functionality.
Eliminates code duplication across all admin views.
"""

import typing as tp
from uuid import UUID, uuid4

from fastadmin import SqlAlchemyModelAdmin


class BaseUUIDModelAdmin(SqlAlchemyModelAdmin):
    """Base admin view with UUID primary key auto-generation."""

    async def orm_save_obj(
        self, id: UUID | int | None, fields_payload: dict[str, tp.Any]
    ) -> tp.Any:
        """Override to auto-generate UUID if not provided.

        Args:
            id: Primary key ID (None for new objects)
            fields_payload: Dictionary of field values

        Returns:
            Saved model instance
        """
        if id is None and "id" not in fields_payload:
            fields_payload["id"] = uuid4()
        return await super().orm_save_obj(id, fields_payload)
