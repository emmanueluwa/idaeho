"""
Database reset script - USE WITH CAUTION
Drops all tables including alembic_version
"""

from dotenv import load_dotenv

load_dotenv()

# Import models to register with Base.metadata
from models.audio import User, AudioFile, Playlist, PlaylistItem

from database.db import drop_tables, engine
from sqlalchemy import text


def reset_database():
    """Drop all tables and alembic version"""
    print("⚠️  WARNING: This will DELETE ALL DATA!")
    confirm = input("Type 'YES' to confirm: ")

    if confirm != "YES":
        print("❌ Reset cancelled")
        return

    print("\n🗑️  Dropping all tables...")

    try:
        # Drop model tables
        drop_tables()
        print("✅ Model tables dropped")

        # Drop alembic_version manually (not in models)
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            conn.commit()
        print("✅ Alembic version table dropped")

        # Verify everything is gone
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
                )
            )
            count = result.scalar()

        if count == 0:
            print("\n✅ Database reset complete! All tables dropped.")
        else:
            print(f"\n⚠️  Warning: {count} table(s) still exist")

        print("\n📝 Next steps:")
        print("  1. rm -rf alembic/versions/*.py")
        print("  2. alembic revision --autogenerate -m 'Initial schema'")
        print("  3. alembic upgrade head")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    reset_database()
