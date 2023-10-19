import os

from constants import PROJECT_ROOT

csv_database = os.path.join(PROJECT_ROOT, 'databases/database.csv')
sql_database = os.path.join(PROJECT_ROOT, 'databases/database.db')

next_datetime = os.path.join(PROJECT_ROOT, 'temp/next_datetime')
previous_record = os.path.join(PROJECT_ROOT, 'temp/previous_record.json')

log = os.path.join(PROJECT_ROOT, 'debug/log.txt')
report = os.path.join(PROJECT_ROOT, 'debug/report.txt')
