**English** | [Türkçe](README.tr.md)

# Hazine Nabzı — Treasury Pulse

> Work in progress. This file is filled in day by day, together with that day's work.

An automated reporting project that compares Türkiye's central government budget, as planned at the start of the year, with what is actually spent month by month.

## What it does

It automates what a finance team does every month: comparing the planned budget with actual spending, finding the variances and reporting them.

The data comes from the budget tables published every month by the General Directorate of Public Accounts (Muhasebat) of the Ministry of Treasury and Finance. The project downloads these tables itself, cleans them, loads them into a database and turns them into a Power BI report.

Questions it answers:

1. Which spending and revenue items deviate most from the plan?
2. Which ministries went over their budget, and which stayed under?
3. In which month of the year does the variance appear?
4. Does the pattern repeat from year to year?
5. Can the year-end outcome be forecast from the first months of the year?

## Data

**Source:** [General Directorate of Public Accounts, Central Government Budget Statistics](https://muhasebat.hmb.gov.tr/merkezi-yonetim-butce-istatistikleri) (in Turkish).

**Coverage:** 2015–2026, monthly. 2026 up to the latest published month.

Three tables are used for each year:

| Table | Content | Rows |
|---|---|---|
| Budget balance table | Main revenue and expenditure items, budget deficit | 23 items |
| Expenditure detail table | Sub-items of expenditure | 23 selected items ([`items.csv`](items.csv)) |
| Institutional table | Ministries and other general budget institutions | 41–52 institutions |

All three tables give the actual amount for each of the 12 months and the plan set at the start of the year for every item. The plan is the initial appropriation in the Budget Law approved by Parliament.

## Cleaning

The 36 raw Excel files are turned into two tables: `data/clean/actuals.csv` (monthly actuals, 13,728 rows) and `data/clean/plans.csv` (annual plans, 1,174 rows).

Each row is a single measurement: the amount of one item, in one year, in one month.

| Column | Content |
|---|---|
| `source` | The table the row comes from: `balance`, `expense_detail`, `ministries` |
| `year`, `month` | Year and month (1–12). `plans.csv` has no month, plans are annual |
| `main_item` | Parent group: expenditure / revenue / balance, a main expenditure item, or the institutions group |
| `item` | Name of the item or institution |
| `amount_thousand_try` | Amount, in thousands of TRY |

The tables are not in the same format from year to year. Differences handled during cleaning:

- **Columns are located by name, not by position.** Some years have an extra column and the positions shift. The plan column is written in seven different ways across the 12 years: "Bütçe Tahmini", "2022 Toplam Bütçe Tahmini*", "Bütçe Başlangıç Ödeneği *", "Toplam Bütçe Ödeneği*" and so on.
- **The plan is the initial appropriation.** The institutional table has a second column for 2015–2024 ("Ödenek Toplamı"): the appropriation after in-year transfers. The other two tables have no equivalent, so it is not used.
- **Month names are abbreviated in some years:** "Oca" instead of "Ocak", and "Agu" for August in 2015.
- **Item names changed in 2021.** Seven names, such as "KİT Görev Zararları" → "KİT Görevlendirme Giderleri". The old names are mapped in the `old_name` column of [`items.csv`](items.csv).
- **The same name can appear more than once.** "Memurlar" (civil servants) appears under both personnel expenditure and social security premiums; "Tahvil Faizi" (bond interest) appears twice, one of them empty. The `search_under` column in `items.csv` says which heading the item must be looked for under.
- **An empty cell means two different things.** If a month has a value for any item in the table, that month has been published and an empty cell means "no spending", recorded as 0. Months with no values at all have not been published yet and are left out.
- **The institutional table has summary rows after the list of institutions:** special budget institutions, regulatory bodies, the central government total. Reading stops at the institutions total row.
- **Institution names are spelled inconsistently:** "Hazine Ve Maliye" / "Hazine ve Maliye".

### Checks

`clean.py` runs three checks on every run and stops if any of them fails:

1. **Row total:** does the sum of the 12 months in each row equal the file's own "Toplam" column?
2. **Institution total:** does the sum of the institutions read equal the total row in the table?
3. **Reconciliation:** do the nine main items in the expenditure detail table give the same amounts as the same items in the balance table? The two tables are published separately, so this is independent evidence that the right rows were read. 1,368 points are compared.

## Setup

*(to be written at the end of day 3)*

## Usage

*(to be written at the end of day 5)*

## Report

*(to be written at the end of day 6)*

## Project structure

```
hazine-nabzi/
├── download.py        Downloads the 2015–2026 tables from Muhasebat
├── clean.py           Cleans the raw files into two tables and runs the checks
├── xls_reader.py      Reads the old .xls files (skips broken format records)
├── items.csv          Items taken from the expenditure detail table, with their old names
├── requirements.txt   Required Python libraries
├── KURALLAR.md        Working rules and daily log of the project (in Turkish)
└── data/
    ├── raw/           Downloaded raw files (not included in the repo)
    └── clean/         Cleaned tables: actuals.csv, plans.csv
```
