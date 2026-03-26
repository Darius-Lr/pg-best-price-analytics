import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge

try:
    from xgboost import XGBRegressor
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Pachetul 'xgboost' nu este instalat. Ruleaza `pip install xgboost` si apoi incearca din nou."
    ) from exc


RIDGE_ALPHA = 1.0
LASSO_ALPHA = 1.0
LASSO_MAX_ITER = 10000
XGB_N_ESTIMATORS = 200
XGB_LEARNING_RATE = 0.05
XGB_MAX_DEPTH = 3
XGB_SUBSAMPLE = 1.0
XGB_COLSAMPLE_BYTREE = 1.0
XGB_RANDOM_STATE = 42
OUTLIER_MULTIPLIER = 1.5
MIN_ROWS_FOR_OUTLIER_DETECTION = 4
GROUP_COLUMNS = [
    "Material Type",
    "Material Sub Type",
    "Material Description",
    "Plant",
    "Supplier",
]
PRICE_COLUMNS = ["Final Price", "Feedstock Price", "Conversion Price", "Transport Price"]
FEATURE_COLUMNS = ["Feedstock Price", "Conversion Price", "Transport Price"]
DATE_COLUMN = "Final Price Month"

MODEL_OPTIONS = {
    "linear": "Linear Regression",
    "ridge": "Ridge",
    "lasso": "Lasso",
    "xgboost": "XGBoost",
}

MODEL_SELECTOR_LABELS = {
    "linear": "Linear Regression",
    "ridge": "Ridge (cea mai buna din istoricul testelor)",
    "lasso": "Lasso",
    "xgboost": "XGBoost",
}

MODEL_EXPLANATIONS = {
    "linear": (
        "Alege Linear Regression cand valorile evolueaza relativ constant; "
        "evit-o daca apar abateri mari sau tipare neregulate."
    ),
    "ridge": (
        "Alege Ridge cand coloanele sunt apropiate sau corelate; "
        "evit-o daca vrei sa elimini influentele mai putin utile."
    ),
    "lasso": (
        "Alege Lasso cand doar cateva coloane par importante; "
        "evit-o daca vrei sa pastrezi toata informatia disponibila."
    ),
    "xgboost": (
        "Alege XGBoost cand baza are tipare complexe si variatii multe; "
        "evit-o daca ai putine date curate si uniforme."
    ),
}


def build_model(model_key):
    if model_key == "linear":
        return LinearRegression()
    if model_key == "ridge":
        return Ridge(alpha=RIDGE_ALPHA)
    if model_key == "lasso":
        return Lasso(alpha=LASSO_ALPHA, max_iter=LASSO_MAX_ITER)
    if model_key == "xgboost":
        return XGBRegressor(
            objective="reg:squarederror",
            n_estimators=XGB_N_ESTIMATORS,
            learning_rate=XGB_LEARNING_RATE,
            max_depth=XGB_MAX_DEPTH,
            subsample=XGB_SUBSAMPLE,
            colsample_bytree=XGB_COLSAMPLE_BYTREE,
            random_state=XGB_RANDOM_STATE,
            n_jobs=1,
            verbosity=0,
        )
    raise ValueError(f"Model necunoscut: {model_key}")


def required_columns():
    return GROUP_COLUMNS + [DATE_COLUMN] + PRICE_COLUMNS


def validate_dataframe(df):
    missing_columns = [column for column in required_columns() if column not in df.columns]
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Fisierul Excel nu contine coloanele necesare: {missing_text}")


def detect_final_price_outliers(train_group):
    if len(train_group) < MIN_ROWS_FOR_OUTLIER_DETECTION:
        return train_group.copy(), train_group.iloc[0:0].copy(), None, None

    q1 = train_group["Final Price"].quantile(0.25)
    q3 = train_group["Final Price"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - OUTLIER_MULTIPLIER * iqr
    upper_bound = q3 + OUTLIER_MULTIPLIER * iqr

    is_kept = train_group["Final Price"].between(lower_bound, upper_bound, inclusive="both")
    cleaned_group = train_group[is_kept].copy()
    removed_group = train_group[~is_kept].copy()

    if len(cleaned_group) < 2:
        return train_group.copy(), train_group.iloc[0:0].copy(), lower_bound, upper_bound

    return cleaned_group, removed_group, lower_bound, upper_bound


def format_removed_rows(removed_group):
    parts = []

    for _, row in removed_group.iterrows():
        parts.append(
            f"{row[DATE_COLUMN].date()}={float(row['Final Price']):.2f}"
        )

    return "; ".join(parts)


def load_excel(file_path):
    df = pd.read_excel(file_path)
    validate_dataframe(df)
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    return df


def build_prediction_table_from_dataframe(df, model_key, months_back=None, ignore_garbage=False):
    if months_back is not None and months_back < 2:
        raise ValueError("Numarul de luni trebuie sa fie cel putin 2.")

    results = []

    for key, group in df.groupby(GROUP_COLUMNS, sort=False):
        group = group.sort_values(DATE_COLUMN).copy()
        group[PRICE_COLUMNS] = group[PRICE_COLUMNS].fillna(0)

        result_row = {column: value for column, value in zip(GROUP_COLUMNS, key)}
        result_row["Status"] = "OK"
        result_row["Model"] = MODEL_OPTIONS[model_key]

        minimum_required = 2 if months_back is None else months_back + 1
        if len(group) < minimum_required:
            result_row["Status"] = (
                f"Date insuficiente: trebuie cel putin {minimum_required} luni, exista {len(group)}"
            )
            results.append(result_row)
            continue

        if months_back is None:
            train_group_raw = group.iloc[:-1].copy()
            test_group = group.iloc[[-1]].copy()
            requested_history = "all"
        else:
            comparison_group = group.tail(months_back + 1).copy()
            train_group_raw = comparison_group.iloc[:-1].copy()
            test_group = comparison_group.iloc[[-1]].copy()
            requested_history = months_back

        cleaned_train_group = train_group_raw
        removed_group = train_group_raw.iloc[0:0].copy()
        lower_bound = None
        upper_bound = None

        if ignore_garbage:
            cleaned_train_group, removed_group, lower_bound, upper_bound = detect_final_price_outliers(
                train_group_raw
            )

        model = build_model(model_key)
        model.fit(cleaned_train_group[FEATURE_COLUMNS], cleaned_train_group["Final Price"])

        predicted_value = float(model.predict(test_group[FEATURE_COLUMNS])[0])
        actual_value = float(test_group.iloc[0]["Final Price"])
        difference = predicted_value - actual_value
        abs_difference = abs(difference)
        percent_error = None

        if actual_value != 0:
            percent_error = abs_difference / abs(actual_value) * 100

        result_row["Months Requested"] = requested_history
        result_row["Training Months Before Cleaning"] = len(train_group_raw)
        result_row["Training Months Used"] = len(cleaned_train_group)
        result_row["Garbage Removed"] = len(removed_group)
        result_row["Removed Rows"] = format_removed_rows(removed_group)
        result_row["Outlier Lower Bound"] = lower_bound
        result_row["Outlier Upper Bound"] = upper_bound
        result_row["Last Actual Month"] = test_group.iloc[0][DATE_COLUMN]
        result_row["Feedstock Price"] = float(test_group.iloc[0]["Feedstock Price"])
        result_row["Conversion Price"] = float(test_group.iloc[0]["Conversion Price"])
        result_row["Transport Price"] = float(test_group.iloc[0]["Transport Price"])
        result_row["Actual Final Price"] = actual_value
        result_row["Predicted Final Price"] = predicted_value
        result_row["Difference"] = difference
        result_row["Abs Difference"] = abs_difference
        result_row["Percent Error"] = percent_error
        results.append(result_row)

    return pd.DataFrame(results)


def build_prediction_table(file_path, model_key, months_back=None, ignore_garbage=False):
    df = load_excel(file_path)
    return build_prediction_table_from_dataframe(
        df=df,
        model_key=model_key,
        months_back=months_back,
        ignore_garbage=ignore_garbage,
    )
