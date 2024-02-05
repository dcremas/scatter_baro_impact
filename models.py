import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv('PG_DB')
user = os.getenv('PG_USERNAME')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
port =os.getenv('PG_PORT')
          
url_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

query_stations = f'''
SELECT DISTINCT loc.station_name
FROM locations loc
JOIN obs_baro_impact obs
    ON loc.station = obs.station
JOIN regions rgn
    ON loc.state = rgn.state
ORDER BY loc.station_name;
'''

query_data = f'''
SELECT
obs.station,
obs.station_name,
obs.region,
obs.sub_region,
obs.state,
obs.date,
obs.rdg_year,
obs.rdg_month,
obs.rdg_day,
obs.rdg_hour,
obs.slp_3hr_diff,
obs.slp_6hr_diff,
obs.slp_24hr_diff
FROM obs_baro_impact obs
WHERE obs.rdg_year >= 2020
ORDER BY obs.station, obs.date;
'''

query_update = f'''
SELECT
MAX(timestamp)
FROM observations;
'''

headers = ['station', 'station_name', 'region', 'sub_region', 'state', 'date',
           'rdg_year', 'rdg_month', 'rdg_day', 'rdg_hour', 'slp_3hr_diff',
           'slp_6hr_diff', 'slp_24hr_diff']

with psycopg2.connect(url_string) as connection:
    cursor = connection.cursor()
    cursor.execute(query_stations)
    response_stations = cursor.fetchall()
    stations = [x[0] for x in response_stations]
    cursor.execute(query_data)
    response_data = cursor.fetchall()
    data = [x for x in response_data]
    cursor.execute(query_update)
    response_update = cursor.fetchall()
    time_update = response_update[0][0]
