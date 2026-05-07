# Evaluation

---

## SK Popis

Táto časť repozitára obsahuje podklady a nástroje na evaluáciu generovaných riešení.

Obsahuje:
- testovacie scenáre (unit testy),
- adaptéry pre jednotlivé systémy,
- vygenerované výstupy,
- logy z testovania,
- logy z činnosti jednotlivých agentov navrhovaného systému,
- výpočty metrík (F1 skóre, kvalita kódu).

Evaluácia je založená na automatizovanom testovaní a porovnávaní očakávaného a skutočného stavu systému.

### Požiadavky

- Python 3.x
- pytest
- pylint
- radon

Inštalácia:
```bash
pip install pytest pylint radon
```

### Spustenie testov
Testy sa spúšťajú pomocou nástroja pytest.
Príklad:
```bash
python -m pytest eshop_tests.py -v
```
Výsledky:
- zobrazia sa v termináli
- F1 skóre a logy jednotlivých testov sa ukladajú do súboru test_log.txt

### Vyhodnotenie kvality kódu
Na analýzu kvality kódu sa používajú nástroje pylint a radon.
Príklad:
```bash
python -m pylint output2_2.py --disable=C0114,C0115,C0116 >> code_quality.txt
python -m radon mi output2_2.py >> code_quality.txt
python -m radon cc output2_2.py -s -a >> code_quality.txt
```
Výsledky sa ukladajú do súboru code_quality.txt.

---

## EN Description

This directory contains artifacts and tools for evaluating generated solutions.

It includes:
- test cases,
- adapters for different systems,
- generated outputs,
- logs from evaluation,
- metric computation (F1 score, code quality).

The evaluation is based on automated testing and comparison of expected and actual system states.

## Requirements

- Python 3.x
- pytest
- pylint
- radon

Install dependencies:

```bash
pip install pytest pylint radon
```

### Running tests
Tests are executed using pytest.
Example:
```bash
python -m pytest eshop_tests.py -v
```
Results:
- printed in terminal
- F1 score and logs of unit tests are stored in test_log.txt

### Code quality evaluation
Code quality is evaluated using pylint and radon.
Example:
```bash
python -m pylint output2_2.py --disable=C0114,C0115,C0116 >> code_quality.txt
python -m radon mi output2_2.py >> code_quality.txt
python -m radon cc output2_2.py -s -a >> code_quality.txt
```
Results are saved into code_quality.txt.
