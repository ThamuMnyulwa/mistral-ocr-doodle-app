import pytest
import sys
from pathlib import Path

# Add the app directory to the Python path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

# Common fixtures can be added here if needed
