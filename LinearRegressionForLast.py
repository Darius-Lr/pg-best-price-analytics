import pandas as pd
import numpy as np


df = pd.read_excel("Project 2 Data.xlsx")
df["Final Price Month"] = pd.to_datetime(df["Final Price Month"])


def LinearRegression_TotalPrice(X, Y):
    X = np.array(X, dtype=float)
    Y = np.array(Y, dtype=float)

    N = len(X)
    sum_x_squared = np.sum(X ** 2)
    sum_x = np.sum(X)
    sum_xy = np.sum(X * Y)
    sum_y = np.sum(Y)

    A = np.array([[sum_x_squared, sum_x], [sum_x, N]], dtype=float)
    B = np.array([sum_xy, sum_y], dtype=float)

    sol = np.linalg.solve(A, B)
    return sol[0], sol[1]


months_to_use = int(input("How many months back do you want to use for linear regression? "))

if months_to_use < 2:
    raise ValueError("You must enter a number greater than or equal to 2.")


output_lines = []
price_columns = ["Final Price", "Feedstock Price", "Conversion Price", "Transport Price"]

for key, group in df.groupby(
    ["Material Type", "Material Sub Type", "Material Description", "Plant", "Supplier"],
    sort=False,
):
    group = group.sort_values("Final Price Month")
    group[price_columns] = group[price_columns].fillna(0)

    recent_group = group.tail(months_to_use).copy()
    data = recent_group[["Final Price Month", *price_columns]].values.tolist()

    output_lines.append(f"Group: {key}")
    output_lines.append(f"Months used for regression: {len(data)}")

    for row in data:
        output_lines.append(str(row))

    prices = [row[1] for row in data]

    if len(prices) < 2:
        output_lines.append("There are not enough data points to perform linear regression.")
        output_lines.append("")
        continue

    months = list(range(1, len(prices) + 1))

    a, b = LinearRegression_TotalPrice(months, prices)
    next_price = a * (len(prices) + 1) + b

    output_lines.append(f"Price for next month (Total Price): {next_price}")

    a_fs, b_fs = LinearRegression_TotalPrice(months, [row[2] for row in data])
    a_cp, b_cp = LinearRegression_TotalPrice(months, [row[3] for row in data])
    a_tp, b_tp = LinearRegression_TotalPrice(months, [row[4] for row in data])

    output_lines.append(f"Price for next month (Feedstock Price): {a_fs * (len(prices) + 1) + b_fs}")
    output_lines.append(f"Price for next month (Conversion Price): {a_cp * (len(prices) + 1) + b_cp}")
    output_lines.append(f"Price for next month (Transport Price): {a_tp * (len(prices) + 1) + b_tp}")
    output_lines.append("")


output_text = "\n".join(output_lines)

with open("outputForX.txt", "w", encoding="utf-8") as output_file:
    output_file.write(output_text)
