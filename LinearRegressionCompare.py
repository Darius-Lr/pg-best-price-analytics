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


def predict_next_value(values):
    months = list(range(1, len(values) + 1))
    a, b = LinearRegression_TotalPrice(months, values)
    return a * (len(values) + 1) + b


def format_number(value):
    return f"{float(value):.2f}"


def format_data_row(row):
    return str(
        [
            row["Final Price Month"],
            format_number(row["Final Price"]),
            format_number(row["Feedstock Price"]),
            format_number(row["Conversion Price"]),
            format_number(row["Transport Price"]),
        ]
    )


def format_comparison(label, predicted, actual):
    difference = predicted - actual
    abs_difference = abs(difference)

    if actual != 0:
        percent_error = abs_difference / abs(actual) * 100
        return (
            f"{label}: Predicted={format_number(predicted)}, Actual={format_number(actual)}, "
            f"Difference={format_number(difference)}, Abs Difference={format_number(abs_difference)}, "
            f"Percent Error={format_number(percent_error)}%"
        )

    return (
        f"{label}: Predicted={format_number(predicted)}, Actual={format_number(actual)}, "
        f"Difference={format_number(difference)}, Abs Difference={format_number(abs_difference)}, "
        "Percent Error=undefined (actual value is 0)"
    )


months_input = input(
    "Cate luni din urma vrei sa folosesti pentru comparatie? Scrie un numar sau 'all': "
).strip()

if months_input.lower() == "all":
    months_to_use = None
else:
    months_to_use = int(months_input)
    if months_to_use < 2:
        raise ValueError("Trebuie sa introduci un numar mai mare sau egal cu 2, sau 'all'.")


output_lines = []
price_columns = ["Final Price", "Feedstock Price", "Conversion Price", "Transport Price"]

for key, group in df.groupby(
    ["Material Type", "Material Sub Type", "Material Description", "Plant", "Supplier"],
    sort=False,
):
    group = group.sort_values("Final Price Month")
    group[price_columns] = group[price_columns].fillna(0)

    output_lines.append(f"Group: {key}")

    minimum_required = 3 if months_to_use is None else months_to_use + 1

    if len(group) < minimum_required:
        output_lines.append(
            f"Nu exista suficiente date pentru comparatie. "
            f"Sunt necesare cel putin {minimum_required} luni, dar grupul are doar {len(group)}."
        )
        output_lines.append("")
        continue

    if months_to_use is None:
        history_group = group.iloc[:-1].copy()
        last_month_row = group.iloc[-1]
    else:
        comparison_group = group.tail(months_to_use + 1).copy()
        history_group = comparison_group.iloc[:-1].copy()
        last_month_row = comparison_group.iloc[-1]

    output_lines.append(f"Months used for regression: {len(history_group)}")
    output_lines.append("Historical data used:")

    for _, row in history_group[["Final Price Month", *price_columns]].iterrows():
        output_lines.append(format_data_row(row))

    output_lines.append(f"Last actual month for comparison: {last_month_row['Final Price Month']}")
    output_lines.append(format_data_row(last_month_row))

    total_prediction = predict_next_value(history_group["Final Price"].tolist())
    feedstock_prediction = predict_next_value(history_group["Feedstock Price"].tolist())
    conversion_prediction = predict_next_value(history_group["Conversion Price"].tolist())
    transport_prediction = predict_next_value(history_group["Transport Price"].tolist())

    output_lines.append(format_comparison("Total Price", total_prediction, float(last_month_row["Final Price"])))
    output_lines.append(
        format_comparison("Feedstock Price", feedstock_prediction, float(last_month_row["Feedstock Price"]))
    )
    output_lines.append(
        format_comparison("Conversion Price", conversion_prediction, float(last_month_row["Conversion Price"]))
    )
    output_lines.append(
        format_comparison("Transport Price", transport_prediction, float(last_month_row["Transport Price"]))
    )
    output_lines.append("")


output_text = "\n".join(output_lines)

with open("outputCompare.txt", "w", encoding="utf-8") as output_file:
    output_file.write(output_text)
