# Business Insights — HR Analytics Project

This document expands the summary findings in the main `README.md` and the closing
comment in `04_sql/HR_Analysis.sql` into a full Finding → Evidence → Business Meaning →
Recommended Action write-up for each business question. It is meant to be read
alongside `05_powerbi/PowerBI-Dashboard.pbix` (pages 1–2) for the visual breakdowns.

---

## 1. Overall Attrition Rate and Departmental Breakdown

**Finding:** Attrition is essentially uniform across the company.

**Evidence:** Overall attrition rate is 33.3% (`04_sql/HR_Analysis.sql`, Section 03).
By department, the rate ranges narrowly from 32.8% to 34.0% (`03_python/HR_Analysis.py`,
Section 6) — a spread of about 1.2 percentage points across five departments, each with
roughly 10,000 employees. See `05_powerbi/page-2.png` for the exact per-department bars.

**Business Meaning:** With sample sizes this large, a 1.2-point spread is within the
range of random variation. There is no department with a statistically or practically
meaningful attrition problem relative to the others.

**Recommended Action:** Do not allocate retention budget or leadership attention to a
specific department based on this data. If attrition is a real concern, the investigation
needs to look at variables not captured here (manager quality, workload, market pay
competitiveness by role) rather than department alone.

---

## 2. Salary and Bonus by Department

**Finding:** Pay is consistent across departments, with no standout.

**Evidence:** Finance has the highest average salary ($75,828); HR has the lowest
($74,584) — a gap of about 1.7% (`README.md`, Key Insights).

**Business Meaning:** A 1.7% spread across departments is not a meaningful pay
disparity — it's smaller than typical year-to-year merit increase variation.

**Recommended Action:** No department-level pay equity intervention is indicated by
this data. If specific roles within departments are underpaid relative to market rate,
that would need to be checked at the job-title level, not department level.

---

## 3. Performance Rating vs. Salary and Bonus

**Finding:** No relationship between performance and pay.

**Evidence:** Correlation between `PerformanceRating` and `Salary` is **-0.005**
(`03_python/HR_Analysis.py`, Section 6) — statistically indistinguishable from zero.

**Business Meaning:** In a healthy pay-for-performance system, you'd expect a positive
correlation (higher-rated employees earning more, on average, within comparable roles
and tenure). A correlation this close to zero suggests either (a) this dataset does not
reflect a real merit-based comp structure, or (b) if it were real data, performance
ratings are not currently driving compensation decisions.

**Recommended Action:** If this were live company data, this would be a flag for
Compensation & Benefits to audit whether merit increases are actually tied to the
performance review process, since the data shows no evidence that they are.

---

## 4. Stress Level vs. Absences and Job Satisfaction

**Finding:** No relationship found in either direction.

**Evidence:** Correlation between `StressLevelScore` and `Absences`, and between
`StressLevelScore` and `JobSatisfactionScore`, are both close to 0
(`03_python/HR_Analysis.py`, Section 6).

**Business Meaning:** In real workforce data, elevated stress typically correlates with
more absences and lower satisfaction. The absence of any relationship here is one of
several signals (alongside Section 8 below) that this dataset does not carry realistic
underlying behavioral dynamics.

**Recommended Action:** None indicated by this data. In a real dataset, a null result
here would still be worth reporting to HR as reassurance that stress isn't currently
translating into disengagement — but would warrant re-checking with a different stress
measure (e.g., self-reported survey vs. this score) before ruling it out entirely.

---

## 5. Hire Source vs. Tenure and Performance

**Finding:** All four hire sources (Referral, Job Board, Recruiter, and others) produce
statistically indistinguishable outcomes.

**Evidence:** Average tenure and performance rating are within 0.1 years and 0.02
rating points of each other across all `HireSource` categories
(`03_python/HR_Analysis.py`, Section 6).

**Business Meaning:** Talent Acquisition often assumes referrals or a specific channel
produce better long-term hires. This dataset does not support that — no channel shows
an advantage in retention or performance.

**Recommended Action:** Don't shift recruiting budget toward one channel based on a
tenure/performance argument using this data. If channel-specific benefits exist (e.g.,
lower cost-per-hire), justify budget decisions on cost, not on the retention/performance
claim.

---

## 6. Retention Risk Label vs. Engagement and Satisfaction

**Finding:** The `RetentionRisk` field does not track the engagement and satisfaction
data it should logically be derived from.

**Evidence:** Employees labeled "High" retention risk show engagement and satisfaction
scores essentially equal to those labeled "Low" risk (`03_python/HR_Analysis.py`,
Section 6; `04_sql/HR_Analysis.sql`, Section 08).

**Business Meaning:** This is the most actionable data-quality finding in the whole
project. A `RetentionRisk` field that doesn't correlate with the inputs it should be
based on is either mislabeled, randomly assigned, or calculated from a broken formula
upstream — any downstream use of this field (e.g., prioritizing manager check-ins for
"High" risk employees) would currently be misdirected.

**Recommended Action:** Before this field is used operationally, have the source system
owner confirm how `RetentionRisk` is calculated. If it's meant to be a composite of
engagement, satisfaction, and tenure, that logic appears to be broken or absent in this
dataset.

---

## 7. Gender Pay Gap

**Finding:** No meaningful gap.

**Evidence:** Average salary by gender differs by less than 0.4% between the highest
and lowest groups (`README.md`, Key Insights). Attrition by gender is similarly close
(33.2%–33.3%, see `05_powerbi/page-2.png`).

**Business Meaning:** A sub-0.4% spread is well within normal noise and does not
indicate a pay equity issue in this dataset.

**Recommended Action:** No action indicated here. Note that a real pay equity audit
would control for role, level, and tenure before drawing conclusions — this is a
simple average, not a regression-adjusted comparison, so it should be treated as a
first-pass check, not a final audit.

---

## 8. Promotion Count vs. Tenure

**Finding:** No relationship between how long someone has been at the company and how
many times they've been promoted.

**Evidence:** Correlation between `PromotionCount` and `YearsAtCompany` is essentially
zero (`03_python/HR_Analysis.py`, Section 6).

**Business Meaning:** In real HR data, tenure and promotion count are almost always
positively correlated (more time = more opportunities to be promoted). A zero
correlation here is one of the strongest individual indicators that this dataset's
fields were generated independently of one another rather than reflecting a coherent
simulated career trajectory.

**Recommended Action:** Treat this as confirmation that the dataset is synthetic
(consistent with the Key Findings note in `03_python/HR_Analysis.py`, Section 8) rather
than as a real finding about promotion practices.

---

## 9. Recruitment Cost and Time-to-Fill by Department

**Finding:** Recruitment cost and time-to-fill are nearly identical across all
departments.

**Evidence:** Average recruitment cost ranges roughly $5,450–$5,490 and time-to-fill
ranges roughly 32.4–32.6 days across departments (`03_python/HR_Analysis.py`,
Section 6).

**Business Meaning:** No department is a meaningful outlier in cost or speed to hire.

**Recommended Action:** No department-specific recruiting process changes are
indicated by this data.

---

## Data Quality Findings (supporting context)

These were identified during cleaning (`03_python/HR_Analysis.py`, Sections 4–5) and
are relevant to interpreting all findings above:

| Issue | Scope | Handling |
|---|---|---|
| Age at hire under 16 (impossible) | 3,373 rows | Flagged (`AgeAtHireFlag`), not deleted |
| `ProjectsCompleted` > `ProjectsAssigned` | 23,789 rows (47.6%) | Flagged (`ProjectsIssueFlag`), not deleted |
| `PromotionCount` > 0 but no `LastPromotionDate` | ~20,800 rows | Left as-is, documented as a limitation |
| `SupervisorID` maps to multiple `SupervisorName` values | All IDs | Dropped from analysis dataset (kept in raw file) |

None of these issues were corrected by guessing at the "true" value — every flagged
row remains in the dataset so downstream users can decide how to handle it for their
specific use case.

---

## Overall Conclusion

Across all nine business questions, every group comparison came out close to equal and
every correlation came out close to zero — including relationships (tenure↔promotions,
stress↔absences, performance↔pay) that would almost always show *some* signal in real
company data. Combined with the data quality issues above, this strongly suggests the
dataset was generated for practice purposes rather than captured from an actual HR
system.

**This does not reduce the value of the exercise.** The workflow — data validation,
flagging vs. deleting, writing SQL that matches Python output, building a dashboard,
and reporting a null result honestly instead of manufacturing a false insight — is the
same discipline required on real company data. The recommendation to any reader of this
project is to treat every number here as a demonstration of *process*, not as an
actionable finding about a real workforce.
