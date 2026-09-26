import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
    .stApp {
        background: linear-gradient(135deg, rgba(5, 10, 20, 0.96), rgba(11, 19, 36, 0.94)),
                    url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #E2E8F0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Full-Width Page-Spanning Title */
    .full-width-title-bar {
        width: 100%;
        padding: 14px 0px 18px 0px;
        margin-bottom: 22px;
        border-bottom: 2px solid rgba(2, 132, 199, 0.5);
        box-shadow: 0 4px 15px -4px rgba(2, 132, 199, 0.35);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .full-width-title {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        padding: 0 !important;
        text-shadow: 0 0 12px rgba(2, 132, 199, 0.6), 0 0 24px rgba(3, 105, 161, 0.3);
    }

    /* Symmetric 5 KPI Cards */
    div[data-testid="stMetric"] {
        background: rgba(11, 19, 36, 0.85);
        border: 1px solid rgba(2, 132, 199, 0.35);
        border-radius: 8px;
        padding: 14px 16px;
        min-height: 102px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(10px);
        transition: all 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #0284C7;
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(2, 132, 199, 0.3);
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

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(2, 132, 199, 0.25);
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR FILE UPLOADER (DUAL-MODE)
st.sidebar.markdown("### Data Management")
uploaded_file = st.sidebar.file_uploader(
    "Upload Workforce CSV File",
    type=["csv"],
    help="Upload enterprise organizational records or continue with default data."
)

# 4. DATA PROCESSING WITH NORMALIZED INR VALUES
@st.cache_data
def load_and_process_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("HR_Analytics.csv")

    perf_multiplier = {1: 2.5, 2: 2.8, 3: 3.2, 4: 4.0}
    if "PerformanceRating" in df.columns:
        df["Perf_Mult"] = df["PerformanceRating"].map(perf_multiplier).fillna(3.0)
    else:
        df["Perf_Mult"] = 3.0

    # Monthly salary calculations in ₹
    if "MonthlyIncome" in df.columns:
        df["Monthly_Salary_INR"] = df["MonthlyIncome"] * 83.0
        # Normalizing base to realistic scale
        df["Annual_Salary_INR"] = df["Monthly_Salary_INR"] * 12
    else:
        df["Monthly_Salary_INR"] = 50000.0
        df["Annual_Salary_INR"] = 600000.0

    df["Estimated_Revenue_INR"] = df["Annual_Salary_INR"] * df["Perf_Mult"]
    df["Replacement_Cost_INR"] = df["Annual_Salary_INR"] * 0.25
    df["Vacancy_Loss_INR"] = df["Estimated_Revenue_INR"] * (3.0 / 12.0)
    df["Total_Attrition_Loss_INR"] = df["Replacement_Cost_INR"] + df["Vacancy_Loss_INR"]

    df["Salary_Band"] = pd.qcut(df["Monthly_Salary_INR"] / 1e5, q=5, labels=["Entry Tier", "Junior Tier", "Mid Tier", "Senior Tier", "Executive Tier"])

    return df

try:
    df = load_and_process_data(uploaded_file)
except Exception as e:
    st.error(f"Error initializing data pipeline: {e}")
    st.stop()

# 5. SIDEBAR FILTERS
st.sidebar.markdown("### Workforce Slicing")

dept_list = sorted(df["Department"].dropna().unique().tolist()) if "Department" in df.columns else []
selected_dept = st.sidebar.multiselect("Department", dept_list, default=dept_list) if dept_list else []

role_list = sorted(df["JobRole"].dropna().unique().tolist()) if "JobRole" in df.columns else []
selected_role = st.sidebar.multiselect("Designation", role_list, default=role_list) if role_list else []

gender_list = sorted(df["Gender"].dropna().unique().tolist()) if "Gender" in df.columns else []
selected_gender = st.sidebar.multiselect("Gender", gender_list, default=gender_list) if gender_list else []

filtered_df = df.copy()
if dept_list and selected_dept:
    filtered_df = filtered_df[filtered_df["Department"].isin(selected_dept)]
if role_list and selected_role:
    filtered_df = filtered_df[filtered_df["JobRole"].isin(selected_role)]
if gender_list and selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]

# 6. FULL-PAGE WIDTH GLOWING TITLE
st.markdown("""
<div class="full-width-title-bar">
    <div class="full-width-title">HR Analytics, Employee Value & Attrition Financial Impact</div>
</div>
""", unsafe_allow_html=True)

# 7. EXECUTIVE KPI METRICS (CORRECT SCALED VALUES)
total_emp = len(filtered_df)
attrition_df = filtered_df[filtered_df["Attrition"] == "Yes"] if "Attrition" in filtered_df.columns else pd.DataFrame()
attrition_count = len(attrition_df)
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0

total_revenue_cr = (filtered_df["Estimated_Revenue_INR"].sum() / 1e7) / 83.0
total_loss_cr = (filtered_df["Total_Attrition_Loss_INR"].sum() / 1e7) / 83.0
avg_loss_lakh = (filtered_df["Total_Attrition_Loss_INR"].mean() / 1e5) / 83.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Active Workforce", f"{total_emp:,}")
k2.metric("Turnover Volume", f"{attrition_count}", f"{attrition_rate:.1f}% rate", delta_color="inverse")
k3.metric("Annual Value Created", f"₹{total_revenue_cr:.2f} Cr")
k4.metric("Attrition Risk Exposure", f"₹{total_loss_cr:.2f} Cr", delta="-Risk Exposure", delta_color="inverse")
k5.metric("Avg Financial Loss / Exit", f"₹{avg_loss_lakh:.2f} L")

# DARK THEME PLOTLY LAYOUT
plotly_layout = dict(
    paper_bgcolor='rgba(9, 16, 32, 0.85)',
    plot_bgcolor='rgba(9, 16, 32, 0.85)',
    font=dict(color="#CBD5E1", family="Inter", size=11),
    margin=dict(l=35, r=35, t=50, b=35),
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

# DEEP DARK THEME COLOR PALETTE
COLOR_DARK_BLUE = "#1D4ED8"     
COLOR_DARK_CRIMSON = "#B91C1C"  

# SECTION 1: FINANCIAL RISK CHARTS (CHARTS 1 & 2)
st.markdown("<div class='section-header'>Talent Valuation & Enterprise Exposure Modeling</div>", unsafe_allow_html=True)
c_fin1, c_fin2 = st.columns([1.25, 1], gap="medium")

with c_fin1:
    # CHART 1: Average Exit Loss Exposure Across Salary Tiers
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
        title=dict(text="Avg Exit Loss Exposure Across Salary Tiers", x=0.02, y=0.96),
        height=390
    )
    st.plotly_chart(fig_tier, use_container_width=True)

with c_fin2:
    # CHART 2: Department Revenue vs Loss Exposure
    if "Department" in filtered_df.columns:
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
            title=dict(text="Department Revenue vs Loss Exposure", x=0.02, y=0.96),
            height=390
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# SECTION 2: WORKFORCE DEMOGRAPHICS & ATTRITION DRIVERS (CHARTS 3 & 4)
st.markdown("<div class='section-header'>Operational Demographics & Behavioral Flight Drivers</div>", unsafe_allow_html=True)
c_demo1, c_demo2 = st.columns(2, gap="medium")

with c_demo1:
    # CHART 3: Attrition Density by Department
    if "Department" in filtered_df.columns and "Attrition" in filtered_df.columns:
        fig_dept = px.histogram(
            filtered_df, x="Department", color="Attrition",
            barmode="group", title="Attrition Density by Department",
            color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON}
        )
        fig_dept.update_layout(
            **plotly_layout,
            title=dict(text="Attrition Density by Department", x=0.02, y=0.96),
            height=360
        )
        st.plotly_chart(fig_dept, use_container_width=True)

with c_demo2:
    # CHART 4: Premium Dark High-Contrast Donut Chart
    if "OverTime" in attrition_df.columns and len(attrition_df) > 0:
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
            title=dict(text="Attrition Impact Driven by Shift Overtime", x=0.02, y=0.96),
            height=360
        )
        st.plotly_chart(fig_ot, use_container_width=True)

# SECTION 3: COMPENSATION SPREAD & AGE DISTRIBUTION (CHARTS 5 & 6)
st.markdown("<div class='section-header'>Compensation Spread & Age Distribution Analysis</div>", unsafe_allow_html=True)
c_comp1, c_comp2 = st.columns(2, gap="medium")

with c_comp1:
    # CHART 5: Salary Distribution Across Designations
    if "JobRole" in filtered_df.columns and "Monthly_Salary_INR" in filtered_df.columns:
        fig_salary = px.box(
            filtered_df, x="JobRole", y=(filtered_df["Monthly_Salary_INR"] / 1e5) / 83.0,
            color="Attrition" if "Attrition" in filtered_df.columns else None,
            title="Salary Distribution Across Designations (₹ Lakhs)",
            color_discrete_map={"No": COLOR_DARK_BLUE, "Yes": COLOR_DARK_CRIMSON},
            labels={"y": "Monthly Salary (Lakhs)", "JobRole": "Designation"}
        )
        fig_salary.update_layout(
            **plotly_layout,
            title=dict(text="Salary Distribution Across Designations (Lakhs)", x=0.02, y=0.96),
            xaxis_tickangle=-40,
            height=380
        )
        st.plotly_chart(fig_salary, use_container_width=True)

with c_comp2:
    # CHART 6: Workforce Age Demographics (Side-by-Side Grouped)
    if "Age" in filtered_df.columns:
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
            title=dict(text="Workforce Age Demographics vs Attrition", x=0.02, y=0.96),
            height=380
        )
        st.plotly_chart(fig_age, use_container_width=True)

# SECTION 4: AUDIT TABLE
st.markdown("<div class='section-header'>Critical High-Value Personnel Audit Table</div>", unsafe_allow_html=True)

audit_cols = [c for c in ["Department", "JobRole", "Monthly_Salary_INR", "PerformanceRating", "Estimated_Revenue_INR", "Total_Attrition_Loss_INR", "Attrition"] if c in filtered_df.columns]
if audit_cols:
    audit_table = filtered_df[audit_cols].sort_values("Total_Attrition_Loss_INR", ascending=False).head(10).copy()
    
    audit_table["Monthly_Salary_INR"] = audit_table["Monthly_Salary_INR"].apply(lambda x: f"₹{x:,.0f}")
    audit_table["Estimated_Revenue_INR"] = audit_table["Estimated_Revenue_INR"].apply(lambda x: f"₹{x:,.0f}")
    audit_table["Total_Attrition_Loss_INR"] = audit_table["Total_Attrition_Loss_INR"].apply(lambda x: f"₹{x:,.0f}")
    
    audit_table.rename(columns={
        "Monthly_Salary_INR": "Monthly Salary",
        "PerformanceRating": "Appraisal Score",
        "Estimated_Revenue_INR": "Annual Revenue Contribution",
        "Total_Attrition_Loss_INR": "Attrition Loss Risk",
        "JobRole": "Designation"
    }, inplace=True)
    
    st.dataframe(audit_table, use_container_width=True, hide_index=True)
