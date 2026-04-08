import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
import os

# ------------------------------------------------------------
# Helper: Load Headers.xlsx (Headers + Basis + synonyms)
# ------------------------------------------------------------
def load_headers_config():
    headers_path = "Headers.xlsx"
    if not os.path.exists(headers_path):
        st.error(f"Configuration file '{headers_path}' not found in the current directory.")
        st.stop()
    xl = pd.ExcelFile(headers_path)

    # 1. Headers sheet (standard headers + synonyms)
    if 'Headers' not in xl.sheet_names:
        st.error("Headers file must contain sheet 'Headers'")
        st.stop()
    headers_df = pd.read_excel(headers_path, sheet_name='Headers', header=None)
    standard_headers = headers_df.iloc[0].astype(str).str.strip().tolist()
    synonyms = []
    for col_idx in range(len(standard_headers)):
        col_synonyms = headers_df.iloc[1:, col_idx].dropna().astype(str).str.strip().tolist()
        synonyms.append(col_synonyms)

    # 2. Basis sheet (value transformations)
    basis_maps = {}
    if 'Basis' in xl.sheet_names:
        basis_df = pd.read_excel(headers_path, sheet_name='Basis')
        if 'LEVEL/CYCLE' in basis_df.columns and 'FINAL LEVEL/CYCLE' in basis_df.columns:
            basis_maps['LEVEL/CYCLE'] = dict(zip(
                basis_df['LEVEL/CYCLE'].astype(str).str.strip(),
                basis_df['FINAL LEVEL/CYCLE'].astype(str).str.strip()
            ))
        if 'PROD TYPE' in basis_df.columns and 'FINAL PROD TYPE' in basis_df.columns:
            basis_maps['PROD TYPE'] = dict(zip(
                basis_df['PROD TYPE'].astype(str).str.strip(),
                basis_df['FINAL PROD TYPE'].astype(str).str.strip()
            ))
        if 'PLACEMENT' in basis_df.columns and 'FINAL PLACEMENT' in basis_df.columns:
            basis_maps['PLACEMENT'] = dict(zip(
                basis_df['PLACEMENT'].astype(str).str.strip(),
                basis_df['FINAL PLACEMENT'].astype(str).str.strip()
            ))
    else:
        st.warning("Basis sheet not found; no value transformations will be applied.")

    return standard_headers, synonyms, basis_maps

def map_to_standard_headers(df_input, standard_headers, synonyms):
    """Map input columns to standard headers using case-insensitive synonym matching."""
    mapping = {}
    for i, std_col in enumerate(standard_headers):
        possible_names = [std_col] + synonyms[i]
        matched = None
        for pname in possible_names:
            pname_norm = pname.strip().lower()
            for col in df_input.columns:
                if col.strip().lower() == pname_norm:
                    matched = col
                    break
            if matched:
                break
        if matched:
            mapping[matched] = std_col
    df_std = df_input.rename(columns=mapping)
    existing = [col for col in standard_headers if col in df_std.columns]
    df_std = df_std[existing]

    # Special: if LEVEL/CYCLE is missing but DUE DATE exists in original data
    if 'LEVEL/CYCLE' not in df_std.columns and 'DUE DATE' in df_input.columns:
        df_std['LEVEL/CYCLE'] = df_input['DUE DATE']
        st.info("Mapped 'DUE DATE' column to 'LEVEL/CYCLE'.")

    return df_std

def apply_basis_transformations(df, basis_maps):
    """Add FINAL_* columns using the Basis sheet mappings."""
    for src_col, value_map in basis_maps.items():
        if src_col in df.columns:
            final_col = f"FINAL_{src_col}"
            df[final_col] = df[src_col].astype(str).str.strip().map(value_map).fillna(df[src_col])
        else:
            st.warning(f"Basis source column '{src_col}' not found, skipping.")
    return df

# ------------------------------------------------------------
# Helper: Load Settings (BCRM & CHCODE) from local directory
# ------------------------------------------------------------
def load_settings():
    settings_path = "BPI PL XDAYS_SETTINGS.xlsx"
    if not os.path.exists(settings_path):
        st.error(f"Settings file '{settings_path}' not found in the current directory.")
        st.stop()
    xl = pd.ExcelFile(settings_path)

    if 'BCRM' not in xl.sheet_names:
        st.error("Settings file must contain 'BCRM' sheet")
        st.stop()
    bcrm = pd.read_excel(settings_path, sheet_name='BCRM')
    if 'Columns' not in bcrm.columns or 'Equivalent in Raw' not in bcrm.columns:
        st.error("BCRM sheet must have 'Columns' and 'Equivalent in Raw'")
        st.stop()

    if 'CHCODE' not in xl.sheet_names:
        st.error("Settings file must contain 'CHCODE' sheet")
        st.stop()
    chcode = pd.read_excel(settings_path, sheet_name='CHCODE')
    required = ['BANK', 'LEVEL/CYCLE', 'PROD TYPE', 'PLACEMENT', 'Code Pattern']
    for col in required:
        if col not in chcode.columns:
            st.error(f"CHCODE sheet missing column: {col}")
            st.stop()
    return bcrm, chcode

def get_code_pattern(row, chcode_df):
    # Use FINAL_* columns if they exist, otherwise original
    bank = str(row.get('BANK', '')).strip()
    level = str(row.get('FINAL_LEVEL/CYCLE', row.get('LEVEL/CYCLE', ''))).strip()
    prod = str(row.get('FINAL_PROD TYPE', row.get('PROD TYPE', ''))).strip()
    placement = str(row.get('FINAL_PLACEMENT', row.get('PLACEMENT', ''))).strip()

    if not bank:
        bank = "BPI PL XDAYS"

    # Case‑insensitive match
    match = chcode_df[
        (chcode_df['BANK'].astype(str).str.strip().str.lower() == bank.lower()) &
        (chcode_df['LEVEL/CYCLE'].astype(str).str.strip().str.lower() == level.lower()) &
        (chcode_df['PROD TYPE'].astype(str).str.strip().str.lower() == prod.lower()) &
        (chcode_df['PLACEMENT'].astype(str).str.strip().str.lower() == placement.lower())
    ]

    if not match.empty:
        return str(match.iloc[0]['Code Pattern']).strip()

    # Fallback: extract number from level
    num_match = re.search(r'(\d+)', level)
    if num_match:
        number = num_match.group(1).zfill(2)
        return f"{number}BPEXL"

    return "UNKNOWN"

# ------------------------------------------------------------
# Helper: Load / Update Sequence
# ------------------------------------------------------------
def load_sequence():
    seq_path = "Sequence.xlsx"
    if not os.path.exists(seq_path):
        st.warning("Sequence.xlsx not found. Starting fresh counters.")
        return {}
    df = pd.read_excel(seq_path, sheet_name=0)
    if 'Code Pattern' not in df.columns or 'YYMM' not in df.columns or 'Last Count' not in df.columns:
        st.warning("Sequence file missing required columns. Starting fresh.")
        return {}
    seq_dict = {}
    for _, row in df.iterrows():
        key = (str(row['Code Pattern']).strip(), str(row['YYMM']).strip())
        seq_dict[key] = int(row['Last Count'])
    return seq_dict

def save_sequence(seq_dict):
    rows = [{'Code Pattern': p, 'YYMM': y, 'Last Count': c} for (p, y), c in seq_dict.items()]
    df_seq = pd.DataFrame(rows)
    df_seq.to_excel("Sequence.xlsx", index=False)

# ------------------------------------------------------------
# Helper: Format date columns and set defaults
# ------------------------------------------------------------
def format_dates_and_agent(df, bcrm):
    """
    Format date columns as MM/dd/yyyy based on BCRM's 'Data Type' column.
    Fill missing Agent with "MSPM" and ensure Agent column exists.
    """
    # Build a mapping of output column -> data type from BCRM
    dtype_map = {}
    for _, row in bcrm.iterrows():
        col = str(row['Columns']).strip()
        dtype = str(row.get('Data Type', '')).strip().lower() if 'Data Type' in row else ''
        dtype_map[col] = dtype

    # Apply date formatting
    for col in df.columns:
        if col in dtype_map and dtype_map[col] == 'date':
            # Convert to datetime, then format as MM/dd/yyyy
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.strftime('%m/%d/%Y')
        elif 'DATE' in col.upper() and col not in dtype_map:
            # Fallback: if column name contains 'DATE' but not in BCRM, also try formatting
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.strftime('%m/%d/%Y')

    # Ensure Agent column exists, fill empty with "MSPM"
    if 'Agent' not in df.columns:
        df['Agent'] = "MSPM"
    else:
        df['Agent'] = df['Agent'].fillna("MSPM").replace("", "MSPM")
        # Also handle numeric or other types
        df['Agent'] = df['Agent'].astype(str).str.strip()
        df.loc[df['Agent'] == '', 'Agent'] = "MSPM"
        df.loc[df['Agent'].isna(), 'Agent'] = "MSPM"

    return df

# ------------------------------------------------------------
# Main processing
# ------------------------------------------------------------
def process_data(data_df, standard_headers, synonyms, basis_maps, bcrm, chcode, seq_dict):
    # Step 1: Map to standard headers
    df_std = map_to_standard_headers(data_df, standard_headers, synonyms)

    # Step 2: Apply Basis transformations (creates FINAL_* columns)
    df_std = apply_basis_transformations(df_std, basis_maps)

    # Step 3: Build output dataframe from BCRM
    output_cols = []
    for _, row in bcrm.iterrows():
        out_col = str(row['Columns']).strip()
        src_std = str(row['Equivalent in Raw']).strip() if pd.notna(row['Equivalent in Raw']) else ''
        output_cols.append((out_col, src_std))

    out_df = pd.DataFrame()
    for out_col, src_std in output_cols:
        if src_std and src_std in df_std.columns:
            out_df[out_col] = df_std[src_std]
        else:
            out_df[out_col] = ""   # empty string instead of NaN/NA

    # Step 4: Generate Ch Code
    if 'DATE PROCESSED' not in out_df.columns:
        st.warning("DATE PROCESSED column missing. Using today's date for YYMM.")
        date_processed = pd.Series([datetime.now()] * len(out_df))
    else:
        date_processed = pd.to_datetime(out_df['DATE PROCESSED'], errors='coerce')
        date_processed = date_processed.fillna(datetime.now())
    out_df['__YYMM'] = date_processed.dt.strftime('%y%m')

    # Bring in needed columns for pattern lookup
    lookup_cols = ['BANK', 'LEVEL/CYCLE', 'PROD TYPE', 'PLACEMENT',
                   'FINAL_LEVEL/CYCLE', 'FINAL_PROD TYPE', 'FINAL_PLACEMENT']
    for col in lookup_cols:
        if col in df_std.columns and col not in out_df.columns:
            out_df[col] = df_std[col]

    out_df['__Pattern'] = out_df.apply(lambda row: get_code_pattern(row, chcode), axis=1)
    out_df['__Key'] = out_df.apply(lambda row: (row['__Pattern'], row['__YYMM']), axis=1)

    # Determine starting counters
    start_counter = {}
    for key in out_df['__Key'].unique():
        last = seq_dict.get(key, 0)
        start_counter[key] = last + 1

    out_df['__counter'] = 0
    for key, group_indices in out_df.groupby('__Key').groups.items():
        start = start_counter[key]
        for i, idx in enumerate(group_indices):
            out_df.at[idx, '__counter'] = start + i

    out_df['Ch Code'] = out_df.apply(
        lambda row: f"{row['__Pattern']}{row['__YYMM']}-{row['__counter']:03d}",
        axis=1
    )

    # Capture new last counts
    new_counts = {}
    for key, group in out_df.groupby('__Key'):
        new_counts[key] = group['__counter'].max()

    # Clean temporary columns
    out_df.drop(['__YYMM', '__Pattern', '__Key', '__counter'], axis=1, inplace=True)

    # Step 5: Format dates and set default Agent
    out_df = format_dates_and_agent(out_df, bcrm)

    # Step 6: Reorder columns – put Agent before Ch Code, both at the end
    all_cols = list(out_df.columns)
    if 'Agent' in all_cols:
        all_cols.remove('Agent')
    if 'Ch Code' in all_cols:
        all_cols.remove('Ch Code')
    # Final order: all other columns, then Agent, then Ch Code
    final_cols = all_cols + ['Agent', 'Ch Code']
    # Keep only columns that actually exist
    final_cols = [c for c in final_cols if c in out_df.columns]
    out_df = out_df[final_cols]

    return out_df, new_counts

# ------------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------------
st.set_page_config(page_title="BPI PL XDAYS Processor", layout="wide")
st.title("📄 BPI PL XDAYS Processor (with Basis, Sequence & Date Formatting)")
st.markdown("""
The following configuration files must be present in the **same folder as this app**:
- `Headers.xlsx` (sheets: Headers, Basis)
- `BPI PL XDAYS_SETTINGS.xlsx` (sheets: BCRM, CHCODE)
- `Sequence.xlsx` (will be updated automatically)

Upload your data file to process.
""")

# Load config files once
with st.spinner("Loading configuration files..."):
    standard_headers, synonyms, basis_maps = load_headers_config()
    bcrm, chcode = load_settings()
    seq_dict = load_sequence()
st.success("Configuration files loaded successfully.")

# Data file upload
data_file = st.file_uploader("📂 Upload Data Excel File", type=["xlsx", "xls"])

if data_file:
    try:
        df_raw = pd.read_excel(data_file)
        st.subheader("Raw Data Preview")
        st.dataframe(df_raw.head(10))
    except Exception as e:
        st.error(f"Cannot read data: {e}")
        st.stop()

    with st.spinner("Processing data and generating codes..."):
        try:
            result_df, new_counts = process_data(df_raw, standard_headers, synonyms, basis_maps, bcrm, chcode, seq_dict)

            st.subheader("Processed Output Preview")
            st.dataframe(result_df.head(10))

            # Update sequence file
            for key, last in new_counts.items():
                seq_dict[key] = last
            save_sequence(seq_dict)
            st.success(f"Sequence updated for {len(new_counts)} pattern(s).")

            # Download processed data
            output_result = io.BytesIO()
            with pd.ExcelWriter(output_result, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Output')
            st.download_button("💾 Download Processed Data", data=output_result.getvalue(),
                               file_name="processed_output.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Processing failed: {e}")
else:
    st.info("👈 Please upload a data Excel file to start.")