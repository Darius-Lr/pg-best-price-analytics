import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#CURATAREA DATELOR

# Citesc fisierul Excel si il salvez in variabila df
df = pd.read_excel('Project 2 Data.xlsx')

# Elimin randurile care nu contin date (sunt goale) din urmatoarele coloane
df = df.dropna(subset=['Feedstock Price', 'Conversion Price', 'Transport Price', 'Grammage'])

# Elimin randurile duplicate ca sa nu calculez aceleasi date de doua ori
# inplace=True => modific direct tabelul 'df' fara sa mai creez o variabila noua
df.drop_duplicates(inplace=True)

# Urmeaza sa verific daca Final Price este calculat corect
# Creez o coloana noua numita Calculated Price adunand cele 3 costuri
df['Calculated Price'] = df['Feedstock Price'] + df['Conversion Price'] + df['Transport Price']

# Calculez diferenta dintre pretul final din tabel si cel calculat de mai sus
df['Price Difference'] = df['Final Price'] - df['Calculated Price']

# Creez o coloana cu True sau False, True inseamna ca exista o diferenta
df['Price is different'] = df['Price Difference'] != 0

# Afisez in consola cateva statistici  despre diferente (media, minim, maxim etc.)
print(df['Price Difference'].describe().round(4))

# Calculez eficienta: impart costul la gramaj pentru a afla pretul per gram
df['Efficiency Price'] = df['Calculated Price'] / df['Grammage']

# Definesc categoriile dupa care voi grupa datele deoarece,nu vreau sa amestec materiale diferite intre ele
group = ['Material Type', 'Material Sub Type', 'Material Description']

# ---------------------------------------------------------------
# SCENARIUL 1(What if 1): Luna istorica cu cel mai bun pret total


# gasesc numarul randului cu cel mai mic pret si ma folosesc de df.loc[] pentru a extrage randul intreg cu toate datele sale
best_calendaristic_price = df.loc[df.groupby(group)['Calculated Price'].idxmin()]

# Filtrez rezultatele ca sa pastrez doar materialele care sunt active in prezent
best_calendaristic_price = best_calendaristic_price[best_calendaristic_price['Material Status'] == 'active']

# Salvez data acestui pret bun intr-o coloana noua mai intuitiva, numita Best Month
best_calendaristic_price['Best Month'] = best_calendaristic_price['Final Price Month']

# Sterg vechea coloana de data ,axis=1 inseamna ca stergem o coloana, nu un rand
best_calendaristic_price = best_calendaristic_price.drop('Final Price Month', axis=1)

# Salvez tabelul rezultat intr-un fisier Excel nou pe calculator
best_calendaristic_price.to_excel('Best_Calendaristic_price.xlsx', index=False)

# Transform data intr-un format text
best_calendaristic_price['Month_Abbrev'] = pd.to_datetime(best_calendaristic_price['Best Month']).dt.strftime('%b')

# Setez ordinea corecta a lunilor pentru a aparea pe grafic din Ianuarie pana in Decembrie
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Numar de cate ori apare fiecare luna si le asezam in ordinea definita mai sus
month_counts = best_calendaristic_price['Month_Abbrev'].value_counts().reindex(month_order, fill_value=0)

# Creez graficul si il afisez
plt.figure(figsize=(20, 10))
month_counts.plot(kind='bar', color='red')
plt.title('Count of Best Month for Lowest Price')
plt.xlabel('Month')
plt.ylabel('Count')
plt.xticks(rotation=0)  # Textul lunilor sa stea drept (nerotit)
plt.show()

#------------------------------------------------------------------------------
# SCENARIUL 2(What if 2): Luna istorica cu cea mai buna eficienta (pret/cantitate)

# Acelasi proces ca la Scenariul 1, doar ca acum caut minimul pe coloana Efficiency Price
best_calendaristic_efficiency = df.loc[df.groupby(group)['Efficiency Price'].idxmin()]
best_calendaristic_efficiency = best_calendaristic_efficiency[
    best_calendaristic_efficiency['Material Status'] == 'active']

best_calendaristic_efficiency['Best Month'] = best_calendaristic_efficiency['Final Price Month']
best_calendaristic_efficiency = best_calendaristic_efficiency.drop('Final Price Month', axis=1)
best_calendaristic_efficiency.to_excel('Best_Calendaristic_Efficiency.xlsx', index=False)

# Creez graficul pentru scenariul 2
best_calendaristic_efficiency['Month_Abbrev'] = pd.to_datetime(best_calendaristic_efficiency['Best Month']).dt.strftime(
    '%b')
month_counts = best_calendaristic_efficiency['Month_Abbrev'].value_counts().reindex(month_order, fill_value=0)
plt.figure(figsize=(20, 10))
month_counts.plot(kind='bar', color='green')
plt.title('Count of Best Month for the best Price/Quantity')
plt.xlabel('Month')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.show()

# --------------------------------------------------------------------------
# SCENARIUL 3(what if 3): Combinatii Optime pentru Pret (luna cu cel mai bun feedstock + luna cu cel mai bun conversion price+
# luna cu cel mai bun transport price)


# Adaug Furnizorul (Supplier) si Fabrica (Plant) pentru ca nu pot amesteca preturi de la fabrici diferite
group1 = ['Material Type', 'Material Sub Type', 'Material Description', 'Supplier', 'Plant']

# Gasesc luna istorica cu cel mai bun pret DOAR pentru materia prima (Feedstock Price)
best_feed_idx = df.groupby(group1)['Feedstock Price'].idxmin()
# Folosesc 'Final Price Month' in loc de 'Feedstock Price Month' pentru a evita eroarea
best_feed = df.loc[best_feed_idx, group1 + ['Feedstock Price', 'Final Price Month']]
best_feed = best_feed.rename(columns={'Final Price Month': 'Best Feedstock Month'})

# Gasesc luna istorica cu cel mai bun pret DOAR pentru Conversion Price
best_conv_idx = df.groupby(group1)['Conversion Price'].idxmin()
best_conv = df.loc[best_conv_idx, group1 + ['Conversion Price', 'Final Price Month']]
best_conv = best_conv.rename(columns={'Final Price Month': 'Best Conversion Month'})

# Gasesc luna istorica cu cel mai bun pret DOAR pentru Transport
best_trans_idx = df.groupby(group1)['Transport Price'].idxmin()
best_trans = df.loc[best_trans_idx, group1 + ['Transport Price', 'Final Price Month']]
best_trans = best_trans.rename(columns={'Final Price Month': 'Best Transport Month'})

# Concatenez la loc aceste 3 tabele intr-un singur tabel
theoretical_best = pd.merge(best_feed, best_conv, on=group1)
theoretical_best = pd.merge(theoretical_best, best_trans, on=group1)

# Calculez pretul in acest scenariu adunand cele mai bune componente
theoretical_best['Theoretical Best Final Price'] = (
        theoretical_best['Feedstock Price'] +
        theoretical_best['Conversion Price'] +
        theoretical_best['Transport Price']
)

# Aduc inapoi si gramajul pentru a calcula eficienta pe acest scenariu
grammage_df = df[group1 + ['Grammage']].drop_duplicates()
theoretical_best = pd.merge(theoretical_best, grammage_df, on=group1, how='left')
theoretical_best['Theoretical Efficiency Price'] = theoretical_best['Theoretical Best Final Price'] / theoretical_best[
    'Grammage']

# Salvez rezultatul intr-un Excel
theoretical_best.to_excel('Theoretical_Best_Combinations_S3.xlsx', index=False)



#-----------------------------------------------------------
# SCENARIUL 4(what if 4): Combinatii Optime pentru Eficienta


# Impart fiecare cost individual la gramaj pentru a vedea eficienta proprie
df['Feedstock Efficiency'] = df['Feedstock Price'] / df['Grammage']
df['Conversion Efficiency'] = df['Conversion Price'] / df['Grammage']
df['Transport Efficiency'] = df['Transport Price'] / df['Grammage']

# Extrag cel mai bun moment istoric pentru eficienta materiei prime
best_feed_eff_idx = df.groupby(group1)['Feedstock Efficiency'].idxmin()
best_feed_eff = df.loc[best_feed_eff_idx, group1 + ['Feedstock Efficiency', 'Final Price Month']]
best_feed_eff = best_feed_eff.rename(columns={'Final Price Month': 'Best Feedstock Eff Month'})

# Extrag cel mai bun moment istoric pentru eficienta conversiei
best_conv_eff_idx = df.groupby(group1)['Conversion Efficiency'].idxmin()
best_conv_eff = df.loc[best_conv_eff_idx, group1 + ['Conversion Efficiency', 'Final Price Month']]
best_conv_eff = best_conv_eff.rename(columns={'Final Price Month': 'Best Conversion Eff Month'})

# Extrag cel mai bun moment istoric pentru eficienta transportului
best_trans_eff_idx = df.groupby(group1)['Transport Efficiency'].idxmin()
best_trans_eff = df.loc[best_trans_eff_idx, group1 + ['Transport Efficiency', 'Final Price Month']]
best_trans_eff = best_trans_eff.rename(columns={'Final Price Month': 'Best Transport Eff Month'})

# Concatenez din nou componentele intr-un tabel nou  pentru eficienta
theoretical_best_efficiency = pd.merge(best_feed_eff, best_conv_eff, on=group1)
theoretical_best_efficiency = pd.merge(theoretical_best_efficiency, best_trans_eff, on=group1)

# Calculez eficienta finala
theoretical_best_efficiency['Theoretical Best Efficiency Price'] = (
        theoretical_best_efficiency['Feedstock Efficiency'] +
        theoretical_best_efficiency['Conversion Efficiency'] +
        theoretical_best_efficiency['Transport Efficiency']
)

theoretical_best_efficiency.to_excel('Theoretical_Best_Efficiency_S4.xlsx', index=False)



# --------------------------------------
# COMPARATII INTRE SCENARII SI GRAFICE

# --------------S1 VS S3----------------
# Iau cea mai buna varianta rezultata din Scenariul 3
s3_best_overall = theoretical_best.loc[theoretical_best.groupby(group)['Theoretical Best Final Price'].idxmin()]

# Concatenez Scenariul 1 cu Scenariul 3  pentru a le compara
# suffixes ajuta ca programul sa nu se incurce in cazul in care avem coloane cu acelasi nume in ambele tabele
comparison_s1_s3 = pd.merge(
    best_calendaristic_price[group + ['Calculated Price']],
    s3_best_overall[group + ['Theoretical Best Final Price']],
    on=group, suffixes=('_S1', '_S3')
)

# Calculez diferenta in bani intre S1 si S3
comparison_s1_s3['Potential Savings ($)'] = comparison_s1_s3['Calculated Price'] - comparison_s1_s3[
    'Theoretical Best Final Price']
# Transform diferenta de bani in procentaj (%)
comparison_s1_s3['Savings (%)'] = (comparison_s1_s3['Potential Savings ($)'] / comparison_s1_s3[
    'Calculated Price']) * 100

# Creez un grafic pentru compararea scenariului 1 cu 3
plt.figure(figsize=(10, 6))
plt.hist(comparison_s1_s3['Savings (%)'].dropna(), bins=20, color='royalblue', edgecolor='black', alpha=0.7)
plt.title('Distribution of Potential Savings (%)\nWhat if 1 vs What if 3', fontsize=14)
plt.xlabel('Savings (%)', fontsize=12)
plt.ylabel('Frequency (Number of Materials)', fontsize=12)

plt.axvline(comparison_s1_s3['Savings (%)'].mean(), color='red', linestyle='dashed', linewidth=2,
            label=f"Mean: {comparison_s1_s3['Savings (%)'].mean():.2f}%")
plt.legend()
plt.tight_layout()  # Face loc automat textelor ca sa nu iasa din ecran
plt.show()

# --------------S2 VS S4----------------
s4_best_eff_overall = theoretical_best_efficiency.loc[
    theoretical_best_efficiency.groupby(group)['Theoretical Best Efficiency Price'].idxmin()]

comparison_s2_s4 = pd.merge(
    best_calendaristic_efficiency[group + ['Efficiency Price']],
    s4_best_eff_overall[group + ['Theoretical Best Efficiency Price']],
    on=group, suffixes=('_S2', '_S4')
)
comparison_s2_s4['Efficiency Potential Savings ($/Gram)'] = comparison_s2_s4['Efficiency Price'] - comparison_s2_s4[
    'Theoretical Best Efficiency Price']
comparison_s2_s4['Efficiency Savings (%)'] = (comparison_s2_s4['Efficiency Potential Savings ($/Gram)'] /
                                              comparison_s2_s4['Efficiency Price']) * 100

# Creez graficul pentru diferentele de eficienta
plt.figure(figsize=(10, 6))
plt.hist(comparison_s2_s4['Efficiency Savings (%)'].dropna(), bins=20, color='mediumorchid', edgecolor='black',
         alpha=0.7)
plt.title('Distribution of Potential Efficiency Savings (%)\nScenario 2 (Historic) vs Scenario 4 (Theoretical)',
          fontsize=14)
plt.xlabel('Efficiency Savings (%)', fontsize=12)
plt.ylabel('Frequency (Number of Materials)', fontsize=12)
plt.axvline(comparison_s2_s4['Efficiency Savings (%)'].mean(), color='red', linestyle='dashed', linewidth=2,
            label=f"Mean: {comparison_s2_s4['Efficiency Savings (%)'].mean():.2f}%")
plt.legend()
plt.tight_layout()
plt.show()



# ----------------------------------------------------
# Fuunctia pentru evolutia preturilor

def plot_price_evolution(df, material_type='Absorbent Core', material_sub_type='DT', material_desc='Description 22',
                         supplier='Supplier 4', plant='Plant 4'):
    # Filtrez datele ca sa raman doar cu materialul si furnizorul cerut
    filtered_df = df[(df['Material Type'] == material_type) &
                     (df['Material Sub Type'] == material_sub_type) &
                     (df['Material Description'] == material_desc) &
                     (df['Supplier'] == supplier) &
                     (df['Plant'] == plant)].copy()

    # Daca am filtrat si nu am gasit nimic, opresc functia ca sa evit eroarea
    if filtered_df.empty:
        print("No data found for the specified group.")
        return

    # Transform data in format de Calendar ca sa le pot aseza in ordine cronologica pe axa
    filtered_df['Sort_Date'] = pd.to_datetime(filtered_df['Final Price Month'])
    filtered_df = filtered_df.sort_values('Sort_Date')

    # Transformam data in text (ex: "Jan 2023")
    filtered_df['Month_Year'] = filtered_df['Sort_Date'].dt.strftime('%b %Y')

    # Incep noul grafic de evolutie
    plt.figure(figsize=(15, 7))

    # Linia albastra este pentru pretul materiei prime
    plt.plot(filtered_df['Month_Year'], filtered_df['Feedstock Price'], marker='o', label='Feedstock Price',
             color='blue', linewidth=2)

    # linia portocalie este pentru costul conversiei
    plt.plot(filtered_df['Month_Year'], filtered_df['Conversion Price'], marker='s', label='Conversion Price',
             color='orange', linewidth=2)


    plt.title(f'Price Evolution: {material_desc} | {supplier} | {plant}')
    plt.xlabel('Month')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

def calculate_price_impact(df, material):
    data = df[df['Material Description'] == material]

    if data.empty:
        print("No data found")
        return

    avg_feed = data['Feedstock Price'].mean()
    avg_conv = data['Conversion Price'].mean()
    avg_trans = data['Transport Price'].mean()

    total = avg_feed + avg_conv + avg_trans

    feed_pct = (avg_feed / total) * 100
    conv_pct = (avg_conv / total) * 100
    trans_pct = (avg_trans / total) * 100

    print(f"\nImpact for {material}:")
    print(f"Feedstock: {feed_pct:.2f}%")
    print(f"Conversion: {conv_pct:.2f}%")
    print(f"Transport: {trans_pct:.2f}%")

        # Plot
    plt.figure(figsize=(6, 6))
    plt.pie(
            [feed_pct, conv_pct, trans_pct],
            labels=['Feedstock', 'Conversion', 'Transport'],
            autopct='%1.1f%%'
        )
    plt.title(f"Price Structure - {material}")
    plt.show()



def compare_all_models(df, material, best_calendaristic_price, theoretical_best):

    from random_search import random_search_material

    # RANDOM
    _, best_random, _ = random_search_material(df, material, n_iter=2000)

    # REAL
    real = best_calendaristic_price[
        best_calendaristic_price['Material Description'] == material
    ]

    # THEORETICAL
    theo = theoretical_best[
        theoretical_best['Material Description'] == material
    ]

    if real.empty or theo.empty or best_random is None:
        print("Missing data")
        return

    real_price = real['Calculated Price'].values[0]
    theo_price = theo['Theoretical Best Final Price'].values[0]
    random_price = best_random['Total Synthetic Price']

    print(f"\nComparison for {material}:")
    print(f"Real: {real_price:.2f}")
    print(f"Theoretical: {theo_price:.2f}")
    print(f"Random: {random_price:.2f}")

    # Plot
    plt.figure(figsize=(8,5))
    plt.bar(['Real','Theoretical','Random'], [real_price, theo_price, random_price])
    plt.title(f"Model Comparison - {material}")
    plt.ylabel("Price")
    plt.show()

def plot_component_trends(df, material):

    data = df[df['Material Description'] == material].copy()

    if data.empty:
        print("No data")
        return

    data['Date'] = pd.to_datetime(data['Final Price Month'])
    data = data.sort_values('Date')

    plt.figure(figsize=(12,6))

    plt.plot(data['Date'], data['Feedstock Price'], label='Feedstock')
    plt.plot(data['Date'], data['Conversion Price'], label='Conversion')
    plt.plot(data['Date'], data['Transport Price'], label='Transport')

    plt.title(f"Component Trends - {material}")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
