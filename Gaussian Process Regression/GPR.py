import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from scipy.stats import norm

# incarcam datele
df = pd.read_excel('Project_2_Data_Features.xlsx')
df['Final Price Month'] = pd.to_datetime(df['Final Price Month'])

print("--- predictie pret viitor (selectie pe 4 criterii) ---")

# selectie plant
available_plants = sorted(df['Plant'].unique())
print(f"\nplant-uri: {', '.join(available_plants)}")
plant_input = input("alegeti plant: ")

# selectie material type
df_p = df[df['Plant'] == plant_input]
available_types = sorted(df_p['Material Type'].unique())
print(f"\ntipuri material in {plant_input}: {', '.join(available_types)}")
type_input = input("alegeti material type: ")

# selectie supplier
df_pt = df_p[df_p['Material Type'] == type_input]
available_suppliers = sorted(df_pt['Supplier'].unique())
print(f"\nfurnizori pentru {type_input}: {', '.join(available_suppliers)}")
supplier_input = input("alegeti supplier: ")

# selectie material sub type
df_pts = df_pt[df_pt['Supplier'] == supplier_input]
available_subtypes = sorted(df_pts['Material Sub Type'].unique())
print(f"\nsub-tipuri disponibile: {', '.join(available_subtypes)}")
subtype_input = input("alegeti material sub type: ")

# subset final (combinatie de 4)
df_sub = df_pts[df_pts['Material Sub Type'] == subtype_input].copy()

if len(df_sub) < 5:
    print("\neroare: date insuficiente pentru aceasta combinatie.")
else:
    df_sub = df_sub.sort_values('Final Price Month')
    df_sub['Month_Index'] = (df_sub['Final Price Month'] - df_sub['Final Price Month'].min()).dt.days // 30

    X = df_sub[['Month_Index', 'Price_Lag_1', 'Feedstock_Lag_1']].values
    y = df_sub['Final Price'].values.reshape(-1, 1)

    # scalare si model
    scaler_X, scaler_y = StandardScaler(), StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y)

    kernel = C(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=20)
    gpr.fit(X_scaled, y_scaled.ravel())

    # predictie
    last_row = df_sub.iloc[-1]
    X_next = np.array([[last_row['Month_Index'] + 1, last_row['Final Price'], last_row['Feedstock Price']]])
    X_next_scaled = scaler_X.transform(X_next)

    y_pred_scaled, sigma_scaled = gpr.predict(X_next_scaled, return_std=True)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1))[0][0]
    sigma = sigma_scaled[0] * scaler_y.scale_[0]

    # plotare rezultate
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # plot 1: evolutie
    ax1.scatter(df_sub['Final Price Month'], df_sub['Final Price'], color='blue', label='istoric')
    next_date = last_row['Final Price Month'] + pd.DateOffset(months=1)
    ax1.errorbar(next_date, y_pred, yerr=1 * sigma, fmt='ro', capsize=8, label='predictie (68% CI)')
    ax1.set_title(f"prognoza: {plant_input} | {subtype_input}")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # plot 2: distributia gausiana
    x_axis = np.linspace(y_pred - 4 * sigma, y_pred + 4 * sigma, 200)
    y_axis = norm.pdf(x_axis, y_pred, sigma)
    ax2.plot(x_axis, y_axis, 'r-', lw=2)
    ax2.fill_between(x_axis, y_axis, where=(x_axis >= y_pred - 1 * sigma) & (x_axis <= y_pred + 1 * sigma),
                     color='red', alpha=0.3, label='68% probabilitate')
    ax2.axvline(y_pred, color='darkred', linestyle='--', label=f'media: {y_pred:.2f}')
    ax2.set_title(f"densitate probabilitate (std: {sigma:.2f})")
    ax2.set_xlabel("pret")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()