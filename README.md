# P&G Linear Regression Project

Acest proiect contine 3 scripturi Python care lucreaza pe fisierul `Project 2 Data.xlsx` si aplica regresie liniara pentru preturi, grupate dupa:

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

- `LiniarRegression.py`
  Foloseste toate datele disponibile din fiecare grup si estimeaza pretul pentru luna urmatoare.

- `LiniarRegressionForLast.py`
  Cere un numar `N` si foloseste doar ultimele `N` luni din fiecare grup pentru a estima luna urmatoare.

- `LiniarRegressionCompare.py`
  Compara predictia obtinuta prin regresie liniara cu ultima luna reala din fiecare grup.

## Fisiere de iesire

- `output.txt`
  Rezultatul generat de `LiniarRegression.py`

- `outputForX.txt`
  Rezultatul generat de `LiniarRegressionForLast.py`

- `outputCompare.txt`
  Rezultatul generat de `LiniarRegressionCompare.py`

## Cerinte

Ai nevoie de Python 3 si de pachetele:

```bash
pip install pandas numpy openpyxl
```

## Cum se ruleaza

### 1. Regresie pe toate datele

```bash
python LiniarRegression.py
```

Scriptul:

- citeste toate lunile disponibile din fiecare grup
- estimeaza luna urmatoare
- scrie rezultatele in `output.txt`

### 2. Regresie pe ultimele N luni

```bash
python LiniarRegressionForLast.py
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
python LiniarRegressionCompare.py
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

## Nota

Numele fisierelor Python sunt scrise cu `Liniar` in loc de `Linear`, pentru a pastra denumirile existente din proiect.
