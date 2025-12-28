"""
FastAdmin admin panel setup.
Clean, modular structure with separated concerns.
"""

from fastadmin import fastapi_app
from fastadmin.settings import settings as fastadmin_settings

from app.core.config import settings as app_settings

# Configure FastAdmin settings
fastadmin_settings.ADMIN_USER_MODEL = "User"
fastadmin_settings.ADMIN_USER_MODEL_USERNAME_FIELD = "username"
fastadmin_settings.ADMIN_SECRET_KEY = app_settings.SECRET_KEY


def setup_admin(app) -> None:
    """Setup FastAdmin admin panel.

    All admin views are automatically registered via @register decorator
    when views are imported in __init__.py. This function only mounts
    the FastAdmin app to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Mount FastAdmin app
    app.mount("/admin", fastapi_app)
