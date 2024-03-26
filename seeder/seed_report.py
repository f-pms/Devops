import random
import json
from datetime import datetime, timedelta

year_count = 5


# Function to generate SQL rows
def generate_sql_rows():
    sql_rows = []
    sum_json_map = {}
    for i in range(year_count * 365):
        recording_date = datetime.now() - timedelta(days=i)
        sum_json_map[recording_date.strftime("%Y-%m-%d")] = {}
        for type_id in range(1, 3):
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

            sum_json = "[{}, {}]".format(shift, shift)
            sum_json_map[recording_date.strftime("%Y-%m-%d")][
                "DAM" if type_id == 1 else "BTP"
            ] = eval(sum_json)

            sql = "INSERT INTO report (recording_date, sum_json, type_id) VALUES ('{}', '{}', {});".format(
                recording_date.strftime("%Y-%m-%d"), sum_json, type_id
            )
            sql_rows.append(sql)
    return {"sql": sql_rows, "sum_json": sum_json_map}


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
