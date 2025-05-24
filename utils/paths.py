from pathlib import Path

# Define project root and log directory
PROJECT_ROOT = Path(__file__).parent.parent
PATH_LOG = PROJECT_ROOT / "logs"

# Create logs directory if it doesn't exist
PATH_LOG.mkdir(exist_ok=True) 