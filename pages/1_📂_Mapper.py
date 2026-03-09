import streamlit as st
import pandas as pd
from io import BytesIO
from mappings.mappings import placements

st.title("📂 Header Automation Tool")

placement_name = st.selectbox(
    "Select Placement",
    options=list(placements.keys())
)

config = placements[placement_name]
HEADER_MAPPING = config["header_mapping"]
CUSTOM_FIELDS = config["custom_fields"]
FINAL_COLUMN_ORDER = config["final_column_order"]
TEAM_NAME = config["team_name"]
CLEANING_RULE = config["cleaning"].get("no_leading_zero_for_accountNumber", False)

uploaded_file = st.file_uploader(
    "Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"]
)

if uploaded_file:
    # --- Read file ---
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # --- Normalize headers (strip spaces, keep original case for mapping) ---
    df.columns = df.columns.str.strip()

    # --- Detect Truly Empty Columns ---
    empty_columns = []
    for col in df.columns:
        series = df[col]
        is_blank = series.isna() | (series.astype(str).str.strip() == "")
        if is_blank.all():
            empty_columns.append(col)

    # --- Map Non-Empty Standard Headers (with multi-target support) ---
    mapped_columns = []
    column_counts = {}

    for col in df.columns:
        if col in HEADER_MAPPING and col not in empty_columns:
            targets = HEADER_MAPPING[col]
            if isinstance(targets, str):
                targets = [targets]

            for std_col in targets:
                if std_col in column_counts:
                    column_counts[std_col] += 1
                    new_col_name = f"{std_col}_{column_counts[std_col]}"
                else:
                    column_counts[std_col] = 1
                    new_col_name = std_col

                mapped_columns.append(
                    pd.DataFrame({new_col_name: df[col]})
                )

    if not mapped_columns:
        st.error("❌ No valid headers detected. File not processed.")
        st.stop()

    df_mapped = pd.concat(mapped_columns, axis=1)

    # --- Add Non-Empty Custom Fields (skip None values) ---
    for cf_name in CUSTOM_FIELDS:
        if cf_name is None or not isinstance(cf_name, str):
            continue
        cf_name_upper = cf_name.strip().upper()
        if cf_name_upper in df.columns and cf_name_upper not in empty_columns:
            df_mapped[cf_name] = df[cf_name_upper]

    # --- Add computed columns ---
    computed_cols = config.get("computed_columns", {})
    for target_col, spec in computed_cols.items():
        col_type = spec.get("type")
        if col_type == "date_format":
            source = spec.get("source")
            fmt = spec.get("format")
            if source and fmt and source in df_mapped.columns:
                dt_series = pd.to_datetime(df_mapped[source], errors='coerce')
                df_mapped[target_col] = dt_series.dt.strftime(fmt).fillna('')
            else:
                df_mapped[target_col] = ''

        elif col_type == "concat":
            sources = spec.get("sources", [])
            separator = spec.get("separator", " ")
            series_list = []
            for src in sources:
                if src in df_mapped.columns:
                    series_list.append(df_mapped[src].astype(str).replace('nan', ''))
                else:
                    series_list.append(pd.Series([''] * len(df_mapped), index=df_mapped.index))
            df_mapped[target_col] = pd.Series(separator.join(filter(None, parts)) 
                                               for parts in zip(*series_list))

        elif col_type == "if_gt_zero":
            value_col = spec.get("value_column")
            date_col = spec.get("date_column")
            fmt = spec.get("format")
            if value_col and date_col and fmt and value_col in df_mapped.columns and date_col in df_mapped.columns:
                # Convert value column to numeric, coerce errors to NaN
                values = pd.to_numeric(df_mapped[value_col], errors='coerce')
                # Convert date column to datetime
                dates = pd.to_datetime(df_mapped[date_col], errors='coerce')
                # Where values > 0, format the date; else empty string
                formatted = dates.dt.strftime(fmt).where(values > 0, '')
                df_mapped[target_col] = formatted.fillna('')
            else:
                df_mapped[target_col] = ''

        else:
            # Unknown type: create empty column
            df_mapped[target_col] = ''

    # --- Cleaning Functions ---
    def clean_number(x):
        if pd.isna(x) or str(x).strip() == "":
            return ""
        try:
            return "0" + str(int(float(x)))
        except:
            return str(x).strip()

    def clean_number_no_leading_zero(x):
        if pd.isna(x) or str(x).strip() == "":
            return ""
        try:
            return str(int(float(x)))
        except:
            return str(x).strip()

    # --- Apply cleaning based on column and placement rule ---
    for col in df_mapped.columns:
        if col.startswith("accountNumber"):
            if CLEANING_RULE:
                df_mapped[col] = df_mapped[col].apply(clean_number_no_leading_zero)
            else:
                df_mapped[col] = df_mapped[col].apply(clean_number)
        elif col.startswith("phone"):
            df_mapped[col] = df_mapped[col].apply(clean_number)

    # --- Assign Team from config ---
    df_mapped["assignedTeam"] = TEAM_NAME

    # --- Ensure assignedAgent column exists ---
    if "assignedAgent" not in df_mapped.columns:
        df_mapped["assignedAgent"] = ""

    # --- Force all FINAL_COLUMN_ORDER headers to appear, even if empty ---
    final_df = pd.DataFrame(columns=FINAL_COLUMN_ORDER)
    for col in df_mapped.columns:
        if col in final_df.columns:
            final_df[col] = df_mapped[col]
    df_mapped = final_df

    # --- Display and download ---
    st.success("✅ Headers mapped successfully.")
    st.write("Returned Columns:")
    st.write(list(df_mapped.columns))
    st.dataframe(df_mapped.head())

    output_file = placement_name.replace(" ", "_") + "_TEXXEN.xlsx"
    buffer = BytesIO()
    df_mapped.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Processed File",
        data=buffer,
        file_name=output_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )