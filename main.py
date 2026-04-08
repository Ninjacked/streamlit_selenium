import streamlit as st
import pandas as pd

from db import get_mysql_config, get_mysql_connection

st.set_page_config(
    page_title="Excel Header & Consolidation Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Excel Data Management App")

st.markdown(
    """
    Welcome to the **Excel Header & Consolidation Tool** 👋  
    Use the sidebar (left side) to navigate between pages:
    - 📑 **Header Alignment** – Align column headers for consistency  
    - 📂 **File Consolidation** – Combine multiple Excel files into one  
    """
)

st.info("Select a page from the sidebar to get started.")

st.divider()
st.subheader("MySQL Query (SELECT only)")

config = get_mysql_config()
if config is None:
    st.warning(
        "MySQL is not configured. Set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, "
        "MYSQL_DATABASE, and optionally MYSQL_PORT in your .env file."
    )
else:
    default_query = "SELECT 1 AS ok;"
    query = st.text_area("SQL", value=default_query, height=120)
    run_query = st.button("Run SELECT")

    if run_query:
        if not query.strip().lower().startswith("select"):
            st.error("Only SELECT statements are allowed here.")
        else:
            try:
                conn = get_mysql_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query)
                rows = cursor.fetchall()
                cursor.close()
                conn.close()

                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True)
                else:
                    st.info("Query returned 0 rows.")
            except Exception as e:
                st.error(f"Query failed: {e}")
