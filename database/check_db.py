from dotenv import load_dotenv

load_dotenv()

import os
from sqlalchemy import create_engine, text, inspect

DATABASE_URL = os.environ.get("DATABASE_URL")
print(f"Connecting to: {DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

try:
    # Use a single connection for all queries
    with engine.connect() as conn:
        # Check tables
        result = conn.execute(
            text(
                """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
            )
        )

        tables = [row[0] for row in result]

        print(" Connected successfully!")
        print(f"\n Tables in database ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

        # Check each table's structure
        for table in tables:
            if table != "alembic_version":  # Skip alembic metadata table
                print(f"\n {table} table structure:")
                result = conn.execute(
                    text(
                        f"""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """
                    )
                )

                for row in result:
                    default = f" DEFAULT {row[3]}" if row[3] else ""
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    print(f"  - {row[0]:<20} {row[1]:<20} {nullable:<10} {default}")

        # Check foreign keys
        print("\n Foreign Key Constraints:")
        result = conn.execute(
            text(
                """
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            ORDER BY tc.table_name
        """
            )
        )

        fks = list(result)
        if fks:
            for row in fks:
                print(f"  - {row[0]}.{row[1]} -> {row[2]}.{row[3]}")
        else:
            print("  - No foreign keys found")

        # Check alembic migration version
        print("\n Alembic Migration Status:")
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        if version:
            print(f"  Current version: {version[0]}")
        else:
            print("  No migration version found")

except Exception as e:
    print(f"\n Error: {e}")
    import traceback

    traceback.print_exc()
