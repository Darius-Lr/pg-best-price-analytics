import pandas as pd
import numpy as np
import warnings
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# folosim direct fisierul validat, fara lags
df = pd.read_excel('../Isolation Forest/Project_2_Data_Validated.xlsx')
df['Final Price Month'] = pd.to_datetime(df['Final Price Month'])

results = []
combinations = list(df.groupby(['Plant', 'Supplier', 'Material Sub Type']))
total = len(combinations)

print(f"incepe validarea baseline pentru {total} combinatii...")

for i, (name, group) in enumerate(combinations):
    if i % 50 == 0:
        print(f"progres: {i}/{total}...")

    if len(group) < 6:
        continue

    # sortare si index de timp
    group = group.sort_values('Final Price Month')
    group['Month_Index'] = (group['Final Price Month'] - group['Final Price Month'].min()).dt.days // 30

    # split train/test
    train_df = group.iloc[:-1].copy()
    test_row = group.iloc[-1].copy()

    # folosim DOAR indexul timpului ca feature
    X_train = train_df[['Month_Index']].values
    y_train = train_df['Final Price'].values.reshape(-1, 1)

    scaler_X, scaler_y = StandardScaler(), StandardScaler()
    X_train_scaled = scaler_X.fit_transform(X_train)
    y_train_scaled = scaler_y.fit_transform(y_train)

    kernel = C(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5)

    try:
        gpr.fit(X_train_scaled, y_train_scaled.ravel())

        # predictie doar pe baza indexului lunii viitoare
        X_test = np.array([[test_row['Month_Index']]])
        X_test_scaled = scaler_X.transform(X_test)

        y_pred_scaled, sigma_scaled = gpr.predict(X_test_scaled, return_std=True)
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))[0][0]
        sigma = sigma_scaled[0] * scaler_y.scale_[0]

        actual = test_row['Final Price']
        error_pct = abs(actual - y_pred) / actual * 100
        hit_68 = 1 if (actual >= y_pred - sigma and actual <= y_pred + sigma) else 0

        results.append({
            'Actual': actual, 'Predicted': y_pred, 'Error_%': error_pct, 'In_68': hit_68
        })
    except:
        continue

res_df = pd.DataFrame(results)
print(f"\n--- rezultate baseline (fara features) ---")
print(f"precizie medie: {100 - res_df['Error_%'].mean():.2f}%")
print(f"hit rate (68% interval): {res_df['In_68'].mean() * 100:.2f}%")