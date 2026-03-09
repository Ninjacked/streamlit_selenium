# Streamlit Selenium Mapper

Simple Streamlit app for mapping uploaded Excel/CSV headers into a standardized output format.

## Requirements

- Python 3.10+
- `pip`

## Setup (inside `.venv`)

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
streamlit run main.py
```

## Project Structure

- `main.py`: app entry page
- `pages/1_📂_Mapper.py`: mapping UI and processing logic
- `mappings/mappings.py`: placement mapping rules
