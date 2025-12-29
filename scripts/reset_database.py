"""
Script to reset database: drop all tables, remove migrations, and recreate.
"""

import asyncio
import os
from pathlib import Path

from sqlalchemy import text

from app.core.config import settings
from app.db.base import engine


async def drop_all_tables() -> None:
    """Drop all tables from database."""
    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    print("✓ All tables dropped successfully!")


def remove_migration_files() -> None:
    """Remove all migration files except __init__.py."""
    migrations_dir = Path("alembic/versions")
    if not migrations_dir.exists():
        print("⚠ Migrations directory not found, skipping...")
        return

    print("Removing migration files...")
    removed_count = 0
    for file in migrations_dir.glob("*.py"):
        if file.name != "__init__.py":
            file.unlink()
            removed_count += 1
            print(f"  Removed: {file.name}")

    if removed_count == 0:
        print("  No migration files to remove.")
    else:
        print(f"✓ Removed {removed_count} migration file(s)!")


async def create_initial_migration() -> None:
    """Create initial migration from models."""
    print("\nCreating initial migration...")
    result = os.system("uv run alembic revision --autogenerate -m 'Initial migration'")
    if result != 0:
        raise RuntimeError("Failed to create initial migration")
    print("✓ Initial migration created!")


async def apply_migrations() -> None:
    """Apply migrations to database."""
    print("\nApplying migrations...")
    result = os.system("uv run alembic upgrade head")
    if result != 0:
        raise RuntimeError("Failed to apply migrations")
    print("✓ Migrations applied successfully!")


async def main() -> None:
    """Main function to reset database."""
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    db_name = (
        settings.DATABASE_URL.split("@")[-1]
        if "@" in settings.DATABASE_URL
        else settings.DATABASE_URL
    )
    print(f"Database: {db_name}")
    print()

    # Confirm action
    response = input("⚠️  WARNING: This will DELETE ALL DATA! Continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Operation cancelled.")
        return

    try:
        # Step 1: Drop all tables
        await drop_all_tables()

        # Step 2: Remove migration files
        remove_migration_files()

        # Step 3: Create new initial migration
        await create_initial_migration()

        # Step 4: Apply migrations
        await apply_migrations()

        print("\n" + "=" * 60)
        print("✅ DATABASE RESET COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run: uv run python scripts/seed_users.py")
        print("  2. Or run: make seed-users")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
