# P&G Regression Project

Acest proiect contine mai multe scripturi Python care lucreaza pe fisierul `Project 2 Data.xlsx` si aplica modele de regresie pentru preturi, grupate dupa:

- `Material Type`
- `Material Sub Type`
- `Material Description`
- `Plant`
- `Supplier`

Pentru fiecare grup sunt analizate coloanele:

- `Final Price`
- `Feedstock Price`
- `Conversion Price`
- `Transport Price`

## Fisiere

- `LinearRegression.py`
  Foloseste toate datele disponibile din fiecare grup si estimeaza pretul pentru luna urmatoare.

- `LinearRegressionForLast.py`
  Cere un numar `N` si foloseste doar ultimele `N` luni din fiecare grup pentru a estima luna urmatoare.

- `LinearRegressionCompare.py`
  Compara predictia obtinuta prin regresie liniara cu ultima luna reala din fiecare grup.

- `LRw3Param.py`
  Foloseste `sklearn.LinearRegression` cu 3 parametri (`Feedstock Price`, `Conversion Price`, `Transport Price`) si compara predictia cu ultima luna reala din fiecare grup.

- `Ridgew3Param.py`
  Foloseste `sklearn.Ridge` cu aceiasi 3 parametri si compara predictia cu ultima luna reala din fiecare grup.

- `Lassow3Param.py`
  Foloseste `sklearn.Lasso` cu aceiasi 3 parametri si compara predictia cu ultima luna reala din fiecare grup.

- `comparisons.py`
  Ruleaza `LinearRegression`, `Ridge`, `Lasso` si `XGBoost` pe fiecare grup si afiseaza ce model are eroarea cea mai mica.

- `XGBoostw3Param.py`
  Foloseste `xgboost.XGBRegressor` cu aceiasi 3 parametri si compara predictia cu ultima luna reala din fiecare grup.

- `ignoreGarbage.py`
  Detecteaza valori iesite din tipar in `Final Price` pentru fiecare grup, le exclude din antrenare si apoi compara `LinearRegression`, `Ridge`, `Lasso` si `XGBoost`.

- `prediction_ui.py`
  Deschide o interfata desktop unde alegi modelul, cate luni din urma sa fie folosite, daca se elimina valorile garbage si incarci un fisier Excel pentru predictii pe grup.

## Fisiere de iesire

- `output.txt`
  Rezultatul generat de `LinearRegression.py`

- `outputForX.txt`
  Rezultatul generat de `LinearRegressionForLast.py`

- `outputCompare.txt`
  Rezultatul generat de `LinearRegressionCompare.py`

- `outputSklearn3Param.txt`
  Rezultatul generat de `LRw3Param.py`

- `outputRidge3Param.txt`
  Rezultatul generat de `Ridgew3Param.py`

- `outputLasso3Param.txt`
  Rezultatul generat de `Lassow3Param.py`

- `outputCompareLinearRidgeLasso3Param.txt`
  Rezultatul generat de `comparisons.py`

- `outputXGBoost3Param.txt`
  Rezultatul generat de `XGBoostw3Param.py`

- `outputIgnoreGarbage.txt`
  Rezultatul generat de `ignoreGarbage.py`

## Cerinte

Ai nevoie de Python 3 si de pachetele:

```bash
pip install pandas numpy openpyxl scikit-learn xgboost
```

## Cum se ruleaza

### 1. Regresie pe toate datele

```bash
python LinearRegression.py
```

Scriptul:

- citeste toate lunile disponibile din fiecare grup
- estimeaza luna urmatoare
- scrie rezultatele in `output.txt`

### 2. Regresie pe ultimele N luni

```bash
python LinearRegressionForLast.py
```

Scriptul iti cere:

```text
How many months back do you want to use for linear regression?
```

Introdu un numar mai mare sau egal cu `2`.

Scriptul:

- foloseste doar ultimele `N` luni din fiecare grup
- estimeaza luna urmatoare
- scrie rezultatele in `outputForX.txt`

### 3. Comparatie intre predictie si ultima luna reala

```bash
python LinearRegressionCompare.py
```

Scriptul iti cere:

```text
Cate luni din urma vrei sa folosesti pentru comparatie? Scrie un numar sau 'all':
```

Poti introduce:

- un numar `N` mai mare sau egal cu `2`
- `all`, pentru a folosi toate lunile din grup, in afara de ultima

Logica este:

- ultima luna din grup este pastrata ca valoare reala de comparatie
- lunile anterioare sunt folosite pentru regresie
- se calculeaza predictia pentru luna urmatoare
- predictia este comparata cu ultima luna reala

In `outputCompare.txt` vei gasi:

- istoricul folosit
- ultima luna reala
- valorile prezise si reale
- diferenta
- diferenta absoluta
- eroarea procentuala

Toate valorile numerice din comparatie sunt afisate cu 2 zecimale.

### 4. XGBoost pe 3 parametri

```bash
python XGBoostw3Param.py
```

Scriptul:

- foloseste `Feedstock Price`, `Conversion Price` si `Transport Price`
- pastreaza ultima luna din fiecare grup pentru comparatie
- antreneaza un model `XGBRegressor` pe lunile anterioare
- scrie rezultatele in `outputXGBoost3Param.txt`

In output vei gasi:

- luna reala folosita pentru comparatie
- valorile prezise si reale
- diferenta
- diferenta absoluta
- eroarea procentuala
- importanta fiecarui feature in modelul XGBoost

### 5. Comparatie dupa eliminarea valorilor nepotrivite

```bash
python ignoreGarbage.py
```

Scriptul:

- pastreaza ultima luna din fiecare grup pentru comparatie
- cauta outlieri in istoricul de antrenare doar pe `Final Price`, folosind regula IQR
- elimina valorile care ies din intervalul normal al grupului
- antreneaza apoi `LinearRegression`, `Ridge`, `Lasso` si `XGBoost` pe datele curatate
- scrie rezultatele in `outputIgnoreGarbage.txt`

### 6. Interfata pentru alegerea modelului

```bash
python prediction_ui.py
```

In interfata poti:

- incarca un fisier Excel ca `Project 2 Data.xlsx`
- alege modelul: `Linear Regression`, `Ridge`, `Lasso` sau `XGBoost`
- seta daca foloseste toate lunile sau doar ultimele `N` luni
- bifa daca vrei sa elimine valorile garbage din `Final Price`
- vedea predictia pentru fiecare grup direct in tabel

## Observatii

- Daca un grup nu are suficiente date, scriptul va afisa un mesaj si va trece la urmatorul grup.
- Valorile lipsa din coloanele de pret sunt completate cu `0`.
- Regresia liniara este implementata manual cu `numpy`, fara folosirea unei biblioteci externe de machine learning.

## Structura de baza a calculelor

Pentru fiecare grup:

1. datele sunt sortate crescator dupa `Final Price Month`
2. se construieste axa lunilor ca `1, 2, 3, ...`
3. se calculeaza coeficientii regresiei liniare
4. se estimeaza valoarea pentru luna urmatoare
