import pandas as pd
from sklearn.linear_model import Lasso


DATA_FILE = "Project 2 Data.xlsx"
OUTPUT_FILE = "outputLasso3Param.txt"
ALPHA = 1.0
MAX_ITER = 10000
GROUP_COLUMNS = [
    "Material Type",
    "Material Sub Type",
    "Material Description",
    "Plant",
    "Supplier",
]
PRICE_COLUMNS = ["Final Price", "Feedstock Price", "Conversion Price", "Transport Price"]
FEATURE_COLUMNS = ["Feedstock Price", "Conversion Price", "Transport Price"]


def format_number(value):
    return f"{float(value):.2f}"


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


def format_coefficients(model, feature_names):
    parts = [f"Intercept={format_number(model.intercept_)}"]

    for feature_name, coefficient in zip(feature_names, model.coef_):
        parts.append(f"{feature_name}={format_number(coefficient)}")

    return ", ".join(parts)


def train_and_predict(train_frame, test_frame):
    model = Lasso(alpha=ALPHA, max_iter=MAX_ITER)
    model.fit(train_frame[FEATURE_COLUMNS], train_frame["Final Price"])
    prediction = model.predict(test_frame[FEATURE_COLUMNS])[0]
    return prediction, model


df = pd.read_excel(DATA_FILE)
df["Final Price Month"] = pd.to_datetime(df["Final Price Month"])

output_lines = [f"Lasso alpha used: {ALPHA}", f"Lasso max_iter used: {MAX_ITER}"]
errors = []

for key, group in df.groupby(GROUP_COLUMNS, sort=False):
    group = group.sort_values("Final Price Month").copy()
    group[PRICE_COLUMNS] = group[PRICE_COLUMNS].fillna(0)

    output_lines.append(f"Group: {key}")

    if len(group) < 2:
        output_lines.append(
            "Nu exista suficiente date pentru modelul Lasso cu 3 parametri. Sunt necesare cel putin 2 luni."
        )
        output_lines.append("")
        continue

    train_group = group.iloc[:-1].copy()
    test_group = group.iloc[[-1]].copy()
    actual_final_price = float(test_group.iloc[0]["Final Price"])

    output_lines.append(f"Training months: {len(train_group)}")
    output_lines.append(f"Last actual month for comparison: {test_group.iloc[0]['Final Price Month']}")
    output_lines.append(
        "Last month features: "
        f"Feedstock={format_number(test_group.iloc[0]['Feedstock Price'])}, "
        f"Conversion={format_number(test_group.iloc[0]['Conversion Price'])}, "
        f"Transport={format_number(test_group.iloc[0]['Transport Price'])}"
    )

    predicted_price, model = train_and_predict(train_group, test_group)
    errors.append(abs(predicted_price - actual_final_price))

    output_lines.append(
        format_comparison("Sklearn Lasso (3 params)", predicted_price, actual_final_price)
    )
    output_lines.append(
        "Coefficients: " + format_coefficients(model, FEATURE_COLUMNS)
    )
    output_lines.append("")

if errors:
    output_lines.append(
        f"Overall MAE for Sklearn Lasso (3 params): {format_number(sum(errors) / len(errors))}"
    )

output_text = "\n".join(output_lines)

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write(output_text)
