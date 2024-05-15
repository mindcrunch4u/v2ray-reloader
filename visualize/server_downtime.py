from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
log_file_path = "log_controller_file.txt"

x_axis_hour = list(range(0, 24))

with open(log_file_path, "r") as log:
    columns = ["year", "month", "day", "hour", "minute", "second"]
    df = pd.DataFrame(columns=columns)
    for line in log:
        line = line.strip()
        temp_date = None
        if "Proxy Check Failed" in line and "At:" in line:
            date_string = line.split("At:")[1].split(",")[0].strip()
            temp_date = datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
            date_list = [temp_date.year, temp_date.month, temp_date.day,
                    temp_date.hour, temp_date.minute, temp_date.second]
            df.loc[-1] = date_list
            df.index += 1
        else:
            continue

    arr = np.array(df["hour"])
    labels, counts = np.unique(arr, return_counts=True)
    plt.bar(labels, counts, align='center')

    plt.xticks(np.arange(0, 24, 1))
    plt.savefig('test.png')
