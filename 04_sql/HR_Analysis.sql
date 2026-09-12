-- ============================================================
-- HR Analytics — MySQL Business Analysis
-- Source: 03_python/HR_cleaned_data.csv (already cleaned & flagged)
-- ============================================================

-- ============================================================
-- 01. Database / Table Setup
-- ============================================================

CREATE DATABASE IF NOT EXISTS hr_analytics;
USE hr_analytics;

DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    EmployeeID              INT PRIMARY KEY,
    DateOfHire              DATE,
    DateOfBirth             DATE,
    Gender                  VARCHAR(20),
    Department              VARCHAR(30),
    JobTitle                VARCHAR(100),
    EmploymentStatus        VARCHAR(20),
    SupervisorLevel         VARCHAR(20),
    ProjectsAssigned        INT,
    ProjectsCompleted       INT,
    PerformanceRating       INT,
    Salary                  DECIMAL(10,2),
    Bonus                   DECIMAL(10,2),
    YearsAtCompany          INT,
    YearsInCurrentRole      INT,
    TrainingHours           INT,
    OvertimeHours           INT,
    Absences                INT,
    HireSource              VARCHAR(30),
    EmployeeEngagementScore DECIMAL(4,2),
    TerminationDate         DATE NULL,
    ReasonForLeaving        VARCHAR(30) NULL,
    LastPromotionDate       DATE NULL,
    SeniorLeader            VARCHAR(50),
    TeamSize                INT,
    PromotionCount          INT,
    WorkFromHomeDays        INT,
    PerformanceImprovementPlan VARCHAR(5),
    YearsSinceLastTraining  INT,
    JobSatisfactionScore    DECIMAL(4,2),
    RetentionRisk           VARCHAR(10),
    DiversityCategory       VARCHAR(20),
    SkillsAssessmentScore   DECIMAL(5,2),
    RecruitmentCost         DECIMAL(10,2),
    TimeToFillPosition      INT,
    InternalPromotion       VARCHAR(5),
    WorkHoursPerWeek        INT,
    StressLevelScore        DECIMAL(4,2),
    AgeAtHireYears          DECIMAL(5,1),
    AgeAtHireFlag           TINYINT(1),   -- 1 = impossible age at hire (<16), flagged in Python step
    ProjectsIssueFlag       TINYINT(1)    -- 1 = ProjectsCompleted > ProjectsAssigned, flagged in Python step
);

-- NOTE (manual step): Excel/MySQL Workbench "Table Data Import Wizard" or the
-- statement below both work — dates are already in YYYY-MM-DD format in the
-- cleaned CSV, so no STR_TO_DATE conversion is needed.
--
-- LOAD DATA LOCAL INFILE '/path/to/03_python/HR_cleaned_data.csv'
-- INTO TABLE employees
-- FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;


-- ============================================================
-- 02. Data Validation
-- ============================================================

-- Row count check — should be 50,000
SELECT COUNT(*) AS total_rows FROM employees;

-- Confirm EmployeeID is unique (should return 0 rows)
SELECT EmployeeID, COUNT(*) AS cnt
FROM employees
GROUP BY EmployeeID
HAVING COUNT(*) > 1;

-- Confirm the two data-quality flags carried over correctly from Python
SELECT
    SUM(AgeAtHireFlag)     AS invalid_age_rows,
    SUM(ProjectsIssueFlag) AS projects_issue_rows
FROM employees;


-- ============================================================
-- 03. Basic KPIs
-- ============================================================

-- Total employees by status
SELECT EmploymentStatus, COUNT(*) AS employee_count
FROM employees
GROUP BY EmploymentStatus;

-- Overall attrition rate
SELECT
    ROUND(100.0 * SUM(CASE WHEN EmploymentStatus = 'Terminated' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees;

-- Average salary and average tenure across the whole company
SELECT
    ROUND(AVG(Salary), 2)         AS avg_salary,
    ROUND(AVG(YearsAtCompany), 2) AS avg_tenure_years
FROM employees;


-- ============================================================
-- 04. Department Analysis
-- ============================================================

-- Employees and attrition rate by department
SELECT
    Department,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN EmploymentStatus = 'Terminated' THEN 1 ELSE 0 END) AS terminated,
    ROUND(100.0 * SUM(CASE WHEN EmploymentStatus = 'Terminated' THEN 1 ELSE 0 END) / COUNT(*), 2) AS attrition_rate_pct
FROM employees
GROUP BY Department
ORDER BY attrition_rate_pct DESC;

-- Recruitment cost and time-to-fill by department
SELECT
    Department,
    ROUND(AVG(RecruitmentCost), 2)     AS avg_recruitment_cost,
    ROUND(AVG(TimeToFillPosition), 2)  AS avg_days_to_fill
FROM employees
GROUP BY Department
ORDER BY avg_recruitment_cost DESC;


-- ============================================================
-- 05. Job Role Analysis
-- ============================================================

-- Top 10 most common job titles
-- Note: JobTitle has 639 distinct values and is not tied to Department in this
-- dataset, so this is a simple frequency check rather than a deep breakdown.
SELECT JobTitle, COUNT(*) AS employee_count
FROM employees
GROUP BY JobTitle
ORDER BY employee_count DESC
LIMIT 10;


-- ============================================================
-- 06. Salary Analysis
-- ============================================================

-- Average salary by department
SELECT
    Department,
    ROUND(AVG(Salary), 2) AS avg_salary,
    ROUND(AVG(Bonus), 2)  AS avg_bonus
FROM employees
GROUP BY Department
ORDER BY avg_salary DESC;

-- Average salary by gender
SELECT
    Gender,
    ROUND(AVG(Salary), 2) AS avg_salary
FROM employees
GROUP BY Gender
ORDER BY avg_salary DESC;

-- Average salary by performance rating
SELECT
    PerformanceRating,
    ROUND(AVG(Salary), 2) AS avg_salary,
    COUNT(*) AS employee_count
FROM employees
GROUP BY PerformanceRating
ORDER BY PerformanceRating;


-- ============================================================
-- 07. Attrition Analysis
-- ============================================================

-- Reason for leaving, among terminated employees who have a reason recorded
SELECT
    ReasonForLeaving,
    COUNT(*) AS employee_count
FROM employees
WHERE EmploymentStatus = 'Terminated' AND ReasonForLeaving IS NOT NULL
GROUP BY ReasonForLeaving
ORDER BY employee_count DESC;

-- How many terminated employees have NO reason recorded (data quality gap)
SELECT COUNT(*) AS terminated_no_reason
FROM employees
WHERE EmploymentStatus = 'Terminated' AND ReasonForLeaving IS NULL;

-- Average tenure and performance by hire source (does source relate to attrition risk factors?)
SELECT
    HireSource,
    ROUND(AVG(YearsAtCompany), 2)    AS avg_tenure,
    ROUND(AVG(PerformanceRating), 2) AS avg_performance
FROM employees
GROUP BY HireSource
ORDER BY avg_tenure DESC;


-- ============================================================
-- 08. Other Business Questions
-- ============================================================

-- Engagement and satisfaction by RetentionRisk label
SELECT
    RetentionRisk,
    ROUND(AVG(EmployeeEngagementScore), 2) AS avg_engagement,
    ROUND(AVG(JobSatisfactionScore), 2)    AS avg_satisfaction
FROM employees
GROUP BY RetentionRisk;

-- Promotions vs tenure (does staying longer mean more promotions?)
SELECT
    YearsAtCompany,
    ROUND(AVG(PromotionCount), 2) AS avg_promotions
FROM employees
GROUP BY YearsAtCompany
ORDER BY YearsAtCompany;


-- ============================================================
-- 09. Final Findings
-- ============================================================

-- This section is a summary, not a query. See 07_project_documentation/
-- 02_Business_Insights.md for the full Finding / Evidence / Business Meaning /
-- Possible Action write-up.
--
-- Short version: attrition rate, salary, performance, and engagement all come
-- out close to equal across department, gender, hire source, and retention-risk
-- label. Nothing in this dataset shows a strong, actionable driver of attrition —
-- consistent with it being a synthetic/practice dataset rather than real
-- company data.
