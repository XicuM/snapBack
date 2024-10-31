import sys
import pytest

# Skip the test if the platform is not Windows
pytestmark = pytest.mark.skipif(
    sys.platform != "win32", 
    reason="Test runs only on Windows"
)

def test_register_task():
    # Create task
    # Check if task exists
    pass