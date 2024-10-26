from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATABASES = PROJECT_ROOT.joinpath("databases")
LOG_FOLDER = PROJECT_ROOT.joinpath("log")

DATABASES.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

DATABASE = DATABASES.joinpath("database.db")
NEXT_RUN = DATABASES.joinpath("next_run")

LOG = LOG_FOLDER.joinpath("log.txt")
REPORT = LOG_FOLDER.joinpath("report.txt")
