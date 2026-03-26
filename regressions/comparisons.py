import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from xgboost import XGBRegressor


DATA_FILE = "Project 2 Data.xlsx"
OUTPUT_FILE = "outputComparisons.txt"
RIDGE_ALPHA = 1.0
LASSO_ALPHA = 1.0
LASSO_MAX_ITER = 10000
XGB_N_ESTIMATORS = 200
XGB_LEARNING_RATE = 0.05
XGB_MAX_DEPTH = 3
XGB_SUBSAMPLE = 1.0
XGB_COLSAMPLE_BYTREE = 1.0
XGB_RANDOM_STATE = 42
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


def format_comparison(model_name, predicted, actual):
    difference = predicted - actual
    abs_difference = abs(difference)

    if actual != 0:
        percent_error = abs_difference / abs(actual) * 100
        return (
            f"{model_name}: Predicted={format_number(predicted)}, Actual={format_number(actual)}, "
            f"Difference={format_number(difference)}, Abs Difference={format_number(abs_difference)}, "
            f"Percent Error={format_number(percent_error)}%"
        )

    return (
        f"{model_name}: Predicted={format_number(predicted)}, Actual={format_number(actual)}, "
        f"Difference={format_number(difference)}, Abs Difference={format_number(abs_difference)}, "
        "Percent Error=undefined (actual value is 0)"
    )


def format_coefficients(model, feature_names):
    parts = [f"Intercept={format_number(model.intercept_)}"]

    for feature_name, coefficient in zip(feature_names, model.coef_):
        parts.append(f"{feature_name}={format_number(coefficient)}")

    return ", ".join(parts)


def format_feature_importances(model, feature_names):
    parts = []

    for feature_name, importance in zip(feature_names, model.feature_importances_):
        parts.append(f"{feature_name}={format_number(importance)}")

    return ", ".join(parts)


def build_models():
    return {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=RIDGE_ALPHA),
        "Lasso": Lasso(alpha=LASSO_ALPHA, max_iter=LASSO_MAX_ITER),
        "XGBoost": XGBRegressor(
            objective="reg:squarederror",
            n_estimators=XGB_N_ESTIMATORS,
            learning_rate=XGB_LEARNING_RATE,
            max_depth=XGB_MAX_DEPTH,
            subsample=XGB_SUBSAMPLE,
            colsample_bytree=XGB_COLSAMPLE_BYTREE,
            random_state=XGB_RANDOM_STATE,
            n_jobs=1,
            verbosity=0,
        ),
    }


df = pd.read_excel(DATA_FILE)
df["Final Price Month"] = pd.to_datetime(df["Final Price Month"])

models = build_models()
output_lines = [
    f"Features used: {', '.join(FEATURE_COLUMNS)}",
    f"Ridge alpha used: {RIDGE_ALPHA}",
    f"Lasso alpha used: {LASSO_ALPHA}",
    f"Lasso max_iter used: {LASSO_MAX_ITER}",
    f"XGBoost n_estimators used: {XGB_N_ESTIMATORS}",
    f"XGBoost learning_rate used: {XGB_LEARNING_RATE}",
    f"XGBoost max_depth used: {XGB_MAX_DEPTH}",
    f"XGBoost subsample used: {XGB_SUBSAMPLE}",
    f"XGBoost colsample_bytree used: {XGB_COLSAMPLE_BYTREE}",
    f"XGBoost random_state used: {XGB_RANDOM_STATE}",
    "",
]
model_errors = {model_name: [] for model_name in models}
model_wins = {model_name: 0 for model_name in models}

for key, group in df.groupby(GROUP_COLUMNS, sort=False):
    group = group.sort_values("Final Price Month").copy()
    group[PRICE_COLUMNS] = group[PRICE_COLUMNS].fillna(0)

    output_lines.append(f"Group: {key}")

    if len(group) < 2:
        output_lines.append(
            "Nu exista suficiente date pentru comparatie. Sunt necesare cel putin 2 luni."
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

    group_results = []

    for model_name, model in build_models().items():
        model.fit(train_group[FEATURE_COLUMNS], train_group["Final Price"])
        predicted_price = float(model.predict(test_group[FEATURE_COLUMNS])[0])
        abs_error = abs(predicted_price - actual_final_price)
        model_errors[model_name].append(abs_error)
        group_results.append((model_name, predicted_price, abs_error, model))

        output_lines.append(
            format_comparison(model_name, predicted_price, actual_final_price)
        )
        if model_name == "XGBoost":
            output_lines.append(
                f"Feature importances {model_name}: "
                + format_feature_importances(model, FEATURE_COLUMNS)
            )
        else:
            output_lines.append(
                f"Coefficients {model_name}: " + format_coefficients(model, FEATURE_COLUMNS)
            )

    best_model_name, _, best_abs_error, _ = min(group_results, key=lambda item: item[2])
    model_wins[best_model_name] += 1
    output_lines.append(
        f"Best model for this group: {best_model_name} with Abs Difference={format_number(best_abs_error)}"
    )
    output_lines.append("")

output_lines.append("Overall summary:")

best_overall_model = None
best_overall_mae = None

for model_name, errors in model_errors.items():
    if not errors:
        continue

    mae = sum(errors) / len(errors)
    output_lines.append(
        f"{model_name}: Overall MAE={format_number(mae)}, Wins={model_wins[model_name]}"
    )

    if best_overall_mae is None or mae < best_overall_mae:
        best_overall_mae = mae
        best_overall_model = model_name

if best_overall_model is not None:
    output_lines.append(
        f"Best overall model by MAE: {best_overall_model} with MAE={format_number(best_overall_mae)}"
    )

output_text = "\n".join(output_lines)

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write(output_text)
