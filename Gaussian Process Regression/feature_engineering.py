import pandas as pd

df = pd.read_excel('../Isolation Forest/Project_2_Data_Validated.xlsx')

# ne asiguram ca data este in format corect si sortam cronologic
df['Final Price Month'] = pd.to_datetime(df['Final Price Month'])
df = df.sort_values(by=['Plant', 'Supplier', 'Material Sub Type', 'Final Price Month'])

# definim combinatia noastra
comb = ['Plant', 'Supplier', 'Material Sub Type']

# cream lag-ul de 1 luna pentru pretul final
df['Price_Lag_1'] = df.groupby(comb)['Final Price'].shift(1)

# cream lag-ul de 1 luna pentru feedstock
df['Feedstock_Lag_1'] = df.groupby(comb)['Feedstock Price'].shift(1)

# cream o medie pe ultimele 3 luni pentru a vedea trendul
df['Price_Rolling_Mean_3'] = df.groupby(comb)['Final Price'].transform(lambda x: x.rolling(window=3).mean().shift(1))

# eliminam randurile care au acum valori goale (primele luni din fiecare grup nu au istoric)
df_features = df.dropna(subset=['Price_Lag_1', 'Feedstock_Lag_1']).copy()

output_path = 'Project_2_Data_Features.xlsx'
df_features.to_excel(output_path, index=False)

print(f"Feature engineering gata. Randuri ramase: {len(df_features)}")
print(f"Coloane noi create: Price_Lag_1, Feedstock_Lag_1, Price_Rolling_Mean_3")