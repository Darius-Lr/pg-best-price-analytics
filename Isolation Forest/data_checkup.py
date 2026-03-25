import pandas as pd

file_path = 'Project_2_Data_Cleaned.xlsx'
df = pd.read_excel(file_path)

# calculam suma teoretica
df['Calculated_Sum'] = df['Feedstock Price'] + df['Conversion Price'] + df['Transport Price']

# calculam diferenta absoluta si procentuala
df['Price_Delta'] = df['Final Price'] - df['Calculated_Sum']
df['Delta_Percentage'] = (df['Price_Delta'].abs() / df['Final Price']) * 100

# setam pragul de eroare
error_threshold = 3.0

# filtram doar datele corecte matematic
df_validated = df[df['Delta_Percentage'] <= error_threshold].copy()

# filtram anomaliile matematice pentru afisare
anomalies_math = df[df['Delta_Percentage'] > error_threshold]

print(f"total randuri analizate: {len(df)}")
print(f"randuri valide (salvate): {len(df_validated)}")
print(f"randuri cu erori matematice (eliminate): {len(anomalies_math)}")

if not anomalies_math.empty:
    print("\ntop discrepante gasite:")
    print(anomalies_math[['Material Description', 'Final Price', 'Calculated_Sum', 'Price_Delta', 'Delta_Percentage']].head())

df_validated.to_excel('Project_2_Data_Validated.xlsx', index=False)

print("\nfisier salvat cu succes fara erori matematice.")