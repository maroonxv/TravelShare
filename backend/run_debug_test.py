import pytest
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

if __name__ == "__main__":
    # Run the specific test file
    sys.exit(pytest.main(["backend/tests/integration/database/test_user_repo_int.py", "-v"]))
