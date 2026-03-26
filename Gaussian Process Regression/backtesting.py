import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import StandardScaler
import warnings
from sklearn.exceptions import ConvergenceWarning

# ignoram avertizarile
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

df = pd.read_excel('Project_2_Data_Features.xlsx')
df['Final Price Month'] = pd.to_datetime(df['Final Price Month'])

results = []
combinations = df.groupby(['Plant', 'Supplier', 'Material Sub Type'])

print(f"incepe validarea pentru {len(combinations)} combinatii...")

for name, group in combinations:
    if len(group) < 6:  # dam skip la combinatii cu date insuficiente
        continue

    # sortare si pregatire index
    group = group.sort_values('Final Price Month')
    group['Month_Index'] = (group['Final Price Month'] - group['Final Price Month'].min()).dt.days // 30

    # split: train (totul minus ultima), test (doar ultima)
    train_df = group.iloc[:-1].copy()
    test_row = group.iloc[-1].copy()

    # date antrenare
    X_train = train_df[['Month_Index', 'Price_Lag_1', 'Feedstock_Lag_1']].values
    y_train = train_df['Final Price'].values.reshape(-1, 1)

    # scalare
    scaler_X, scaler_y = StandardScaler(), StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    y_train_scaled = scaler_y.fit_transform(y_train)

    # model gpr
    kernel = C(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)

    try:
        gpr.fit(X_train_scaled, y_train_scaled.ravel())

        # predictie pentru luna ascunsa
        X_test = np.array([[test_row['Month_Index'], test_row['Price_Lag_1'], test_row['Feedstock_Lag_1']]])
        X_test_scaled = scaler_X.transform(X_test)

        y_pred_scaled, sigma_scaled = gpr.predict(X_test_scaled, return_std=True)
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))[0][0]
        sigma = sigma_scaled[0] * scaler_y.scale_[0]

        # calcul precizie
        actual = test_row['Final Price']
        error_pct = abs(actual - y_pred) / actual * 100
        hit_68 = 1 if (actual >= y_pred - sigma and actual <= y_pred + sigma) else 0

        results.append({
            'Plant': name[0], 'Supplier': name[1], 'Material': name[2],
            'Actual': actual, 'Predicted': y_pred, 'Error_%': error_pct,
            'In_Interval_68': hit_68, 'Sigma': sigma
        })
    except:
        continue

# generare raport final
res_df = pd.DataFrame(results)
accuracy_total = 100 - res_df['Error_%'].mean()
hit_rate_68 = res_df['In_Interval_68'].mean() * 100

print(f"\n--- raport precizie model ---")
print(f"numar combinatii testate: {len(res_df)}")
print(f"precizie medie (point accuracy): {accuracy_total:.2f}%")
print(f"rata de succes interval 68% (hit rate): {hit_rate_68:.2f}%")

# salvare pentru analiza detaliata
res_df.to_excel('GPR_Validation_Results.xlsx', index=False)