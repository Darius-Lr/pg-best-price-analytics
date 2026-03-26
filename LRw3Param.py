import pandas as pd
from sklearn.linear_model import LinearRegression


DATA_FILE = "Project 2 Data.xlsx"
OUTPUT_FILE = "outputSklearn3Param.txt"
GROUP_COLUMNS = [
    "Material Type",
    "Material Sub Type",
    "Material Description",
    "Plant",
    "Supplier",
]
PRICE_COLUMNS = ["Final Price", "Feedstock Price", "Conversion Price", "Transport Price"]
FEATURE_COLUMNS_3 = ["Feedstock Price", "Conversion Price", "Transport Price"]
FEATURE_COLUMNS_4 = ["Feedstock Price", "Conversion Price", "Transport Price", "Previous Final Price"]


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


def train_and_predict(train_frame, test_frame, feature_names):
    model = LinearRegression()
    model.fit(train_frame[feature_names], train_frame["Final Price"])
    prediction = model.predict(test_frame[feature_names])[0]
    return prediction, model


df = pd.read_excel(DATA_FILE)
df["Final Price Month"] = pd.to_datetime(df["Final Price Month"])

output_lines = []
errors_3 = []
errors_4 = []

for key, group in df.groupby(GROUP_COLUMNS, sort=False):
    group = group.sort_values("Final Price Month").copy()
    group[PRICE_COLUMNS] = group[PRICE_COLUMNS].fillna(0)
    group["Previous Final Price"] = group["Final Price"].shift(1)

    output_lines.append(f"Group: {key}")

    if len(group) < 2:
        output_lines.append(
            "Nu exista suficiente date pentru modelul cu 3 parametri. Sunt necesare cel putin 2 luni."
        )
        output_lines.append("")
        continue

    train_3 = group.iloc[:-1].copy()
    test_3 = group.iloc[[-1]].copy()
    actual_final_price = float(test_3.iloc[0]["Final Price"])

    output_lines.append(f"Training months for 3-parameter model: {len(train_3)}")
    output_lines.append(f"Last actual month for comparison: {test_3.iloc[0]['Final Price Month']}")
    output_lines.append(
        "Last month features (3 params): "
        f"Feedstock={format_number(test_3.iloc[0]['Feedstock Price'])}, "
        f"Conversion={format_number(test_3.iloc[0]['Conversion Price'])}, "
        f"Transport={format_number(test_3.iloc[0]['Transport Price'])}"
    )

    predicted_3, model_3 = train_and_predict(train_3, test_3, FEATURE_COLUMNS_3)
    errors_3.append(abs(predicted_3 - actual_final_price))

    output_lines.append(
        format_comparison("Sklearn LinearRegression (3 params)", predicted_3, actual_final_price)
    )
    output_lines.append(
        "Coefficients (3 params): "
        + format_coefficients(model_3, FEATURE_COLUMNS_3)
    )

    valid_group_for_4 = group.dropna(subset=["Previous Final Price"]).copy()

    if len(valid_group_for_4) < 2:
        output_lines.append(
            "Nu exista suficiente date pentru modelul cu 4 parametri "
            "(Feedstock, Conversion, Transport, Previous Final Price)."
        )
        output_lines.append("")
        continue

    train_4 = valid_group_for_4.iloc[:-1].copy()
    test_4 = valid_group_for_4.iloc[[-1]].copy()

    output_lines.append(f"Training months for 4-parameter model: {len(train_4)}")
    output_lines.append(
        "Last month features (4 params): "
        f"Feedstock={format_number(test_4.iloc[0]['Feedstock Price'])}, "
        f"Conversion={format_number(test_4.iloc[0]['Conversion Price'])}, "
        f"Transport={format_number(test_4.iloc[0]['Transport Price'])}, "
        f"Previous Final Price={format_number(test_4.iloc[0]['Previous Final Price'])}"
    )

    predicted_4, model_4 = train_and_predict(train_4, test_4, FEATURE_COLUMNS_4)
    errors_4.append(abs(predicted_4 - actual_final_price))

    output_lines.append(
        format_comparison("Sklearn LinearRegression (4 params)", predicted_4, actual_final_price)
    )
    output_lines.append(
        "Coefficients (4 params): "
        + format_coefficients(model_4, FEATURE_COLUMNS_4)
    )
    output_lines.append("")

if errors_3:
    output_lines.append(
        f"Overall MAE for Sklearn LinearRegression (3 params): {format_number(sum(errors_3) / len(errors_3))}"
    )

if errors_4:
    output_lines.append(
        f"Overall MAE for Sklearn LinearRegression (4 params): {format_number(sum(errors_4) / len(errors_4))}"
    )

output_text = "\n".join(output_lines)

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write(output_text)
