import random
import json
from datetime import datetime, timedelta
import pytz

year_count = 5
date_format_pattern = "%Y-%m-%d %H:%M:%S %:z"


# Function to generate SQL rows
def generate_sql_rows():
    sql_rows = []
    sum_json_map = {}
    for i in range(year_count * 365):
        recording_date = datetime.now(pytz.timezone("Asia/Bangkok")).replace(
            hour=6,
            minute=5,
            second=0,
            microsecond=0,
        ) - timedelta(days=i)

        sum_json_map[recording_date.strftime(date_format_pattern)] = {}
        for type_id in range(1, 3):
            sum_json = "[{}, {}]".format(
                get_shift_random(type_id), get_shift_random(type_id)
            )
            sum_json_map[recording_date.strftime(date_format_pattern)][
                "DAM" if type_id == 1 else "BTP"
            ] = eval(sum_json)

            sql = "INSERT INTO report (recording_date, sum_json, type_id) VALUES ('{}', '{}', {});".format(
                recording_date.strftime(date_format_pattern), sum_json, type_id
            )
            sql_rows.append(sql)
    return {"sql": sql_rows, "sum_json": sum_json_map}


def get_shift_random(type_id):
    sumPeak = random.randint(1, 100)
    sumOffPeak = random.randint(1, 100)
    sumStandard = random.randint(1, 100)

    if type_id == 1:
        sum_fields = ", ".join(
            [
                '"SUM_SPECIFIC_{}":{}'.format(j, random.randint(1, 100))
                for j in range(1, 4)
            ]
        )
    else:
        sum_fields = ", ".join(
            [
                '"SUM_SPECIFIC_{}":{}'.format(j, random.randint(1, 100))
                for j in range(1, 17)
                if j != 10
            ]
        )

    shift = '{{"SUM_TOTAL": {}, "SUM_PEAK": {}, "SUM_OFFPEAK": {},	"SUM_STANDARD": {}, {}}}'.format(
        sumPeak + sumOffPeak + sumStandard,
        sumPeak,
        sumOffPeak,
        sumStandard,
        sum_fields,
    )
    return shift


# Generate SQL rows
result = generate_sql_rows()
sql_rows = result["sql"]

with open("seeder/reports.sql", "w+") as f:
    for line in sql_rows:
        f.write(line + "\n")

with open("seeder/sum_jsons.json", "w+") as f:
    f.write(json.dumps(result["sum_json"]))

# Print the SQL rows
for row in sql_rows:
    print(row)
