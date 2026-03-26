import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

df = pd.read_excel('Project_2_Data_Validated.xlsx')

df['Year'] = pd.to_datetime(df['Final Price Month']).dt.year
df['Month'] = pd.to_datetime(df['Final Price Month']).dt.month

# definim coloanele categorice si cele numerice
cat_cols = ['Material Type', 'Material Sub Type', 'Plant', 'Supplier', 'BU', 'Material Status', 'SP Low']
num_cols = ['Final Price', 'Feedstock Price', 'Conversion Price', 'Transport Price', 'Grammage', 'Year', 'Month']

# transformam textul in numere
le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col].astype(str))

# scalam numerele pentru a avea aceeasi importanta
scaler = StandardScaler()
df[num_cols] = scaler.fit_transform(df[num_cols])

# pastram doar coloanele necesare pentru model
df_model = df[cat_cols + num_cols].copy()

# salvam rezultatul pentru faza finala
df_model.to_excel('Project_2_Data_Ready.xlsx', index=False)

print(f"date pregatite cu succes: {len(df_model)} randuri")
print(f"coloane incluse: {list(df_model.columns)}")