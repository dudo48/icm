from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

CONFIG = PROJECT_ROOT.joinpath("config.toml")
CONFIG_EXAMPLE = PROJECT_ROOT.joinpath("config.example.toml")

DATA_FOLDER = PROJECT_ROOT.joinpath("data")
DATA_FOLDER.mkdir(exist_ok=True)

DATABASE = DATA_FOLDER.joinpath("database.db")
LOG = DATA_FOLDER.joinpath("log.txt")
REPORT_TABLE_TEMPLATE = DATA_FOLDER.joinpath("report_template.html")
REPORT_TABLE = DATA_FOLDER.joinpath("report.html")
REPORT_VISUAL = DATA_FOLDER.joinpath("report.png")
