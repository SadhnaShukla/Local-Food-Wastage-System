# app.py  — Local Food Wastage Management System
# Works with your schema shown in setup_database.py:
# providers(Provider_ID, Name, Type, Address, City, Contact)
# receivers(Receiver_ID, Name, Type, City, Contact)
# food_listings(Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location)
# claims(Claim_ID, Food_ID, Receiver_ID, Claim_Date, Status)   # if present

import sqlite3
import pandas as pd
import streamlit as st
import altair as alt
from datetime import date

DB_PATH =  "database/food_wastage.db"

# ---------- DB helpers ----------
def run_query(query: str, params: tuple | None = None) -> pd.DataFrame:
    """Return a DataFrame or empty DataFrame on any error."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.info(f"ℹ️ {e}")
        return pd.DataFrame()

def exec_query(query: str, params: tuple | None = None) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ {e}")
        return False

def table_exists(name: str) -> bool:
    q = "SELECT name FROM sqlite_master WHERE type='table' AND lower(name)=lower(?);"
    return not run_query(q, (name,)).empty

# ---------- UI helpers ----------
def kpi(label: str, value):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.metric(label, value)

def chart_or_msg(df: pd.DataFrame, chart_fn, *args, **kwargs):
    if df is None or df.empty:
        st.warning("No data available.")
    else:
        chart_fn(df, *args, **kwargs)

# ---------- DASHBOARD ----------
def dashboard():
    st.title("Local Food Wastage Management System")
    st.header("Local Food Wastage Dashboard")

    # KPIs
    total_providers = run_query("SELECT COUNT(*) AS cnt FROM providers;") if table_exists("providers") else pd.DataFrame([{"cnt": 0}])
    total_receivers = run_query("SELECT COUNT(*) AS cnt FROM receivers;") if table_exists("receivers") else pd.DataFrame([{"cnt": 0}])
    total_listings  = run_query("SELECT COUNT(*) AS cnt FROM food_listings;") if table_exists("food_listings") else pd.DataFrame([{"cnt": 0}])
    total_claims    = run_query("SELECT COUNT(*) AS cnt FROM claims;") if table_exists("claims") else pd.DataFrame([{"cnt": 0}])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Providers", int(total_providers.iloc[0,0]))
    with c2: st.metric("Total Receivers", int(total_receivers.iloc[0,0]))
    with c3: st.metric("Total Food Listings", int(total_listings.iloc[0,0]))
    with c4: st.metric("Total Claims", int(total_claims.iloc[0,0]))

    st.subheader("Top 5 Providers by Donations")
    top5 = run_query("""
        SELECT p.Name AS Provider, COUNT(f.Food_ID) AS Donations
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Provider_ID, p.Name
        ORDER BY Donations DESC
        LIMIT 5;
    """) if table_exists("providers") and table_exists("food_listings") else pd.DataFrame()
    if not top5.empty:
        st.altair_chart(
            alt.Chart(top5).mark_bar().encode(
                x=alt.X("Provider:N", sort="-y"),
                y=alt.Y("Donations:Q")
            ).properties(height=300),
            use_container_width=True
        )
    else:
        st.warning("No provider/listing data.")

    st.subheader("Claims by Status")
    claims_by_status = run_query("""
        SELECT Status, COUNT(*) AS Count
        FROM claims
        GROUP BY Status;
    """) if table_exists("claims") else pd.DataFrame()
    if not claims_by_status.empty:
        st.altair_chart(
            alt.Chart(claims_by_status).mark_arc(innerRadius=60).encode(
                theta="Count:Q", color="Status:N"
            ).properties(height=280),
            use_container_width=True
        )
    else:
        st.info("No claims data.")

    st.subheader("Available vs Expired Food")
    avail_vs_exp = run_query("""
        SELECT 
            CASE WHEN DATE(Expiry_Date) >= DATE('now') THEN 'Available' ELSE 'Expired' END AS Food_Status,
            COUNT(*) AS Count
        FROM food_listings
        GROUP BY Food_Status;
    """) if table_exists("food_listings") else pd.DataFrame()
    if not avail_vs_exp.empty:
        st.altair_chart(
            alt.Chart(avail_vs_exp).mark_bar().encode(
                x="Food_Status:N", y="Count:Q"
            ).properties(height=300),
            use_container_width=True
        )
    else:
        st.info("No food listings data.")

    st.subheader("Food Listings by Provider Type")
    by_type = run_query("""
        SELECT COALESCE(Provider_Type,'Unknown') AS Provider_Type, COUNT(*) AS Count
        FROM food_listings
        GROUP BY Provider_Type;
    """) if table_exists("food_listings") else pd.DataFrame()
    if not by_type.empty:
        st.altair_chart(
            alt.Chart(by_type).mark_bar().encode(
                x=alt.X("Provider_Type:N", sort="-y"),
                y="Count:Q"
            ).properties(height=300),
            use_container_width=True
        )

    st.subheader("Monthly Claims Trend")
    monthly = run_query("""
        SELECT strftime('%Y-%m', DATE(Claim_Date)) AS Month, COUNT(*) AS Count
        FROM claims
        GROUP BY Month
        ORDER BY Month;
    """) if table_exists("claims") else pd.DataFrame()
    if not monthly.empty:
        st.altair_chart(
            alt.Chart(monthly).mark_line(point=True).encode(
                x="Month:T", y="Count:Q"
            ).properties(height=300),
            use_container_width=True
        )

    st.subheader("Most Claimed Food Items (Top 5)")
    most_claimed = run_query("""
        SELECT f.Food_Name AS Food, COUNT(c.Claim_ID) AS Claim_Count
        FROM food_listings f
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Food_Name
        ORDER BY Claim_Count DESC
        LIMIT 5;
    """) if table_exists("food_listings") and table_exists("claims") else pd.DataFrame()
    if not most_claimed.empty:
        st.altair_chart(
            alt.Chart(most_claimed).mark_bar().encode(
                x=alt.X("Food:N", sort="-y"),
                y="Claim_Count:Q"
            ).properties(height=300),
            use_container_width=True
        )

    st.subheader("Claims per Provider")
    claims_per_provider = run_query("""
        SELECT p.Name AS Provider, COUNT(c.Claim_ID) AS Total_Claims
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY p.Name
        ORDER BY Total_Claims DESC;
    """) if table_exists("providers") and table_exists("food_listings") and table_exists("claims") else pd.DataFrame()
    if not claims_per_provider.empty:
        st.dataframe(claims_per_provider, use_container_width=True)

    st.subheader("Food Expiring in Next 7 Days")
    next7 = run_query("""
        SELECT Food_ID, Food_Name, Quantity, DATE(Expiry_Date) AS Expiry_Date
        FROM food_listings
        WHERE DATE(Expiry_Date) BETWEEN DATE('now') AND DATE('now','+7 day')
        ORDER BY DATE(Expiry_Date);
    """) if table_exists("food_listings") else pd.DataFrame()
    st.dataframe(next7, use_container_width=True)

    st.subheader("Unclaimed Food")
    unclaimed = run_query("""
        SELECT f.Food_ID, f.Food_Name, f.Provider_Type, DATE(f.Expiry_Date) AS Expiry_Date
        FROM food_listings f
        LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Claim_ID IS NULL
        ORDER BY DATE(f.Expiry_Date);
    """) if table_exists("food_listings") else pd.DataFrame()
    st.dataframe(unclaimed, use_container_width=True)

# ---------- CRUD ----------
def crud():
    st.header("Manage Data (CRUD)")

    tab1, tab2, tab3 = st.tabs(["Providers", "Receivers", "Food Listings"])

    # --- Providers ---
    with tab1:
        st.subheader("Add Provider")
        with st.form("add_provider"):
            name = st.text_input("Name")
            ptype = st.text_input("Type")
            addr = st.text_input("Address")
            city = st.text_input("City")
            contact = st.text_input("Contact")
            submitted = st.form_submit_button("Add Provider")
            if submitted:
                ok = exec_query(
                    "INSERT INTO providers (Name, Type, Address, City, Contact) VALUES (?, ?, ?, ?, ?);",
                    (name, ptype, addr, city, contact)
                )
                if ok: st.success("Provider added.")

        st.subheader("Providers (table)")
        st.dataframe(run_query("SELECT * FROM providers;") if table_exists("providers") else pd.DataFrame(),
                     use_container_width=True)

    # --- Receivers ---
    with tab2:
        st.subheader("Add Receiver")
        with st.form("add_receiver"):
            name = st.text_input("Name", key="rname")
            rtype = st.text_input("Type", key="rtype")
            city = st.text_input("City", key="rcity")
            contact = st.text_input("Contact", key="rcontact")
            submitted = st.form_submit_button("Add Receiver")
            if submitted:
                ok = exec_query(
                    "INSERT INTO receivers (Name, Type, City, Contact) VALUES (?, ?, ?, ?);",
                    (name, rtype, city, contact)
                )
                if ok: st.success("Receiver added.")

        st.subheader("Receivers (table)")
        st.dataframe(run_query("SELECT * FROM receivers;") if table_exists("receivers") else pd.DataFrame(),
                     use_container_width=True)

    # --- Food Listings ---
    with tab3:
        st.subheader("Add Food Listing")
        providers_df = run_query("SELECT Provider_ID, Name FROM providers;") if table_exists("providers") else pd.DataFrame()
        provider_map = {row["Name"]: int(row["Provider_ID"]) for _, row in providers_df.iterrows()} if not providers_df.empty else {}

        with st.form("add_food"):
            food_name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=0, step=1)
            exp = st.date_input("Expiry Date", value=date.today())
            provider_name = st.selectbox("Provider", list(provider_map.keys()) or ["-- no providers --"])
            ptype = st.text_input("Provider Type")
            loc = st.text_input("Location")
            submitted = st.form_submit_button("Add Food")
            if submitted and provider_map:
                ok = exec_query(
                    "INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location) VALUES (?, ?, ?, ?, ?, ?);",
                    (food_name, int(qty), str(exp), provider_map[provider_name], ptype, loc)
                )
                if ok: st.success("Food listing added.")
            elif submitted:
                st.error("Add a provider first.")

        st.subheader("Update Food Listing")
        listings = run_query("SELECT Food_ID, Food_Name, Quantity, DATE(Expiry_Date) AS Expiry_Date FROM food_listings;") if table_exists("food_listings") else pd.DataFrame()
        if listings.empty:
            st.info("No listings to update.")
        else:
            row = st.selectbox("Choose item", listings.apply(lambda r: f"{r.Food_ID} – {r.Food_Name}", axis=1))
            selected_id = int(row.split(" – ")[0])
            new_qty = st.number_input("New Quantity", min_value=0, step=1)
            new_date = st.date_input("New Expiry Date", value=date.today())
            if st.button("Save Update"):
                ok = exec_query("UPDATE food_listings SET Quantity=?, Expiry_Date=? WHERE Food_ID=?;",
                                (int(new_qty), str(new_date), selected_id))
                if ok: st.success("Updated.")

        st.subheader("Delete Food Listing")
        listings2 = run_query("SELECT Food_ID, Food_Name FROM food_listings;") if table_exists("food_listings") else pd.DataFrame()
        if listings2.empty:
            st.info("No listings to delete.")
        else:
            row2 = st.selectbox("Select to delete", listings2.apply(lambda r: f"{r.Food_ID} – {r.Food_Name}", axis=1), key="del")
            del_id = int(row2.split(" – ")[0])
            if st.button("Delete"):
                ok = exec_query("DELETE FROM food_listings WHERE Food_ID=?;", (del_id,))
                if ok: st.success("Deleted.")

# ---------- Insights ----------
def insights():
    st.header("Business Insights")
    # % unclaimed
    total_items = run_query("SELECT COUNT(*) AS c FROM food_listings;") if table_exists("food_listings") else pd.DataFrame([{"c":0}])
    unclaimed = run_query("""
        SELECT COUNT(*) AS c
        FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Claim_ID IS NULL;
    """) if table_exists("food_listings") else pd.DataFrame([{"c":0}])
    t = int(total_items.iloc[0,0]) if not total_items.empty else 0
    u = int(unclaimed.iloc[0,0]) if not unclaimed.empty else 0
    pct = round((u/t)*100, 2) if t else 0.0
    st.metric("% Unclaimed Food", f"{pct}%")

    # Most waste-prone provider type (expired items)
    waste = run_query("""
        SELECT COALESCE(Provider_Type,'Unknown') AS Provider_Type, COUNT(*) AS Expired_Items
        FROM food_listings
        WHERE DATE(Expiry_Date) < DATE('now')
        GROUP BY Provider_Type
        ORDER BY Expired_Items DESC;
    """) if table_exists("food_listings") else pd.DataFrame()
    if not waste.empty:
        st.altair_chart(
            alt.Chart(waste).mark_bar().encode(
                x=alt.X("Provider_Type:N", sort="-y"),
                y="Expired_Items:Q"
            ).properties(height=300),
            use_container_width=True
        )
    st.dataframe(waste, use_container_width=True)

# ---------- App ----------
st.set_page_config(page_title="Local Food Wastage", layout="wide")
with st.sidebar:
    st.image("https://static.streamlit.io/examples/cat.jpg", caption="Local Food Wastage")
    page = st.radio("Navigate", ["Dashboard", "CRUD", "Insights"])

if page == "Dashboard":
    dashboard()
elif page == "CRUD":
    crud()
else:
    insights()

df_monthly = run_query("""
    SELECT 
      CASE 
        WHEN instr(Timestamp,'-') > 0 
          THEN substr(Timestamp,7,4) || '-' || substr(Timestamp,1,2)
        WHEN instr(Timestamp,'/') > 0 
          THEN substr(Timestamp,-4) || '-' || printf('%02d', CAST(substr(Timestamp,1,instr(Timestamp,'/')-1) AS INT))
        ELSE 'Unknown'
      END AS Month,
      COUNT(*) AS Count
    FROM claims
    GROUP BY Month
    ORDER BY Month;
""")


