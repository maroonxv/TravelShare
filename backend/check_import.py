try:
    from sqlalchemy.exc import IntegrityError
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
