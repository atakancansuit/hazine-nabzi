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
├── xls_reader.py      Reads the old .xls files (skips broken format records)
├── items.csv          List of items taken from the expenditure detail table
├── requirements.txt   Required Python libraries
├── KURALLAR.md        Working rules and daily log of the project (in Turkish)
└── data/raw/          Downloaded raw files (not included in the repo)
```
