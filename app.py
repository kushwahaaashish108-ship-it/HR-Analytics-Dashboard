import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="HR Analytics & Financial Risk Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 HR Analytics, Employee Value & Attrition Financial Impact")

# 2. SIDEBAR FILE UPLOADER (DUAL-MODE INGESTION)
st.sidebar.header("📁 Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload Custom HR CSV",
    type=["csv"],
    help="Upload your own HR dataset or leave blank to use benchmark demo data."
)

# 3. LOAD DATASET & FINANCIAL CALCULATIONS
@st.cache_data
def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        df = pd.read_csv("HR_Analytics.csv")

    # Financial Modeling Logic
    perf_multiplier = {1: 2.5, 2: 2.8, 3: 3.2, 4: 4.0}
    if "PerformanceRating" in df.columns:
        df["Perf_Mult"] = df["PerformanceRating"].map(perf_multiplier).fillna(3.0)
    else:
        df["Perf_Mult"] = 3.0

    if "MonthlyIncome" in df.columns:
        df["Annual_Salary"] = df["MonthlyIncome"] * 12
    else:
        df["Annual_Salary"] = 60000 * 12

    df["Estimated_Revenue"] = df["Annual_Salary"] * df["Perf_Mult"]
    df["Replacement_Cost"] = df["Annual_Salary"] * 0.25
    df["Vacancy_Loss"] = df["Estimated_Revenue"] * (3.0 / 12.0)
    df["Total_Attrition_Loss"] = df["Replacement_Cost"] + df["Vacancy_Loss"]

    return df

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# 4. SIDEBAR DYNAMIC FILTERS
st.sidebar.header("🔍 Filter Employees")

dept_list = df["Department"].dropna().unique().tolist() if "Department" in df.columns else []
selected_dept = st.sidebar.multiselect("Department:", dept_list, default=dept_list) if dept_list else []

role_list = df["JobRole"].dropna().unique().tolist() if "JobRole" in df.columns else []
selected_role = st.sidebar.multiselect("Job Role:", role_list, default=role_list) if role_list else []

gender_list = df["Gender"].dropna().unique().tolist() if "Gender" in df.columns else []
selected_gender = st.sidebar.multiselect("Gender:", gender_list, default=gender_list) if gender_list else []

filtered_df = df.copy()
if dept_list and selected_dept:
    filtered_df = filtered_df[filtered_df["Department"].isin(selected_dept)]
if role_list and selected_role:
    filtered_df = filtered_df[filtered_df["JobRole"].isin(selected_role)]
if gender_list and selected_gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]

# 5. TOP EXECUTIVE KPI CARDS
total_emp = len(filtered_df)
attrition_df = filtered_df[filtered_df["Attrition"] == "Yes"] if "Attrition" in filtered_df.columns else pd.DataFrame()
attrition_count = len(attrition_df)
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0

total_revenue = filtered_df["Estimated_Revenue"].sum() if total_emp > 0 else 0
total_at_risk_loss = filtered_df["Total_Attrition_Loss"].sum() if total_emp > 0 else 0
avg_loss_per_exit = filtered_df["Total_Attrition_Loss"].mean() if total_emp > 0 else 0

st.markdown("### 📌 Workforce & Financial Key Performance Indicators")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Workforce", f"{total_emp:,}")
k2.metric("Attrition Count", f"{attrition_count}", f"{attrition_rate:.1f}% rate", delta_color="inverse")
k3.metric("Total Value Generated", f"₹{total_revenue/10000000:.2f} Cr")
k4.metric("Total Loss Exposure", f"₹{total_at_risk_loss/10000000:.2f} Cr", delta="-Potential Risk", delta_color="inverse")
k5.metric("Avg Loss / Exit", f"₹{avg_loss_per_exit/100000:.2f} L")

st.markdown("---")

# 6. EMPLOYEE REVENUE & FINANCIAL LOSS IMPACT CHARTS
st.markdown("### 💼 Employee Revenue Generation & Attrition Financial Risk")
f_c1, f_c2 = st.columns([1.2, 1], gap="medium")

with f_c1:
    hover_cols = [c for c in ["JobRole", "Department", "YearsAtCompany", "OverTime"] if c in filtered_df.columns]
    fig_scatter = px.scatter(
        filtered_df,
        x="Estimated_Revenue",
        y="Total_Attrition_Loss",
        size="MonthlyIncome" if "MonthlyIncome" in filtered_df.columns else None,
        color="Attrition" if "Attrition" in filtered_df.columns else None,
        color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"},
        hover_data=hover_cols,
        title="Employee Value vs Exit Financial Loss Matrix",
        labels={
            "Estimated_Revenue": "Annual Revenue Value (₹)",
            "Total_Attrition_Loss": "Potential Loss if Leaves (₹)"
        },
        template="plotly_white"
    )
    fig_scatter.update_layout(height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)

with f_c2:
    if "Department" in filtered_df.columns:
        dept_fin = filtered_df.groupby("Department")[["Estimated_Revenue", "Total_Attrition_Loss"]].sum().reset_index()
        fig_bar = go.Figure(data=[
            go.Bar(name='Revenue Generated', x=dept_fin['Department'], y=dept_fin['Estimated_Revenue'], marker_color='#3366CC'),
            go.Bar(name='Attrition Loss Risk', x=dept_fin['Department'], y=dept_fin['Total_Attrition_Loss'], marker_color='#DC3912')
        ])
        fig_bar.update_layout(
            barmode='group',
            title="Department-wise Revenue vs Loss Exposure",
            template='plotly_white',
            height=420
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 7. WORKFORCE DEMOGRAPHICS CHARTS
st.markdown("### 📊 Workforce Demographics & Attrition Drivers")
c1, c2 = st.columns(2)

with c1:
    if "Department" in filtered_df.columns and "Attrition" in filtered_df.columns:
        fig_dept = px.histogram(
            filtered_df, x="Department", color="Attrition",
            barmode="group", title="Attrition by Department",
            color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
        )
        st.plotly_chart(fig_dept, use_container_width=True)

with c2:
    if "OverTime" in attrition_df.columns and len(attrition_df) > 0:
        fig_ot = px.pie(
            attrition_df, names="OverTime",
            title="Attrition Impact by Overtime Status",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_ot, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    if "JobRole" in filtered_df.columns and "MonthlyIncome" in filtered_df.columns:
        fig_salary = px.box(
            filtered_df, x="JobRole", y="MonthlyIncome", color="Attrition" if "Attrition" in filtered_df.columns else None,
            title="Salary Distribution Across Job Roles",
            color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
        )
        fig_salary.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_salary, use_container_width=True)

with c4:
    if "Age" in filtered_df.columns:
        fig_age = px.histogram(
            filtered_df, x="Age", color="Attrition" if "Attrition" in filtered_df.columns else None,
            nbins=25, title="Age Distribution vs Attrition",
            color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
        )
        st.plotly_chart(fig_age, use_container_width=True)

# 8. TOP 10 CRITICAL EMPLOYEES AUDIT TABLE
st.markdown("---")
st.markdown("### 🚨 Top 10 Critical Employees by Financial Loss Impact")

audit_cols = [c for c in ["Department", "JobRole", "MonthlyIncome", "PerformanceRating", "Estimated_Revenue", "Total_Attrition_Loss", "Attrition"] if c in filtered_df.columns]
if audit_cols:
    audit_table = filtered_df[audit_cols].sort_values("Total_Attrition_Loss", ascending=False).head(10).copy()
    if "MonthlyIncome" in audit_table.columns:
        audit_table["MonthlyIncome"] = audit_table["MonthlyIncome"].apply(lambda x: f"₹{x:,.0f}")
    if "Estimated_Revenue" in audit_table.columns:
        audit_table["Estimated_Revenue"] = audit_table["Estimated_Revenue"].apply(lambda x: f"₹{x:,.0f}")
    if "Total_Attrition_Loss" in audit_table.columns:
        audit_table["Total_Attrition_Loss"] = audit_table["Total_Attrition_Loss"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(audit_table, use_container_width=True, hide_index=True)
