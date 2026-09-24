import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="HR Analytics & Financial Risk Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 HR Analytics, Employee Value & Attrition Financial Impact")

# ============================================================
# 2. LOAD DATASET & FINANCIAL CALCULATIONS
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("HR_Analytics.csv")

    # Financial Modeling Logic:
    # 1. Performance Multiplier (Rating 1-4 mapped to 2.5x - 4.0x)
    perf_multiplier = {1: 2.5, 2: 2.8, 3: 3.2, 4: 4.0}
    df["Perf_Mult"] = df["PerformanceRating"].map(perf_multiplier).fillna(3.0)

    # 2. Annual Salary & Estimated Annual Revenue per Employee
    df["Annual_Salary"] = df["MonthlyIncome"] * 12
    df["Estimated_Revenue"] = df["Annual_Salary"] * df["Perf_Mult"]

    # 3. Financial Loss Exposure on Exit:
    # Replacement Cost = 25% of Annual CTC
    # Vacancy Loss = 3 months of revenue productivity gap
    df["Replacement_Cost"] = df["Annual_Salary"] * 0.25
    df["Vacancy_Loss"] = df["Estimated_Revenue"] * (3.0 / 12.0)
    df["Total_Attrition_Loss"] = df["Replacement_Cost"] + df["Vacancy_Loss"]

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading file: {e}. Please ensure 'HR_Analytics.csv' is present in the same folder.")
    st.stop()

# ============================================================
# 3. SIDEBAR FILTERS
# ============================================================
st.sidebar.header("🔍 Filter Employees")

dept_list = df["Department"].dropna().unique().tolist()
selected_dept = st.sidebar.multiselect("Department:", dept_list, default=dept_list)

role_list = df["JobRole"].dropna().unique().tolist()
selected_role = st.sidebar.multiselect("Job Role:", role_list, default=role_list)

gender_list = df["Gender"].dropna().unique().tolist()
selected_gender = st.sidebar.multiselect("Gender:", gender_list, default=gender_list)

# Filter Data
filtered_df = df[
    (df["Department"].isin(selected_dept)) &
    (df["JobRole"].isin(selected_role)) &
    (df["Gender"].isin(selected_gender))
]

# ============================================================
# 4. TOP KPI CARDS (WORKFORCE & FINANCIAL IMPACT)
# ============================================================
total_emp = len(filtered_df)
attrition_df = filtered_df[filtered_df["Attrition"] == "Yes"]
attrition_count = len(attrition_df)
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0

total_revenue = filtered_df["Estimated_Revenue"].sum() if total_emp > 0 else 0
total_at_risk_loss = filtered_df["Total_Attrition_Loss"].sum() if total_emp > 0 else 0
actual_realized_loss = attrition_df["Total_Attrition_Loss"].sum() if len(attrition_df) > 0 else 0
avg_loss_per_exit = filtered_df["Total_Attrition_Loss"].mean() if total_emp > 0 else 0

st.markdown("### 📌 Workforce & Financial Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Workforce", f"{total_emp:,}")
kpi2.metric("Attrition Count", f"{attrition_count}", f"{attrition_rate:.1f}% rate", delta_color="inverse")
kpi3.metric("Total Value Generated", f"₹{total_revenue/10000000:.2f} Cr")
kpi4.metric("Total Loss Exposure", f"₹{total_at_risk_loss/10000000:.2f} Cr", delta="-Potential Risk", delta_color="inverse")
kpi5.metric("Avg Loss / Exit", f"₹{avg_loss_per_exit/100000:.2f} L")

st.markdown("---")

# ============================================================
# 5. FINANCIAL RISK & REVENUE ANALYTICS (NEW FEATURE)
# ============================================================
st.markdown("### 💼 Employee Revenue Generation & Attrition Financial Risk")
f_c1, f_c2 = st.columns([1.2, 1], gap="medium")

with f_c1:
    fig_scatter = px.scatter(
        filtered_df,
        x="Estimated_Revenue",
        y="Total_Attrition_Loss",
        size="MonthlyIncome",
        color="Attrition",
        color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"},
        hover_data=["JobRole", "Department", "YearsAtCompany", "OverTime"],
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

# ============================================================
# 6. ATTRITION PATTERN CHARTS (EXISTING)
# ============================================================
st.markdown("### 📊 Workforce Demographics & Attrition Drivers")
c1, c2 = st.columns(2)

with c1:
    fig_dept = px.histogram(
        filtered_df, x="Department", color="Attrition",
        barmode="group", title="Attrition by Department",
        color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with c2:
    fig_ot = px.pie(
        attrition_df, names="OverTime",
        title="Attrition Impact by Overtime Status",
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_ot, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    fig_salary = px.box(
        filtered_df, x="JobRole", y="MonthlyIncome", color="Attrition",
        title="Salary Distribution Across Job Roles",
        color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
    )
    fig_salary.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_salary, use_container_width=True)

with c4:
    fig_age = px.histogram(
        filtered_df, x="Age", color="Attrition",
        nbins=25, title="Age Distribution vs Attrition",
        color_discrete_map={"Yes": "#EF553B", "No": "#636EFA"}
    )
    st.plotly_chart(fig_age, use_container_width=True)

# ============================================================
# 7. HIGH IMPACT EMPLOYEE RISK AUDIT TABLE
# ============================================================
st.markdown("---")
st.markdown("### 🚨 Top 10 Critical Employees by Financial Loss Impact")

audit_cols = [
    "Department", "JobRole", "MonthlyIncome", "PerformanceRating",
    "Estimated_Revenue", "Total_Attrition_Loss", "Attrition"
]

audit_table = filtered_df[audit_cols].sort_values("Total_Attrition_Loss", ascending=False).head(10).copy()

audit_table["MonthlyIncome"] = audit_table["MonthlyIncome"].apply(lambda x: f"₹{x:,.0f}")
audit_table["Estimated_Revenue"] = audit_table["Estimated_Revenue"].apply(lambda x: f"₹{x:,.0f}")
audit_table["Total_Attrition_Loss"] = audit_table["Total_Attrition_Loss"].apply(lambda x: f"₹{x:,.0f}")

st.dataframe(audit_table, use_container_width=True, hide_index=True)
