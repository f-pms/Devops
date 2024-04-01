import random
import json
from datetime import datetime, timedelta
import pytz

year_count = 6
date_format_pattern = "%Y-%m-%d %H:%M:%S %:z"
report_type_map = {
    1: "DAM",
    2: "BTP",
}

report_type_device_count_map = {
    1: 11,
    2: 16,
}

shift_map = {
    1: "I",
    2: "II",
}

big_indicators = [
    "DAM_2",
    "BTP_7",
]

additional_sum_with_list_specific_index_for_report_type = {
    1: {
        "SUM_DAM_CATEGORY_1": {"list": [1, 2, 3]},
        "SUM_DAM_CATEGORY_2.1": {"list": [4, 5, 6]},
        "SUM_DAM_CATEGORY_2.2": {"list": [8, 9, 10, 11]},
    },
    2: {
        "SUM_BTP_CATEGORY_1": {"list": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
        "SUM_BTP_CATEGORY_2": {"list": [10]},
        "SUM_BTP_CATEGORY_3": {"list": [11, 12, 13, 14, 15]},
        "SUM_BTP_CATEGORY_4.1": {"factor": 0.65, "list": [16]},
        "SUM_BTP_CATEGORY_4.1": {"factor": 0.35, "list": [16]},
    },
}


# Function to generate SQL rows
def generate_report_sql():
    sql_rows = []
    sum_json_map = {}
    id_count = 1
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
                get_sumjson_shift_random(type_id), get_sumjson_shift_random(type_id)
            )
            sum_json_map[recording_date.strftime(date_format_pattern)][
                report_type_map[type_id]
            ] = eval(sum_json)

            sql = "INSERT INTO report (recording_date, sum_json, type_id) VALUES ('{}', '{}', {});".format(
                recording_date.strftime(date_format_pattern), sum_json, type_id
            )
            sql_rows.append(sql)
            indicators_sql = generate_report_row_sql(type_id, id_count)
            id_count += 1
            sql_rows.extend(indicators_sql)
    return {"sql": sql_rows, "sum_json": sum_json_map}


def generate_report_row_sql(type_id, report_id):
    default_double = 10.0
    sql_rows = []

    sql_values = []
    for shift in range(1, 3):
        for deviceNo in range(1, report_type_device_count_map[type_id] + 1):
            indicator = f"{report_type_map[type_id]}_{deviceNo}"
            multiply_factor = get_multiply_factor(indicator)

            sql_value_string = "('{}', '{}', {}, {}, {}, {}, {}, {})".format(
                indicator,
                shift_map[shift],
                default_double * multiply_factor,
                default_double * 2 * multiply_factor,
                default_double * 3 * multiply_factor,
                default_double * 4 * multiply_factor,
                default_double * 5 * multiply_factor,
                report_id,
            )
            sql_values.append(sql_value_string)

    batch_shift_sql = """INSERT INTO report_row (indicator, shift, old_electric_value, new_electric_value1, new_electric_value2, new_electric_value3, new_electric_value4, report_id) 
                VALUES {};""".format(
        ",".join(sql_values)
    )
    sql_rows.append(batch_shift_sql)

    return sql_rows


def get_multiply_factor(indicator):
    if indicator in big_indicators:
        return 10
    else:
        return 1


def get_sum_specific_list_value(type):
    result = []

    if type == 1:
        for i in range(1, 4):
            result.append(random.randint(1, 100))
    else:
        for i in range(1, 17):
            if i != 10:
                result.append(random.randint(1, 100))

    return result


def get_sumjson_shift_random(type_id):
    sumPeak = random.randint(1, 100)
    sumOffPeak = random.randint(1, 100)
    sumStandard = random.randint(1, 100)

    sum_specifics_vals = get_sum_specific_list_value(type_id)
    sum_list_str = list(
        map(
            lambda x, i: '"SUM_SPECIFIC_{}":{}'.format(i + 1, x),
            sum_specifics_vals,
            range(0, sum_specifics_vals.__len__()),
        )
    )

    additionalSums = additional_sum_with_list_specific_index_for_report_type[type_id]
    additionalSumsStrs = []
    for key, value in additionalSums.items():
        list_specific = map(lambda x: sum_specifics_vals[0], value["list"])

        if "factor" in value:
            additionalSumsStrs.append(
                '"{}":{}'.format(key, sum(list_specific) * value["factor"])
            )
        else:
            additionalSumsStrs.append('"{}":{}'.format(key, sum(list_specific)))

    sum_list_str.extend(additionalSumsStrs)
    sum_specifics_str = ", ".join(sum_list_str)
    # sum_specifics_vals = get_sum_specific_list_value(type_id)
    # alist = map(
    #     lambda x, i: '"SUM_SPECIFIC_{}":{}'.format(i + 1, x),
    #     sum_specifics_vals,
    #     range(0, sum_specifics_vals.__len__()),
    # )

    # sum_specifics_str = ", ".join(alist)

    shift = '{{"SUM_TOTAL": {}, "SUM_PEAK": {}, "SUM_OFFPEAK": {},	"SUM_STANDARD": {}, {}}}'.format(
        sumPeak + sumOffPeak + sumStandard,
        sumPeak,
        sumOffPeak,
        sumStandard,
        sum_specifics_str,
    )
    return shift


# Generate SQL rows
result = generate_report_sql()
sql_rows = result["sql"]

with open("seeder/reports.sql", "w+") as f:
    for line in sql_rows:
        f.write(line + "\n")

with open("seeder/sum_jsons.json", "w+") as f:
    f.write(json.dumps(result["sum_json"]))

# Print the SQL rows
for row in sql_rows:
    print(row)
