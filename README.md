**English** | [Türkçe](README.tr.md)

# Hazine Nabzı — Treasury Pulse

> Work in progress. This file is filled in day by day, together with that day's work.

An automated reporting project that compares Türkiye's central government budget, as planned at the start of the year, with what is actually spent month by month.

## What it does

It automates what a finance team does every month: it compares the planned budget with actual spending, finds the variances and reports them.

The data comes from the budget tables published every month by the General Directorate of Public Accounts (Muhasebat) of the Ministry of Treasury and Finance. The project downloads these tables itself, cleans them, loads them into a database and turns them into a Power BI report.

Questions it answers:

1. Which spending and revenue items deviate most from the plan?
2. Which ministries went over their budget, and which stayed under?
3. In which month of the year does the variance appear?
4. Does the pattern repeat from year to year?
5. Can the year-end outcome be forecast from the first months of the year?

## Data

**Source:** [General Directorate of Public Accounts, Central Government Budget Statistics](https://muhasebat.hmb.gov.tr/merkezi-yonetim-butce-istatistikleri) (in Turkish).

**Coverage:** 2015–2026, monthly. 2026 up to the latest published month (August).

Three tables are used for each year:

| Table | Content | Rows |
|---|---|---|
| Budget balance table | Main revenue and expenditure items, budget deficit | 23 items |
| Expenditure detail table | Sub-items of expenditure | 23 selected items ([`items.csv`](items.csv)) |
| Institutional table | Ministries and other general budget institutions | 41–52 institutions |

All three tables give the actual amount for each of the 12 months and the plan set at the start of the year for every item. The plan is the initial appropriation in the Budget Law approved by Parliament.

## Cleaning

The 36 raw Excel files were turned into two tables: `data/clean/actuals.csv` (monthly actuals, 13,728 rows) and `data/clean/plans.csv` (annual plans, 1,174 rows).

Each row is a single measurement: the amount of one item, in one year, in one specific month of that year.

| Column | Content |
|---|---|
| `source` | The table the row comes from: `balance`, `expense_detail`, `ministries` |
| `year`, `month` | Year and month (1–12). `plans.csv` has no month, plans are annual |
| `main_item` | Parent group: expenditure / revenue / balance, a main expenditure item, or the institutions group |
| `item` | Name of the item or institution |
| `amount_thousand_try` | Amount, in thousands of TRY |

The tables are not in the same format from year to year. What the cleaning step resolves:

- **Columns are located by name, not by position.** Some years have an extra column and the positions shift. The plan column is written in seven different ways across the 12 years: "Bütçe Tahmini", "2022 Toplam Bütçe Tahmini*", "Bütçe Başlangıç Ödeneği *", "Toplam Bütçe Ödeneği*" and so on. They are standardised into one column.
- **The plan is the initial appropriation.** The institutional table has a second column for 2015–2024 ("Ödenek Toplamı"): the appropriation after in-year transfers. The other two tables have no equivalent, so it was not used.
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

## Calculations

Variance, cumulative progress and forecast calculations live in the database as views ([`sql/views.sql`](sql/views.sql)). The report, the Excel output and the management commentary all read the same views, so each calculation is written in one place.

| View | One row is | Question it answers |
|---|---|---|
| `v_monthly` | One item in one month: that month's amount, the cumulative amount since January, its share of the plan, and the average share at the same month in previous years | Where are we against the plan, and is that fast or slow compared with previous years? |
| `v_annual` | One item in one year: total, plan, variance amount and variance percentage | How far above the plan did the year close? |
| `v_variance_rank` | The same rows with two rankings: by variance amount and by variance percentage | Which items and institutions deviate most from the plan? |
| `v_year_end_forecast` | One item of the open year: the amount so far, the year-end forecast and the forecast as a share of the plan | How will the year close at this rate? |
| `v_forecast_backtest` | One month of a completed year: the forecast that would have been made then, and how far off it was | How much can the forecast be trusted? |

The `sp_monthly_report` procedure in [`sql/procedures.sql`](sql/procedures.sql) returns the main table of the report for a given year and source in a single call:

```sql
EXEC sp_monthly_report @year = 2026, @source = 'balance';
```

Example queries are in [`sql/examples.sql`](sql/examples.sql).

### Year-end forecast

The method is the rolling forecast logic used by finance teams; there is no machine learning. Whatever share of an item's annual total had been spent by the same month in previous years is applied to this year's cumulative amount. This accounts for spending piling up at the end of the year: by the end of August an average of 66% of personnel expenditure has been spent, but only 46% of capital expenditure.

The method was backtested. For every completed year a forecast was produced with that year's own data excluded, then compared with the actual outcome (balance table items, 2015–2025):

| Data available | Median error |
|---|---|
| 4 months | 11.4% |
| 6 months | 8.1% |
| 8 months | 5.9% |
| 10 months | 3.4% |

The error is lower for large items: forecast from August 2025 data, total expenditure would have been off by 0.1% and tax revenue by 1.0%. The method misses in unusual years; for capital expenditure in 2023 it is off by 21.6%.

## Setup

**Requirements:** Python 3.12+, SQL Server (2019 or later; the free Express edition is enough).

```bash
git clone <repo>
cd hazine-nabzi
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Create the database and the user once:

```sql
CREATE DATABASE hazine_nabzi;
CREATE LOGIN hazine WITH PASSWORD = '<password>', CHECK_POLICY = OFF;
USE hazine_nabzi;
CREATE USER hazine FOR LOGIN hazine;
ALTER ROLE db_owner ADD MEMBER hazine;
```

Put the connection details in `.env`:

```bash
cp .env.example .env
```

If SQL Server runs on Windows while the code runs in WSL, three settings are needed on the server: SQL login (mixed mode), TCP connections, and a firewall rule for port 1433. `DB_SERVER` is then not `localhost` but the address of the Windows host as seen from WSL:

```bash
ip route show default | awk '{print $3}'
```

## Usage

The whole pipeline runs with one command:

```bash
.venv/bin/python run.py
```

It downloads, cleans, loads into the database and applies the calculations, in that order. Each step's output goes both to the screen and to `logs/<date>.log`. If a step fails the pipeline stops there, so bad data never reaches the next step.

The steps can also be run separately:

```bash
.venv/bin/python download.py   # downloads the raw files from Muhasebat
.venv/bin/python clean.py      # cleans them into data/clean/ and runs the checks
.venv/bin/python load.py       # loads the clean tables into SQL Server
.venv/bin/python apply_sql.py  # applies the views and the procedure to the database
.venv/bin/python run.py --skip-download   # uses the raw files already on disk
```

### Monthly schedule

Muhasebat publishes the data in the middle of each month. The pipeline is scheduled to run on the 20th of every month, so the new month's data is downloaded, cleaned and loaded without anyone touching it.

Through the Windows Task Scheduler, calling the command inside WSL:

```
schtasks /Create /TN "Hazine Nabzi - aylik guncelleme" ^
  /TR "wsl.exe -d Ubuntu -- /home/ataka/hazine-nabzi/.venv/bin/python /home/ataka/hazine-nabzi/run.py" ^
  /SC MONTHLY /D 20 /ST 09:00
```

## Report

*(to be written at the end of day 6)*

## Project structure

```
hazine-nabzi/
├── download.py        Downloads the 2015–2026 tables from Muhasebat
├── clean.py           Cleans the raw files into two tables and runs the checks
├── load.py            Loads the clean tables into SQL Server
├── apply_sql.py       Applies the views and procedures in sql/ to the database
├── run.py             Runs the whole pipeline with one command
├── xls_reader.py      Reads the old .xls files (skips broken format records)
├── items.csv          Items taken from the expenditure detail table, with their old names
├── .env.example       Example of the database connection settings (.env is not in the repo)
├── requirements.txt   Required Python libraries
├── KURALLAR.md        Working rules and daily log of the project (in Turkish)
├── sql/
│   ├── views.sql      Report calculations: five views
│   ├── procedures.sql The management report procedure
│   └── examples.sql   Example queries
├── data/
│   ├── raw/           Downloaded raw files (not included in the repo)
│   └── clean/         Cleaned tables: actuals.csv, plans.csv
└── logs/              Run logs (not included in the repo)
```
