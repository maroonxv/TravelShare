import sys
import os

# Add backend directory to path so we can import shared modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sqlalchemy import text
from shared.database.core import engine

def migrate():
    print("Starting migration: Add media_url and reference_id to messages table...")
    
    with engine.connect() as connection:
        # We need to commit automatically or manage transactions
        # For simple DDL, we can execute directly.
        # Check if columns exist first or just try-catch?
        # MySQL doesn't support "IF NOT EXISTS" in ADD COLUMN standardly in older versions, 
        # but modern MySQL does. Let's assume standard ADD COLUMN.
        
        # We wrap in try-except to handle re-running
        
        try:
            print("Adding media_url column...")
            connection.execute(text("ALTER TABLE messages ADD COLUMN media_url VARCHAR(500) NULL;"))
            print("media_url added.")
        except Exception as e:
            print(f"Skipping media_url (probably exists): {e}")

        try:
            print("Adding reference_id column...")
            connection.execute(text("ALTER TABLE messages ADD COLUMN reference_id VARCHAR(36) NULL;"))
            print("reference_id added.")
        except Exception as e:
            print(f"Skipping reference_id (probably exists): {e}")
            
        connection.commit()

    print("Migration finished.")

if __name__ == "__main__":
    migrate()
