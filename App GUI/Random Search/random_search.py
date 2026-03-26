import pandas as pd
import random
import matplotlib.pyplot as plt


# CURATAREA DATELOR

def load_data(file_path):
    df = pd.read_excel(file_path)

    # Elimin randurile care nu contin date (sunt goale) din urmatoarele coloane
    df = df.dropna(subset=['Feedstock Price', 'Conversion Price', 'Transport Price', 'Grammage'])
    df = df.drop_duplicates()

    # Pastrez doar materialele active
    if 'Material Status' in df.columns:
        df = df[df['Material Status'] == 'active']

    # Urmeaza sa verific daca Final Price este calculat corect
    # Creez o coloana noua numita Calculated Price adunand cele 3 costuri
    df['Calculated Price'] = df['Feedstock Price'] + df['Conversion Price'] + df['Transport Price']
    # Calculez eficienta: impart costul la gramaj pentru a afla pretul per gram
    df['Efficiency Price'] = df['Calculated Price'] / df['Grammage']

    return df


# ----------------------------------------------------
# RANDOM SEARCH
def random_search_material(df, material_name, n_iter=1000):
    # Filtrez materialul ignorand literele mari/mici si spatiile in plus pentru a preveni erorile "empty sequence"
    data = df[
        df['Material Description'].astype(str).str.strip().str.lower() == str(material_name).strip().lower()].copy()

    # Verific daca nu se gasesc date pentru acest material
    if data.empty:
        return None, None, None

    # Extrag furnizorii si fabricile disponibile pentru acest material
    suppliers = data['Supplier'].dropna().unique()
    plants = data['Plant'].dropna().unique()

    # Verific daca avem cel putin un furnizor si o fabrica din care sa alegem
    if len(suppliers) == 0 or len(plants) == 0:
        return None, None, None

    results = []

    # Incep algoritmul
    for _ in range(n_iter):
        # Selectez aleatoriu o combinatie de furnizor si fabrica
        supplier = random.choice(suppliers)
        plant = random.choice(plants)

        # Filtrez setul de date pentru furnizorul si fabrica aleasa
        supplier_data = data[data['Supplier'] == supplier]
        plant_data = data[data['Plant'] == plant]

        # Daca niciunul nu exista pentru acest material, trec la urmatoarea iteratie
        if supplier_data.empty or plant_data.empty:
            continue

        # Selectez aleatoriu un rand istoric specific pentru furnizor
        row_supplier = supplier_data.sample(1).iloc[0]

        # Selectez aleatoriu un rand istoric specific pentru fabrica
        row_transport = plant_data.sample(1).iloc[0]

        # Extrag preturile componentelor pentru a construi pretul sintetic
        feedstock = row_supplier['Feedstock Price']
        conversion = row_supplier['Conversion Price']
        transport = row_transport['Transport Price']
        grammage = row_supplier['Grammage']

        # Calculez noul pret total sintetic si eficienta
        total_price = feedstock + conversion + transport
        efficiency = total_price / grammage

        # Salvez rezultatul acestei combinatii
        results.append({
            'Material Description': material_name,
            'Supplier': supplier,
            'Plant': plant,
            'Feedstock Price': feedstock,
            'Conversion Price': conversion,
            'Transport Price': transport,
            'Total Synthetic Price': total_price,
            'Synthetic Efficiency': efficiency
        })

    # Daca nu s-au format cu succes combinatii valide, iesim
    if len(results) == 0:
        return None, None, None

    results_df = pd.DataFrame(results)

    # Identific cel mai bun pret si eficienta teoretica generala din esantioanele aleatoare
    best_total = results_df.loc[results_df['Total Synthetic Price'].idxmin()]
    best_eff = results_df.loc[results_df['Synthetic Efficiency'].idxmin()]

    return results_df, best_total, best_eff




def plot_random_search_distribution(results_df, material_name):
    if results_df is None or results_df.empty:
        print(f"Nu exista date de afisat pentru {material_name}.")
        return

    plt.style.use('dark_background')
    plt.figure(figsize=(14, 7))

    plt.hist(results_df['Total Synthetic Price'], bins=50, color='cyan', edgecolor='black', alpha=0.7,
             label='Combinatii Simulate')

    best_price = results_df['Total Synthetic Price'].min()
    avg_price = results_df['Total Synthetic Price'].mean()
    worst_price = results_df['Total Synthetic Price'].max()

    plt.axvline(best_price, color='lime', linestyle='-', linewidth=3, label=f'Cel mai bun gasit: {best_price:.2f}')
    plt.axvline(avg_price, color='yellow', linestyle='--', linewidth=2, label=f'Media: {avg_price:.2f}')
    plt.axvline(worst_price, color='crimson', linestyle=':', linewidth=2, label=f'Cel mai slab: {worst_price:.2f}')

    plt.title(f'{material_name}\nDistributia a {len(results_df)} Combinatii Sintetice',
              fontsize=16, fontweight='bold', color='white')
    plt.xlabel('Pret Total Sintetic', fontsize=12, color='lightgray')
    plt.ylabel('Frecventa', fontsize=12, color='lightgray')

    plt.legend(facecolor='black', edgecolor='white', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.4)
    plt.tight_layout()
    plt.show()


# -------------------------
# Main

if __name__ == "__main__":
    file_path = "Project 2 Data.xlsx"

    print("Incarcam datele...")
    df = load_data(file_path)

    # 1. Test pentru un singur material si afisarea graficului
    test_material = "Description 1"
    print(f"\n--- Rulam testul si graficul pentru: {test_material} ---")
    results_df, best_total, best_eff = random_search_material(df, test_material, n_iter=2000)

    if results_df is not None:
        plot_random_search_distribution(results_df, test_material)
        print("Graficul a fost afisat.")
    else:
        print(f"Nu s-au gasit combinatii pentru {test_material}.")

    # 2. Rulare pentru toate materialele
    unique_materials = df['Material Description'].dropna().unique()
    all_best_totals = []

    # Parcurg fiecare material unic din setul de date
    for material in unique_materials:
        # Rulez 2000 de iteratii de combinatii aleatoare per material
        _, best_total, _ = random_search_material(df, material, n_iter=2000)

        # Daca cautarea a gasit o combinatie valida, o adaugam la lista noastra finala
        if best_total is not None:
            all_best_totals.append(best_total)
            print(f"Procesat: {material} | Cel mai bun pret sintetic: {best_total['Total Synthetic Price']:.2f}")

    # Compilez rezultatele finale intr-un nou DataFrame si export intr-un excel nou
    if all_best_totals:
        final_results_df = pd.DataFrame(all_best_totals)
        final_results_df.to_excel("All_Materials_Random_Search_Results.xlsx", index=False)
        print("\n✅ Optimizare Completa! Fisier salvat: All_Materials_Random_Search_Results.xlsx")
    else:
        print("\n❌ Nu s-au gasit combinatii valide pentru niciun material.")
