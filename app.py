import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="HR Analytics, Employee Value & Attrition Financial Impact",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PROFESSIONAL DARK CORPORATE THEME (CUSTOM CSS)
st.markdown("""
<style>
    /* GLOBAL ROOT VARIABLES FOR CANVAS & SELECTION */
    :root, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        --primary-color: #38BDF8 !important;
        --accent-color: #38BDF8 !important;
    }

    .stApp {
        background: linear-gradient(135deg, rgba(5, 10, 20, 0.96), rgba(11, 19, 36, 0.94)),
                    url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Full-Width Normal Sharp Box Title (Exact same border line made into a complete box) */
    .full-width-title-bar {
        width: 100%;
        background: rgba(11, 19, 36, 0.85);
        border: 2px solid rgba(2, 132, 199, 0.5);
        border-radius: 0px !important;
        padding: 14px 20px;
        margin-bottom: 22px;
        display: flex;
        justify-content: center;
        align-items: center;
        backdrop-filter: blur(10px);
        box-shadow: none !important;
    }
    .full-width-title {
        color: #FFFFFF !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        padding: 0 !important;
        text-shadow: none !important;
    }

    /* Symmetric 5 KPI Cards */
    div[data-testid="stMetric"] {
        background: rgba(11, 19, 36, 0.85);
        border: 1.5px solid #38BDF8 !important;
        border-radius: 10px;
        padding: 14px 16px;
        min-height: 102px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4), inset 0 0 8px rgba(56, 189, 248, 0.15) !important;
        backdrop-filter: blur(10px);
        transition: all 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #38BDF8 !important;
        transform: translateY(-2px);
        box-shadow: 0 0 22px rgba(56, 189, 248, 0.7), inset 0 0 12px rgba(56, 189, 248, 0.25) !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #94A3B8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #38BDF8 !important;
        font-size: 21px !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }

    /* KPI Delta Pill Styling */
    div[data-testid="stMetricDelta"] {
        display: inline-flex !important;
        align-items: center !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
        background: rgba(185, 28, 28, 0.25) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #FCA5A5 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        width: fit-content !important;
        margin-top: 4px !important;
    }
    div[data-testid="stMetricDelta"] svg {
        display: none !important;
    }

    .section-header {
        font-size: 14.5px;
        font-weight: 700;
        color: #F1F5F9;
        margin: 24px 0 14px 0;
        display: flex;
        align-items: center;
        border-left: 4px solid #0284C7;
        padding-left: 10px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    section[data-testid="stSidebar"] {
        background-color: rgba(6, 12, 24, 0.96);
        border-right: 1px solid rgba(2, 132, 199, 0.25);
        backdrop-filter: blur(14px);
    }

    /* UPLOAD BUTTON RESIZED & ALIGNED TO 100% WIDTH */
    div[data-testid="stFileUploader"] {
        width: 100% !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stFileUploader"] section {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        min-height: unset !important;
        width: 100% !important;
    }
    div[data-testid="stFileUploader"] section > div {
        display: none !important;
    }
    div[data-testid="stFileUploader"] small {
        display: none !important;
    }
    div[data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        width: 100% !important;
        display: block !important;
    }
    
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploaderDropzone"] [role="button"],
    div[data-testid="stFileUploader"] button {
        background: transparent !important;
        border: 1.5px solid rgba(56, 189, 248, 0.45) !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-sizing: border-box !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 0 6px rgba(56, 189, 248, 0.15) !important;
    }
    div[data-testid="stFileUploaderDropzone"] button:hover,
    div[data-testid="stFileUploaderDropzone"] [role="button"]:hover,
    div[data-testid="stFileUploader"] button:hover {
        background: rgba(56, 189, 248, 0.05) !important;
        border: 1.5px solid #38BDF8 !important;
        color: #38BDF8 !important;
        box-shadow: 
            0 0 14px rgba(56, 189, 248, 0.8),
            inset 0 0 8px rgba(56, 189, 248, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* CUSTOM AUDIT TABLE */
    .custom-audit-container {
        width: 100%;
        overflow-x: auto;
        border: 1.5px solid rgba(56, 189, 248, 0.35);
        border-radius: 8px;
        background: rgba(9, 16, 32, 0.85);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
        margin-top: 8px;
    }
    .custom-audit-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: #E2E8F0;
        table-layout: auto;
    }
    .custom-audit-table th {
        background: rgba(15, 23, 42, 0.95);
        color: #94A3B8;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 11.5px;
        padding: 12px 14px;
        text-align: center !important;
        vertical-align: middle !important;
        border-bottom: 1.5px solid rgba(56, 189, 248, 0.3);
    }
    .custom-audit-table td {
        padding: 11px 14px;
        text-align: center !important;
        vertical-align: middle !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.2s ease;
        user-select: text;
    }
    .custom-audit-table tr:hover td {
        background: rgba(56, 189, 248, 0.04);
    }
    .custom-audit-table td:hover,
    .custom-audit-table td:focus,
    .custom-audit-table td:active {
        outline: none !important;
        border: 1.5px solid #38BDF8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.8), inset 0 0 6px rgba(56, 189, 248, 0.2) !important;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# 3. SCHEMA-AGNOSTIC MULTI-FORMAT FILE UPLOADER
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

st.sidebar.markdown("### Enterprise Data Gateway")
uploaded_file = st.sidebar.file_uploader(
    "Upload Workforce Records (CSV / Excel)",
    type=["csv", "xlsx", "xls"],
    key=f"uploader_{st.session_state['uploader_key']}",
    label_visibility="visible"
)

# File aate hi Return / Reset button display hoga
if uploaded_file is not None:
    if st.sidebar.button("↩ Return to Default Dashboard"):
        st.session_state["uploader_key"] += 1
        st.rerun()

def find_matching_column(columns, candidates):
    cols_clean = {c.lower().replace("_", "").replace(" ", ""): c for c in columns}
    for cand in candidates:
        cand_clean = cand.lower().replace("_", "").replace(" ", "")
        if cand_clean in cols_clean:
            return cols_clean[cand_clean]
    for c_clean, orig in cols_clean.items():
        for cand in candidates:
            if cand.lower() in c_clean:
                return orig
    return None

# 4. ROBUST DATA PROCESSING PIPELINE
@st.cache_data
def load_and_process_data(file_bytes, file_name):
    if file_bytes is not None:
        if file_name.endswith((".xlsx", ".xls")):
            raw_df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raw_df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        raw_df = pd.read_csv("HR_Analytics.csv")

    df = raw_df.copy()

    salary_col = find_matching_column(df.columns, ["MonthlyIncome", "MonthlySalary", "Salary", "CTC", "Income", "Pay"])
    attrition_col = find_matching_column(df.columns, ["Attrition", "Left", "Status", "Exit", "Churn", "Turnover"])
    dept_col = find_matching_column(df.columns, ["Department", "Dept", "Division", "Unit", "BusinessUnit"])
    role_col = find_matching_column(df.columns, ["JobRole", "Role", "Designation", "Title", "Position"])
    rating_col = find_matching_column(df.columns, ["PerformanceRating", "Rating", "Appraisal", "Performance", "Score"])
    overtime_col = find_matching_column(df.columns, ["OverTime", "OT", "ExtraHours"])
    age_col = find_matching_column(df.columns, ["Age", "EmployeeAge"])
    gender_col = find_matching_column(df.columns, ["Gender", "Sex"])

    if attrition_col:
        attr_map = {
            1: "Yes", "1": "Yes", True: "Yes", "true": "Yes", "yes": "Yes", "left": "Yes", "resigned": "Yes",
            0: "No", "0": "No", False: "No", "false": "No", "no": "No", "stayed": "No", "active": "No"
        }
        df["Attrition"] = df[attrition_col].astype(str).str.strip().str.lower().map(lambda x: attr_map.get(x, "No"))
    else:
        df["Attrition"] = "No"

    if salary_col:
        if df[salary_col].dtype == object:
            df["Monthly_Salary_INR"] = df[salary_col].astype(str).str.replace(r"[₹$,]", "", regex=True)
            df["Monthly_Salary_INR"] = pd.to_numeric(df["Monthly_Salary_INR"], errors="coerce").fillna(50000.0)
        else:
            df["Monthly_Salary_INR"] = pd.to_numeric(df[salary_col], errors="coerce").fillna(50000.0)
        
        if df["Monthly_Salary_INR"].mean() < 30000:
            df["Monthly_Salary_INR"] = df["Monthly_Salary_INR"] * 83.0
    else:
        df["Monthly_Salary_INR"] = 50000.0

    perf_multiplier = {1: 2.5, 2: 2.8, 3: 3.2, 4: 4.0}
    if rating_col:
        df["PerformanceRating"] = pd.to_numeric(df[rating_col], errors="coerce").fillna(3).astype(int)
        df["Perf_Mult"] = df["PerformanceRating"].map(perf_multiplier).fillna(3.0)
    else:
        df["PerformanceRating"] = 3
        df["Perf_Mult"] = 3.0

    df["Department"] = df[dept_col].astype(str).fillna("General") if dept_col else "General"
    df["JobRole"] = df[role_col].astype(str).fillna("Associate") if role_col else "Associate"
    df["OverTime"] = df[overtime_col].astype(str).fillna("No") if overtime_col else "No"
    df["Age"] = pd.to_numeric(df[age_col], errors="coerce").fillna(30) if age_col else 30
    df["Gender"] = df[gender_col].astype(str).fillna("Unspecified") if gender_col else "Unspecified"

    df["Annual_Salary_INR"] = df["Monthly_Salary_INR"] * 12
    df["Estimated_Revenue_INR"] = df["Annual_Salary_INR"] * df["Perf_Mult"]
    df["Replacement_Cost_INR"] = df["Annual_Salary_INR"] * 0.25
    df["Vacancy_Loss_INR"] = df["Estimated_Revenue_INR"] * (3.0 / 12.0)
    df["Total_Attrition_Loss_INR"] = df["Replacement_Cost_INR"] + df["Vacancy_Loss_INR"]

    try:
        df["Salary_Band"] = pd.qcut(df["Monthly_Salary_INR"] / 1e5, q=5, labels=["Entry Tier", "Junior Tier", "Mid Tier", "Senior Tier", "Executive Tier"])
    except ValueError:
        df["Salary_Band"] = "Standard Tier"

    return df

file_bytes = uploaded_file.read() if uploaded_file else None
file_name = uploaded_file.name if uploaded_file else "HR_Analytics.csv"

try:
    df = load_and_process_data(file_bytes, file_name)
except Exception as e:
    st.error(f"Error initializing data gateway: {e}")
    st.stop()

# 5. DYNAMIC SIDEBAR FILTERS
st.sidebar.markdown("### Workforce Slicing")

dept_list = sorted(df["Department"].dropna().unique().tolist())
selected_dept = st.sidebar.multiselect("Department", dept_list, default=dept_list) if dept_list else []

role_list = sorted(df["JobRole"].dropna().unique().tolist())
selected_role = st.sidebar.multiselect("Designation", role_list, default=role_list) if role_list else []

gender_list = sorted(df["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.multiselect("Gender", gender_list, default=gender_list) if gender_list else []

filtered_df = df.copy()
if dept_list and selected_dept:
    filtered_df = filtered_df[filtered_df["Department"].isin(selected_dept)]
if role_list and selected_role:
    filtered_df = filtered_df[filtered_df["JobRole"].isin(selected_role)]
if gender_list and selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]

# 6. FULL-PAGE WIDTH SHARP BOX TITLE (EXACT SAME LINE COLOR, NO GLOW)
st.markdown("""
<div class="full-width-title-bar">
    <div class="full-width-title">HR Analytics, Employee Value & Attrition Financial Impact</div>
</div>
""", unsafe_allow_html=True)

# 7. EXECUTIVE KPI METRICS
total_emp = len(filtered_df)
attrition_df = filtered_df[filtered_df["Attrition"] == "Yes"]
attrition_count = len(attrition_df)
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0

total_revenue_cr = (filtered_df["Estimated_Revenue_INR"].sum() / 1e7) / 83.0
total_loss_cr = (filtered_df["Total_Attrition_Loss_INR"].sum() / 1e7) / 83.0
avg_loss_lakh = (filtered_df["Total_Attrition_Loss_INR"].mean() / 1e5) / 83.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Active Workforce", f"{total_emp:,}")
k2.metric("Turnover Volume", f"{attrition_count}", delta=f"{attrition_rate:.1f}% Turnover")
k3.metric("Annual Value Created", f"₹{total_revenue_cr:.2f} Cr")
k4.metric("Attrition Risk Exposure", f"₹{total_loss_cr:.2f} Cr", delta="Direct Exposure")
k5.metric("Avg Financial Loss / Exit", f"₹{avg_loss_lakh:.2f} L")

# DARK THEME PLOTLY LAYOUT
plotly_layout = dict(
    paper_bgcolor='rgba(9, 16, 32, 0.85)',
    plot_bgcolor='rgba(9, 16, 32, 0.85)',
    font=dict(color="#CBD5E1", family="Inter", size=11),
    margin=dict(l=25, r=25, t=50, b=30),
    xaxis=dict(gridcolor="rgba(255, 255, 255, 0.08)"),
    yaxis=dict(gridcolor="rgba(255, 255, 255, 0.08)"),
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="right",
        x=1.18,
        bgcolor="rgba(0,0,0,0)"
    )
)

COLOR_DARK_BLUE = "#1D4ED8"     
COLOR_DARK_CRIMSON = "#B91C1C"  

# SECTION 1: FINANCIAL RISK CHARTS (BALANCED 50-50 SYMMETRIC COLUMNS)
st.markdown("<div class='section-header'>Talent Valuation & Enterprise Exposure Modeling</div>", unsafe_allow_html=True)
c_fin1, c_fin2 = st.columns(2, gap="medium")

with c_fin1:
    tier_summary = filtered_df.groupby(["Salary_Band", "Attrition"], observed=False)["Total_Attrition_Loss_INR"].mean().reset_index()
    tier_summary["Loss_Lakh"] = (tier_summary["Total_Attrition_Loss_INR"] / 1e5) / 83.0
    
    fig_tier = px.bar(
        tier_summary,
        x="Salary_Band",
        y="Loss_Lakh",
        color="Attrition",
        barmode="group",
        title="Avg Exit Loss Exposure Across Salary Tiers (Lakhs)",
        color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON},
        labels={
            "Salary_Band": "Workforce Compensation Band",
            "Loss_Lakh": "Avg Loss Exposure (Lakhs)",
            "Attrition": "Attrition Status"
        }
    )
    fig_tier.update_layout(
        **plotly_layout,
        title=dict(text="Avg Exit Loss Exposure Across Salary Tiers", x=0.01, y=0.96),
        height=380
    )
    st.plotly_chart(fig_tier, use_container_width=True)

with c_fin2:
    dept_fin = filtered_df.groupby("Department")[["Estimated_Revenue_INR", "Total_Attrition_Loss_INR"]].sum().reset_index()
    fig_bar = go.Figure(data=[
        go.Bar(
            name='Revenue (Cr)',
            x=dept_fin['Department'],
            y=(dept_fin['Estimated_Revenue_INR'] / 1e7) / 83.0,
            marker_color=COLOR_DARK_BLUE
        ),
        go.Bar(
            name='Loss Risk (Cr)',
            x=dept_fin['Department'],
            y=(dept_fin['Total_Attrition_Loss_INR'] / 1e7) / 83.0,
            marker_color=COLOR_DARK_CRIMSON
        )
    ])
    fig_bar.update_layout(
        **plotly_layout,
        barmode='group',
        title=dict(text="Department Revenue vs Loss Exposure", x=0.01, y=0.96),
        height=380
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# SECTION 2: WORKFORCE DEMOGRAPHICS & ATTRITION DRIVERS (CHARTS 3 & 4)
st.markdown("<div class='section-header'>Operational Demographics & Behavioral Flight Drivers</div>", unsafe_allow_html=True)
c_demo1, c_demo2 = st.columns(2, gap="medium")

with c_demo1:
    fig_dept = px.histogram(
        filtered_df, x="Department", color="Attrition",
        barmode="group", title="Attrition Density by Department",
        color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON}
    )
    fig_dept.update_layout(
        **plotly_layout,
        title=dict(text="Attrition Density by Department", x=0.01, y=0.96),
        height=360
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with c_demo2:
    if len(attrition_df) > 0:
        fig_ot = px.pie(
            attrition_df, names="OverTime",
            title="Attrition Impact Driven by Shift Overtime",
            hole=0.55,
            color="OverTime",
            color_discrete_map={"Yes": "#991B1B", "No": "#0284C7"}  
        )
        fig_ot.update_traces(
            marker=dict(line=dict(color='#0B1324', width=2.5)),
            textfont=dict(color='#FFFFFF', size=12, family="Inter")
        )
        fig_ot.update_layout(
            **plotly_layout,
            title=dict(text="Attrition Impact Driven by Shift Overtime", x=0.01, y=0.96),
            height=360
        )
        st.plotly_chart(fig_ot, use_container_width=True)
    else:
        st.info("No attrition events recorded in filtered scope.")

# SECTION 3: COMPENSATION SPREAD & AGE DISTRIBUTION (CHARTS 5 & 6)
st.markdown("<div class='section-header'>Compensation Spread & Age Distribution Analysis</div>", unsafe_allow_html=True)
c_comp1, c_comp2 = st.columns(2, gap="medium")

with c_comp1:
    fig_salary = px.box(
        filtered_df, x="JobRole", y=(filtered_df["Monthly_Salary_INR"] / 1e5) / 83.0,
        color="Attrition",
        title="Salary Distribution Across Designations (₹ Lakhs)",
        color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON},
        labels={"y": "Monthly Salary (Lakhs)", "JobRole": "Designation"}
    )
    fig_salary.update_layout(
        **plotly_layout,
        title=dict(text="Salary Distribution Across Designations (Lakhs)", x=0.01, y=0.96),
        xaxis_tickangle=-40,
        height=380
    )
    st.plotly_chart(fig_salary, use_container_width=True)

with c_comp2:
    fig_age = px.histogram(
        filtered_df, x="Age", color="Attrition",
        barmode="group",
        nbins=18,
        title="Workforce Age Demographics vs Attrition",
        color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON},
        labels={"count": "Headcount", "Age": "Employee Age (Years)"}
    )
    fig_age.update_layout(
        **plotly_layout,
        title=dict(text="Workforce Age Demographics vs Attrition", x=0.01, y=0.96),
        height=380
    )
    st.plotly_chart(fig_age, use_container_width=True)

# SECTION 4: AUDIT TABLE (CENTER-ALIGNED WITH GLOWING NEO-BLUE SELECTION)
st.markdown("<div class='section-header'>Critical High-Value Personnel Audit Table</div>", unsafe_allow_html=True)

audit_cols = [c for c in ["Department", "JobRole", "Monthly_Salary_INR", "PerformanceRating", "Estimated_Revenue_INR", "Total_Attrition_Loss_INR", "Attrition"] if c in filtered_df.columns]
if audit_cols:
    audit_table = filtered_df[audit_cols].sort_values("Total_Attrition_Loss_INR", ascending=False).head(10).copy()
    
    audit_table["Monthly_Salary_INR"] = audit_table["Monthly_Salary_INR"].apply(lambda x: f"₹{x:,.0f}")
    audit_table["Estimated_Revenue_INR"] = audit_table["Estimated_Revenue_INR"].apply(lambda x: f"₹{x:,.0f}")
    audit_table["Total_Attrition_Loss_INR"] = audit_table["Total_Attrition_Loss_INR"].apply(lambda x: f"₹{x:,.0f}")
    
    audit_table.rename(columns={
        "Department": "Department",
        "JobRole": "Designation",
        "Monthly_Salary_INR": "Monthly Salary",
        "PerformanceRating": "Appraisal Score",
        "Estimated_Revenue_INR": "Annual Revenue Contribution",
        "Total_Attrition_Loss_INR": "Attrition Loss Risk",
        "Attrition": "Attrition Status"
    }, inplace=True)
    
    table_headers = "".join([f"<th>{col}</th>" for col in audit_table.columns])
    table_rows = ""
    for _, row in audit_table.iterrows():
        row_cells = "".join([f"<td tabindex='0'>{val}</td>" for val in row])
        table_rows += f"<tr>{row_cells}</tr>"
        
    html_table = f"""
    <div class="custom-audit-container">
        <table class="custom-audit-table">
            <thead>
                <tr>{table_headers}</tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)
