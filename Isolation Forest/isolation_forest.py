import pandas as pd
from sklearn.ensemble import IsolationForest

df_ready = pd.read_excel('Project_2_Data_Ready.xlsx')
df_orig = pd.read_excel('Project_2_Data_Validated.xlsx')

model = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)

# antrenam si prezicem (-1 anomalie, 1 normal)
df_ready['anomaly'] = model.fit_predict(df_ready)

# calculam scorul de anomalie
df_ready['anomaly_score'] = model.decision_function(df_ready.drop(columns=['anomaly']))


df_orig['anomaly'] = df_ready['anomaly']
df_orig['anomaly_score'] = df_ready['anomaly_score']

# cream un top al combinatiilor riscante
comb = ['Plant', 'Supplier', 'Material Sub Type']
risk_summary = df_orig[df_orig['anomaly'] == -1].groupby(comb).size().reset_index(name='anomaly_count')
risk_summary = risk_summary.sort_values(by='anomaly_count', ascending=False)

df_orig.to_excel('Project_2_Final_Anomalies.xlsx', index=False)
risk_summary.to_excel('Project_2_Risk_Report.xlsx', index=False)

print(f"Detectie finalizata. Total anomalii gasite: {len(df_orig[df_orig['anomaly'] == -1])}")
print("\nTop 5 combinatii cu risc ridicat:")
print(risk_summary.head())