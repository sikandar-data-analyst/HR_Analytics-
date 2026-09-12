# HR Analytics - Python Cleaning & EDA
# This does the deeper cleaning and exploratory analysis that Excel isn't well suited
# for, and answers the business questions from Part 1.

# %%
# 1. Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Libraries loaded")

# %%
# 2. Load Data
df = pd.read_csv('../01_raw_data/HR_raw_data.csv')
print(df.shape)

# %%
# 3. Understand Data
# Basic look at the columns and data types before doing anything else.
print(df.dtypes)

# Dates are stored as text right now (DD-MM-YYYY). Need to convert them to real dates
# before doing any date math.
date_cols = ['DateOfHire', 'DateOfBirth', 'TerminationDate', 'LastPromotionDate']
for c in date_cols:
    df[c] = pd.to_datetime(df[c], format='%d-%m-%Y', errors='coerce')
print(df[date_cols].dtypes)

# %%
# 4. Data Quality Checks
# Same checks I started in Excel, just easier to do at this scale in Python.

# --- Missing values ---
missing = df.isnull().sum()
print(missing[missing > 0])

# TerminationDate and ReasonForLeaving being blank for people who are still employed
# is expected. LastPromotionDate being blank for people who were never promoted is
# also expected. Checking these against related columns below to see if anything
# doesn't add up.

# %%
# --- Duplicates ---
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate EmployeeID:", df['EmployeeID'].duplicated().sum())

# No duplicates. EmployeeID is a clean primary key.

# %%
# --- Invalid age at hire ---
# Calculated how old each employee was on their hire date. Nobody should be younger
# than about 16.
df['AgeAtHireYears'] = (df['DateOfHire'] - df['DateOfBirth']).dt.days / 365.25
invalid_age = df['AgeAtHireYears'] < 16
print("Employees with age at hire under 16:", invalid_age.sum())
print(df.loc[invalid_age, ['EmployeeID', 'DateOfBirth', 'DateOfHire', 'AgeAtHireYears']].head())

# 3,373 rows have an impossible age at hire. Can't know the real birth date or hire
# date for these, so I'm not going to guess and overwrite them. Adding a flag column
# (AgeAtHireFlag) instead and excluding flagged rows from anything that uses age,
# while keeping them for everything else.

# %%
# --- ProjectsCompleted higher than ProjectsAssigned ---
projects_issue = df['ProjectsCompleted'] > df['ProjectsAssigned']
print("Rows where ProjectsCompleted > ProjectsAssigned:", projects_issue.sum(),
      f"({projects_issue.mean():.1%})")

# Almost half the rows have this. That's too many to be a handful of typos, and
# there isn't enough info to know whether ProjectsAssigned or ProjectsCompleted is
# the wrong one. Flagging it (ProjectsIssueFlag) and leaving both columns as-is
# rather than making up a fix.

# %%
# --- Promotion fields don't agree with each other ---
mismatch = (df['PromotionCount'] > 0) & (df['LastPromotionDate'].isna())
print("PromotionCount > 0 but no LastPromotionDate:", mismatch.sum())

# Over 20,000 rows say someone was promoted but have no date for it. Leaving both
# columns as they are and just noting this as a limitation - any analysis using
# LastPromotionDate specifically should keep this in mind.

# %%
# --- SupervisorID / SupervisorName ---
# In Excel this was hard to check, but Python makes it quick: does each
# SupervisorID always belong to the same SupervisorName?
sup_names_per_id = df.groupby('SupervisorID')['SupervisorName'].nunique()
print("SupervisorIDs linked to more than one name:", (sup_names_per_id > 1).sum(),
      "out of", sup_names_per_id.shape[0])

# Every single SupervisorID is linked to many different names. That means this
# column can't be used as a real "who manages who" key - it's essentially random
# per row. Dropping SupervisorID and SupervisorName from the cleaned dataset used
# for analysis (they stay in the raw file, untouched).

# %%
# 5. Data Cleaning
# Based on the checks above, here's what's actually happening to the data:
#   - Converted date columns to real dates (done above)
#   - Added AgeAtHireYears and a flag AgeAtHireFlag for the 3,373 impossible ages
#     (not deleted, flagged)
#   - Added a flag ProjectsIssueFlag for rows where ProjectsCompleted >
#     ProjectsAssigned (not deleted, flagged)
#   - Dropped SupervisorID and SupervisorName from the analysis dataset
#     (unreliable, not a real key)
#   - Left TerminationDate, ReasonForLeaving, LastPromotionDate blanks as they are
#     - they're legitimately blank for employees the condition doesn't apply to
#
# Not deleting any rows. With a dataset this size and these kinds of issues,
# flagging is safer than guessing what the "correct" value should have been.
df['AgeAtHireFlag'] = df['AgeAtHireYears'] < 16
df['ProjectsIssueFlag'] = df['ProjectsCompleted'] > df['ProjectsAssigned']
cleaned = df.drop(columns=['SupervisorID', 'SupervisorName'])
cleaned.to_csv('HR_cleaned_data.csv', index=False)
print("Cleaned dataset saved:", cleaned.shape)

# %%
# 6. Exploratory Data Analysis

# --- Attrition rate overall and by department ---
total = len(df)
terminated = (df['EmploymentStatus'] == 'Terminated').sum()
print(f"Overall attrition rate: {terminated}/{total} = {terminated/total:.2%}")

dept_attr = df.groupby('Department').apply(
    lambda g: pd.Series({'employees': len(g), 'terminated': (g['EmploymentStatus'] == 'Terminated').sum()})
)
dept_attr['attrition_rate'] = dept_attr['terminated'] / dept_attr['employees']
dept_attr = dept_attr.sort_values('attrition_rate', ascending=False)
print(dept_attr)

plt.figure(figsize=(6, 4))
plt.bar(dept_attr.index, dept_attr['attrition_rate'] * 100, color='#4472C4')
plt.ylabel('Attrition Rate (%)')
plt.title('Attrition Rate by Department')
plt.tight_layout()
plt.savefig('chart_attrition_by_dept.png', dpi=110)
plt.show()

# Attrition is close to 33% in every department (range: 32.8% to 34.0%). With about
# 10,000 employees per department, a difference of this size is close to what you'd
# expect from random chance alone - it doesn't look like one department has a real,
# meaningfully higher attrition problem than another.

# %%
# --- Average salary by department ---
sal_dept = df.groupby('Department')[['Salary', 'Bonus']].mean().sort_values('Salary', ascending=False)
print(sal_dept.round(2))

plt.figure(figsize=(6, 4))
plt.bar(sal_dept.index, sal_dept['Salary'], color='#70AD47')
plt.ylabel('Average Salary ($)')
plt.title('Average Salary by Department')
plt.tight_layout()
plt.savefig('chart_salary_by_dept.png', dpi=110)
plt.show()

# Average salary is within about $1,250 of each other across all five departments
# (roughly 1.7% spread). No department stands out as paying meaningfully more or less.

# %%
# --- Performance rating vs salary ---
perf_sal = df.groupby('PerformanceRating')['Salary'].mean()
print(perf_sal.round(2))
print("\nCorrelation:", round(df['PerformanceRating'].corr(df['Salary']), 4))

plt.figure(figsize=(6, 4))
plt.bar(perf_sal.index.astype(str), perf_sal.values, color='#ED7D31')
plt.xlabel('Performance Rating')
plt.ylabel('Average Salary ($)')
plt.title('Average Salary by Performance Rating')
plt.tight_layout()
plt.savefig('chart_perf_vs_salary.png', dpi=110)
plt.show()

# Correlation is -0.005 - essentially zero. Higher performance ratings are not
# associated with higher pay in this dataset.

# %%
# --- Stress level vs absences and job satisfaction ---
print("Correlation StressLevelScore vs Absences:",
      round(df['StressLevelScore'].corr(df['Absences']), 4))
print("Correlation StressLevelScore vs JobSatisfactionScore:",
      round(df['StressLevelScore'].corr(df['JobSatisfactionScore']), 4))

# Both correlations are close to 0. Stress level doesn't move together with
# absences or job satisfaction here.

# %%
# --- Hire source vs tenure and performance ---
hire_src = df.groupby('HireSource')[['YearsAtCompany', 'PerformanceRating']].mean().sort_values(
    'YearsAtCompany', ascending=False)
print(hire_src.round(3))

plt.figure(figsize=(6, 4))
plt.bar(hire_src.index, hire_src['YearsAtCompany'], color='#264478')
plt.ylabel('Average Years at Company')
plt.title('Average Tenure by Hire Source')
plt.tight_layout()
plt.savefig('chart_tenure_by_hiresource.png', dpi=110)
plt.show()

# Tenure and performance are almost identical across all four hire sources (within
# 0.1 years / 0.02 rating points). Hire source doesn't appear to matter here.

# %%
# --- Retention risk vs engagement and job satisfaction ---
risk_eng = df.groupby('RetentionRisk')[['EmployeeEngagementScore', 'JobSatisfactionScore']].mean().reindex(
    ['Low', 'Medium', 'High'])
print(risk_eng.round(3))

x = np.arange(3)
w = 0.35
plt.figure(figsize=(6, 4))
plt.bar(x - w / 2, risk_eng['EmployeeEngagementScore'], width=w, label='Engagement', color='#4472C4')
plt.bar(x + w / 2, risk_eng['JobSatisfactionScore'], width=w, label='Job Satisfaction', color='#A5A5A5')
plt.xticks(x, risk_eng.index)
plt.title('Engagement & Satisfaction by Retention Risk')
plt.legend()
plt.tight_layout()
plt.savefig('chart_risk_vs_engagement.png', dpi=110)
plt.show()

# Employees labeled "High" retention risk don't show lower engagement or
# satisfaction scores than "Low" risk employees. The RetentionRisk label doesn't
# line up with the engagement/satisfaction data the way you'd expect.

# %%
# --- Gender pay gap ---
gender_sal = df.groupby('Gender')['Salary'].mean().sort_values(ascending=False)
print(gender_sal.round(2))

# Less than 0.4% difference between the highest and lowest average salary by
# gender - no meaningful pay gap in this dataset.

# %%
# --- Promotions vs tenure ---
print("Correlation PromotionCount vs YearsAtCompany:",
      round(df['PromotionCount'].corr(df['YearsAtCompany']), 4))

# Correlation is essentially zero. Employees who have been at the company longer
# don't have more promotions on average, which is a bit surprising for real HR
# data - another sign this dataset was randomly generated rather than captured
# from an actual company.

# %%
# --- Recruitment cost and time-to-fill by department ---
recruit_dept = df.groupby('Department')[['RecruitmentCost', 'TimeToFillPosition']].mean().sort_values(
    'RecruitmentCost', ascending=False)
print(recruit_dept.round(2))

# Recruitment cost and time-to-fill are also nearly identical across departments.

# %%
# 7. Business Questions - Answers
#
# 1. What is the overall attrition rate, and how does it differ by department?
#    Overall attrition is 33.3%. By department it ranges narrowly from 32.8% to
#    34.0% - no department stands out.
#
# 2. Which departments have the highest average salary and bonus?
#    Finance is highest ($75,828 avg salary), HR is lowest ($74,584) - a gap of
#    about 1.7%, not meaningful.
#
# 3. Is PerformanceRating associated with Salary or Bonus?
#    No. Correlation is -0.005, essentially zero.
#
# 4. Is StressLevelScore associated with Absences or JobSatisfactionScore?
#    No. Both correlations are close to 0.
#
# 5. Which HireSource is associated with longer tenure or better performance?
#    None meaningfully - all four sources produce almost identical average
#    tenure and performance.
#
# 6. How does RetentionRisk relate to EmployeeEngagementScore and
#    JobSatisfactionScore?
#    It doesn't. "High" risk employees don't show lower engagement or
#    satisfaction than "Low" risk employees.
#
# 7. Does average Salary differ by Gender?
#    No meaningful gap - under 0.4% difference between genders.
#
# 8. How does PromotionCount relate to YearsAtCompany?
#    No relationship. Correlation is essentially zero.
#
# 9. What is the average RecruitmentCost and TimeToFillPosition by department?
#    Nearly identical across all departments (~$5,450-$5,490, ~32.4-32.6 days).

# %%
# 8. Key Findings
#
# - The dataset is internally clean in terms of structure (no duplicate rows,
#   EmployeeID is a reliable key), but has some real data quality issues: 3,373
#   impossible ages at hire, ~48% of rows where completed projects exceed assigned
#   projects, ~20,800 rows where promotion count and promotion date disagree, and
#   a SupervisorID/Name field that isn't usable as a real key. All of these are
#   flagged rather than silently fixed or deleted.
# - Across every business question checked - department, gender, hire source,
#   performance, stress, retention risk label, promotions - there was no
#   meaningful relationship found with attrition, salary, or performance. Every
#   group comparison came out close to equal, and every correlation came out
#   close to zero.
# - This strongly suggests the dataset was randomly generated for practice
#   purposes rather than captured from a real company's HR system. That's fine
#   for a portfolio project, but the honest conclusion is: this dataset does not
#   show a clear, actionable HR driver of attrition or performance, and any
#   dashboard built on it should present the numbers as they are rather than
#   implying strong patterns that aren't actually there.
