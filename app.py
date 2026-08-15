import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 HR Analytics & Employee Attrition Dashboard")

# 2. Load Dataset
@st.cache_data
st.sidebar.header("📁 Upload Custom Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload HR CSV file", 
    type=["csv"],
    help="Upload custom HR dataset or leave blank for default demo data."
)

@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_csv(file)
    return pd.read_csv("HR_Analytics.csv")

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# 3. Sidebar Filters
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

# 4. Top KPI Cards
total_emp = len(filtered_df)
attrition_df = filtered_df[filtered_df["Attrition"] == "Yes"]
attrition_count = len(attrition_df)
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0
avg_salary = filtered_df["MonthlyIncome"].mean() if total_emp > 0 else 0
avg_tenure = filtered_df["YearsAtCompany"].mean() if total_emp > 0 else 0

st.markdown("### Key Performance Indicators (KPIs)")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Workforce", f"{total_emp:,}")
kpi2.metric("Attrition Count", f"{attrition_count}")
kpi3.metric("Attrition Rate", f"{attrition_rate:.1f}%")
kpi4.metric("Avg Monthly Salary", f"₹{avg_salary:,.0f}")
kpi5.metric("Avg Tenure", f"{avg_tenure:.1f} yrs")

st.markdown("---")

# 5. Visualizations
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
