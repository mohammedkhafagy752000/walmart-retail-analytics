import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Page config 
st.set_page_config(
    page_title="Walmart Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)
st.markdown("""
<style>

[data-testid="stMetric"] {
    background-color: #1E1E1E;
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #333333;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

/* LABEL */
[data-testid="stMetricLabel"] p {
    font-size: 22px !important;
    font-weight: bold !important;
    color: #BBBBBB !important;
}

/* VALUE */
[data-testid="stMetricValue"] {
    font-size: 40px !important;
    color: #00FFA3 !important;
    font-weight: bold !important;
}

[data-testid="stMetric"]:hover {
    transform: scale(1.03);
    transition: 0.3s;
    border: 1px solid #00FFA3;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("Walmart Sales Dashboard")

# SQL Server Connection
engine = create_engine(
    "mssql+pyodbc://localhost\\SQLEXPRESS/walmart_db?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "trusted_connection=yes&"
    "TrustServerCertificate=yes"
)

# ===============================
# Sidebar Filter (Branch)
# ===============================
st.sidebar.image("Walmart_logo.png",width=200)
branches = pd.read_sql("SELECT DISTINCT Branch FROM sales", engine)['Branch'].tolist()
branch = st.sidebar.selectbox("Choose Branch", ["All"] + branches)
if branch=='All':
    query="""select * from sales """
else:
    query=f"""select * 
    from sales 
    where Branch='{branch}';
    """

df=pd.read_sql(query,engine)
# ===============================
# KPI CARDS
#================================
total_rev = df['Total'].sum()
total_trans = len(df)
avg_rating = df['rating'].mean()/2
# ===============================
# END KPI CARDS
#================================

# =============================================================================
# Q1 - Top Categories BY REVENUE
# =============================================================================

if branch == "All":
    query_q1 = """
    WITH totalcat AS(
        SELECT 
            category,
            SUM(total) AS Total_Revenue
        FROM sales
        GROUP BY category
    )
    SELECT TOP(5) *,
           (Total_Revenue * 100.0 / (SELECT SUM(total) FROM sales)) AS percentageof_sales
    FROM totalcat
    ORDER BY Total_Revenue DESC;
    """
else:
    query_q1 = f"""
    WITH totalcat AS(
        SELECT 
            category,
            SUM(total) AS Total_Revenue
        FROM sales
        WHERE Branch = '{branch}'
        GROUP BY category
    )
    SELECT TOP(5) *,
           (Total_Revenue * 100.0 / (SELECT SUM(total) FROM sales WHERE Branch = '{branch}')) AS percentageof_sales
    FROM totalcat
    ORDER BY Total_Revenue DESC;
    """

df_q1 = pd.read_sql(query_q1, engine)

# ===============================
# Chart
# ===============================
fig = px.bar(
    df_q1,
    x='category',
    y='Total_Revenue',
    color='category',
    text_auto='.2s')

# Currency Format
fig.update_layout(
    yaxis_title='Revenue',
    xaxis_title='Category',
    height=500,
    font=dict(
        size=20
    ),
    title={
        'text':'Top 5 Categories by Revenue',
        'font':{'size':25}
    },
        title_x=0.3,
        xaxis=dict(
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            tickfont=dict(size=14)
        )
    )

fig.update_traces(
            width=0.6

)
# ======================================================================
#                                 EDN CHART 1
# ======================================================================

# ======================================================================
# Q2. Which branch has the highest average basket value?
# ======================================================================

if branch == "All":

    query_q2 = """
    WITH countbranch AS (
        SELECT 
            Branch,
            AVG(Total) AS avg_transaction_amount
        FROM sales
        GROUP BY Branch
    )

    SELECT TOP(5) *,
           RANK() OVER (ORDER BY avg_transaction_amount DESC) AS branch_rank
    FROM countbranch;
    """

else:

    query_q2 = f"""
    WITH countbranch AS (
        SELECT 
            Branch,
            AVG(Total) AS avg_transaction_amount
        FROM sales
        WHERE Branch = '{branch}'
        GROUP BY Branch
    )

    SELECT *,
           RANK() OVER (ORDER BY avg_transaction_amount DESC) AS branch_rank
    FROM countbranch;
    """
df_q2 = pd.read_sql(query_q2, engine)

fig_q2 = px.bar(
    df_q2,
    x='Branch',
    y='avg_transaction_amount',
    color='Branch',
    text_auto='.2s'
)

# Currency Format
fig_q2.update_layout(
    yaxis_title='Avg transaction Amount',
    xaxis_title='Branch',
    height=500,
    font=dict(
        size=20
    ),
    title={
        'text':'Average Transaction Amount by Branch (Top 5)',
        'font':{'size':25}
    },
        title_x=0.3,
        xaxis=dict(
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            tickfont=dict(size=14)
        )
    )

fig_q2.update_traces(
            width=0.6

)
# ======================================================================
#                                 EDN CHART 2
# ======================================================================


# ======================================================================
# Q3. What are the true peak sales hours during the day based on both transaction count and total revenue?**
# ======================================================================

if branch == "All":

    query_q3 = """
    WITH hourly_stats AS (
    SELECT 
        DATEPART(HOUR, time) AS hour,
        COUNT(*) AS transaction_count,
        SUM(total) AS total_revenue
    FROM sales
    GROUP BY DATEPART(HOUR, time)
)

SELECT top(5)*,
       RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank, RANK() OVER (ORDER BY transaction_count DESC) AS transictions_rank

FROM hourly_stats;
    """

else:

    query_q3 = f"""
    WITH hourly_stats AS (
    SELECT 
        DATEPART(HOUR, time) AS hour,
        COUNT(*) AS transaction_count,
        SUM(total) AS total_revenue
    FROM sales
    WHERE Branch='{branch}'
    GROUP BY DATEPART(HOUR, time)
)

SELECT Top(5) *,
       RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank, RANK() OVER (ORDER BY transaction_count DESC) AS transictions_rank

FROM hourly_stats;
    """
df_q3 = pd.read_sql(query_q3, engine)

fig_q3 = px.line(
    df_q3,
    x='hour',
    y='transaction_count'
)


# Currency Format
fig_q3.update_layout(
    yaxis_title='Transaction',
    xaxis_title='Hour',
    height=500,
    font=dict(
        size=20
    ),
    title={
        'text':'The true peak sales hours during the day (Top 5)',
        'font':{'size':25}
    },
        title_x=0.3,
        xaxis=dict(
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            tickfont=dict(size=14)
        )
    )


# ======================================================================
#                                 EDN CHART 3
# ======================================================================

# ======================================================================
# Q6. What the payments method is perfered?
# ======================================================================

if branch == "All":

    query_q4 = """
    select payment_method, sum(total) as total_per_method
    from sales 
    group by payment_method;
    """

else:

    query_q4 = f"""
    select payment_method, sum(total) as total_per_method
    from sales 
        WHERE Branch='{branch}'
    group by payment_method

    """
df_q4 = pd.read_sql(query_q4, engine)

fig_q4 = px.pie(
    data_frame= df_q4,
    values= 'total_per_method',
    names= 'payment_method'
)

# Currency Format
fig_q4.update_layout(
    height=500,
    font=dict(
        size=20
    ),
    title={
        'text':'preferred Payment Method',
        'font':{'size':25}
    },
        title_x=0.3
    )


# ======================================================================
#                                 EDN CHART 4
# ======================================================================
# ===============================
# Layout
# ===============================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
    label="💰 Total Revenue",
    value=f"${total_rev:,.0f}"
)
with col2:
    st.metric(
    label="🛒 Total Transactions",
    value=f"{total_trans:,}"
)
with col3:
    st.metric(
    label="⭐ Average Rating",
    value=f"{avg_rating:.1f} / 5"
)

col1_r1, col2_r1 = st.columns([1, 1])

with col1_r1:
    st.plotly_chart(fig, use_container_width=True)
with col2_r1:
    st.plotly_chart(fig_q4,use_container_width=True)
    

col1_r2, col2_r2 = st.columns([1, 1])

with col1_r2:
    st.plotly_chart(fig_q3,use_container_width=True)

with col2_r2:
   st.plotly_chart(fig_q2,use_container_width=True)
