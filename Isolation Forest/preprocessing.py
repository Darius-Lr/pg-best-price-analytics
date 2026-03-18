import pandas as pd
import warnings

file_path = '../Project 2 Data.xlsx'
df = pd.read_excel(file_path)

warnings.filterwarnings('ignore', category=RuntimeWarning)

# eliminam randurile cu pret zero
df = df[df['Final Price'] > 0].copy()

# scoatem coloana incoterm (prea multe lipsuri)
df.drop(columns=['Incoterm'], inplace=True)

# definim coloanele pentru "combinatie"
comb = ['Plant', 'Supplier', 'Material Sub Type']

# calculam mediana globala pentru gramaj ca backup
global_grammage_median = df['Grammage'].median()

# functia pentru completare (foloseste mediana grupului sau fallback)
def fill_group_median(group, fallback_value):
    group_median = group.median()
    if pd.isna(group_median):
        return group.fillna(fallback_value)
    return group.fillna(group_median)

# completam transportul per combinatie (fallback la 0)
df['Transport Price'] = df.groupby(comb)['Transport Price'].transform(lambda x: fill_group_median(x, 0))

# completam gramajul per combinatie (fallback la mediana globala)
df['Grammage'] = df.groupby(comb)['Grammage'].transform(lambda x: fill_group_median(x, global_grammage_median))

# salvam datele curatate
output_path = 'Project_2_Data_Cleaned.xlsx'
df.to_excel(output_path, index=False)

print(f"fisier salvat cu succes: {output_path}")
print(f"randuri finale: {len(df)}")