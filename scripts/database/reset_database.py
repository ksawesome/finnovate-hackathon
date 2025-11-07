"""Reset PostgreSQL database schema."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_postgres_engine
from src.db.postgres import Base


def reset_database():
    """Drop all tables and recreate them."""
    print("\n🔄 Resetting PostgreSQL database...")

    engine = get_postgres_engine()

    # Drop all tables
    print("   ⚠️  Dropping all existing tables...")
    Base.metadata.drop_all(engine)
    print("   ✅ All tables dropped")

    # Recreate tables
    print("   🔧 Creating tables with new schema...")
    Base.metadata.create_all(engine)
    print("   ✅ All tables recreated")

    print(f"\n✅ Database reset complete! {len(Base.metadata.tables)} tables ready.")
    for table_name in Base.metadata.tables.keys():
        print(f"     • {table_name}")


if __name__ == "__main__":
    reset_database()
