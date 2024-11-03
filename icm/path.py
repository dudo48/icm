from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATABASE_FOLDER = PROJECT_ROOT.joinpath("database")
LOG_FOLDER = PROJECT_ROOT.joinpath("log")

DATABASE_FOLDER.mkdir(exist_ok=True)
LOG_FOLDER.mkdir(exist_ok=True)

DATABASE = DATABASE_FOLDER.joinpath("database.db")
NEXT_RUN = DATABASE_FOLDER.joinpath("next_run")

LOG = LOG_FOLDER.joinpath("log.txt")
REPORT = LOG_FOLDER.joinpath("report.txt")

CONFIG = PROJECT_ROOT.joinpath("config.toml")
CONFIG_EXAMPLE = PROJECT_ROOT.joinpath("config.example.toml")
