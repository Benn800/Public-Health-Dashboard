
# Public Health Data Insights Tool

A Python-based dashboard for analyzing **COVID-19 vaccination data** from **Our World in Data (OWID)**.  
The tool loads a public CSV, cleans and normalizes fields, stores data in **SQLite**, and provides **filtering**, **summaries**, **trend plots**, and **CSV export**, implemented with clean architecture (SOLID), PEP8 style, and a TDD approach.



## 📌 Features
- **Data Access & Loading**: Import OWID vaccination CSV into SQLite.
- **Data Cleaning & Structuring**: Normalize dates and numeric fields.
- **Filtering & Summaries**: Query by country and date range; compute count/min/mean/max.
- **Visualization**: Generate time-series plots using Matplotlib.
- **Export**: Save filtered/filtered results to CSV.
- **Logging**: Rotating log file for key operations.
- **TDD**: Unit tests for core components (services, data source, repository).



## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **Libraries**: `pandas`, `matplotlib`, `pytest`
- **Database**: SQLite (lightweight, file-based)
- **Architecture**: SOLID principles, modular packages





## 📂 Project Structure
task1_public_health/ \
├─ src/ \
│  ├─ app.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Entry point\
│  ├─ config.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Config constants\
│  ├─ logging_conf.py   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Logging setup\
│  ├─ domain/       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Business logic\
│  ├─ infrastructure/  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Data sources & repository\
│  └─ presentation/    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # CLI & charts\
├─ tests/              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Pytest unit tests\
├─ data/              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # SQLite DB\
├─ logs/              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  # Log files\
└─ README.md\


## 🚀 Installation
```bash
# 1) Clone your private repository
git clone https://github.com/Benn800/Public-Health-Dashboard.git
cd Public-Health-Dashboard

# 2) Create & activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt
