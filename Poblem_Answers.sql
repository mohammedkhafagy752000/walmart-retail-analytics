-- create new db 
create database walmart_db;
use walmart_db;

-- DB validations
select count(invoice_id) from sales;   -- << success>>

-- Payments Methods grouping 
select distinct payment_method from sales;

select distinct payment_method,count(*)
from sales
group by payment_method;

-- count no. distinct Branch in salaes Table
select count(distinct Branch) from sales;  --> 100 Dis Branch
-- MAX AND MIN QUANTITY
SELECT MAX (quantity) as Max_q , MIN (quantity) as Min_q from sales;

-----------------Bussines Problem----------------------------------
-- Q1. What are the top 4 product categories contributing to total revenue, and what percentage of overall sales does each category represent?
with totalcat AS(
select category,sum(total) as Total_Category
from sales
group by category
)
select Top(4) * , (Total_Category/(select sum(total) from sales))*100 As percentageof_sales
from totalcat
order by Total_Category desc;
--Q2. Which branch has the highest average basket value (average transaction amount), and how does its transaction volume compare to other branches?
WITH countbranch AS (
    SELECT 
        Branch,
        AVG(Total) AS avg_transaction_amount
    FROM sales
    GROUP BY Branch
)

SELECT *,
       RANK() OVER (ORDER BY avg_transaction_amount DESC) AS branch_rank
FROM countbranch;
--Q3. What are the true peak sales hours during the day based on both transaction count and total revenue?

WITH hourly_stats AS (
    SELECT 
        DATEPART(HOUR, time) AS hour,
        COUNT(*) AS transaction_count,
        SUM(total) AS total_revenue
    FROM sales
    GROUP BY DATEPART(HOUR, time)
)

SELECT *,
       RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM hourly_stats
ORDER BY total_revenue DESC;
--Q4. Display the highest rated category in each Branch
select * 
from
(
select branch, category,avg(rating) as avg_rate,RANK() over (partition by branch order by avg(rating) desc)as rankCinB
from sales
group by Branch,category ) as t
where rankCinB=1
--Q5. What is the busiest day of the week for each branch based on transaction volume?
WITH sales_day AS (
    SELECT 
        Branch,
        DATENAME(WEEKDAY, CONVERT(DATE, [date], 3)) AS day_name
    FROM sales
)
select * 
from(
SELECT 
    Branch,
    day_name,
    COUNT(*) AS no_transactions, RANK() over (partition by branch order by  COUNT(*)  desc) as Rank_day
FROM sales_day
GROUP BY Branch, day_name
) as t
where Rank_day=1;