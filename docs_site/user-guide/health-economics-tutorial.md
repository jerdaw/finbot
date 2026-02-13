# Health Economics Tutorial

**Audience:** Clinicians, health policymakers, researchers
**Prerequisites:** Basic Python, understanding of QALYs and cost-effectiveness
**Time:** 30-45 minutes
**Goal:** Learn to perform cost-effectiveness analysis using Finbot's health economics toolkit

---

## Introduction

This tutorial walks through a realistic health economics analysis: comparing treatment options for patients with newly diagnosed Type 2 diabetes. By the end, you'll be able to:

- Model health interventions using Monte Carlo simulation
- Calculate standard cost-effectiveness metrics (ICER, NMB, CEAC)
- Interpret results against international thresholds (NICE, CADTH, WHO, US)
- Make evidence-based formulary and clinical decisions

**Real-world application:** This analysis mirrors decisions made daily by:
- **NICE (UK):** Appraising new diabetes drugs for NHS formulary
- **CADTH (Canada):** Reviewing for provincial drug coverage
- **US Payers:** Making formulary tier decisions (preferred vs. non-preferred)
- **Clinicians:** Choosing between metformin and newer GLP-1 agonists

---

## Clinical Scenario

**Patient Population:** Adults aged 45-65 with newly diagnosed Type 2 diabetes (HbA1c 7.5-9%)

**Treatment Options:**
1. **Metformin** (standard of care): Generic, $500/year, modest efficacy
2. **GLP-1 Receptor Agonist** (newer option): Branded, $10,000/year, greater efficacy

**Clinical Question:** Is the higher cost of GLP-1 agonists justified by improved health outcomes?

**Decision Framework:** Use cost-effectiveness analysis to balance costs against health benefits (measured in QALYs).

---

## Step 1: Define Interventions

First, we define each treatment's parameters based on clinical trial data.

```python
from finbot.services.health_economics.qaly_simulator import HealthIntervention

# Metformin (standard of care)
metformin = HealthIntervention(
    name='Metformin',
    cost_per_year=500.0,           # Generic pricing
    cost_std=100.0,                # Cost uncertainty
    utility_gain=0.08,              # Quality of life improvement (0-1 scale)
    utility_gain_std=0.02,         # Utility uncertainty
    mortality_reduction=0.003,      # Annual mortality reduction (3 per 1000)
    mortality_reduction_std=0.001, # Mortality uncertainty
)

# GLP-1 agonist (e.g., semaglutide, liraglutide)
glp1 = HealthIntervention(
    name='GLP-1 Agonist',
    cost_per_year=10_000.0,        # Branded pricing
    cost_std=1_500.0,
    utility_gain=0.15,              # Greater QoL (HbA1c control + weight loss)
    utility_gain_std=0.03,
    mortality_reduction=0.008,      # Proven CV mortality reduction
    mortality_reduction_std=0.002,
)
```

**Parameter sources:**
- Costs: AWP (Average Wholesale Price) databases
- Utility gains: EQ-5D or SF-6D quality-of-life instruments from trials
- Mortality: Hazard ratios from cardiovascular outcomes trials (SUSTAIN, LEADER)

**Uncertainty:** Standard deviations capture parameter uncertainty from clinical trials.

---

## Step 2: Run Monte Carlo Simulations

Monte Carlo simulation generates distributions of outcomes, not just point estimates.

```python
from finbot.services.health_economics.qaly_simulator import simulate_qalys

# Baseline for newly diagnosed T2D patients
baseline_utility = 0.65      # Uncontrolled diabetes quality of life
baseline_mortality = 0.04    # 4%/year CV mortality risk
time_horizon = 15            # 15 years (until age 60-80)

# Run 10,000 Monte Carlo trials for each intervention
sim_metformin = simulate_qalys(
    metformin,
    baseline_utility=baseline_utility,
    baseline_mortality=baseline_mortality,
    time_horizon=time_horizon,
    n_sims=10_000,
    discount_rate=0.03,  # 3% per WHO/NICE guidelines
    seed=42,
)

sim_glp1 = simulate_qalys(
    glp1,
    baseline_utility=baseline_utility,
    baseline_mortality=baseline_mortality,
    time_horizon=time_horizon,
    n_sims=10_000,
    discount_rate=0.03,
    seed=42,
)

# View mean results
print(f'Metformin:     {sim_metformin["mean_qaly"]:.2f} QALYs, ${sim_metformin["mean_cost"]:,.0f}')
print(f'GLP-1 Agonist: {sim_glp1["mean_qaly"]:.2f} QALYs, ${sim_glp1["mean_cost"]:,.0f}')
```

**Example Output:**
```
Metformin:     9.23 QALYs, $3,876
GLP-1 Agonist: 10.71 QALYs, $78,245
```

**Interpretation:**
- Metformin provides 9.23 discounted QALYs over 15 years at low cost
- GLP-1 provides 1.48 more QALYs but costs $74,369 more
- Is this trade-off worthwhile?

---

## Step 3: Calculate Cost-Effectiveness Metrics

Now we compare the interventions using standard health economics metrics.

```python
from finbot.services.health_economics.cost_effectiveness import cost_effectiveness_analysis

# Run cost-effectiveness analysis
cea = cost_effectiveness_analysis(
    sim_results={'GLP-1 Agonist': sim_glp1, 'Metformin': sim_metformin},
    comparator='Metformin',
)

# Display ICER
icer_val = cea['icer']['ICER'].iloc[0]
print(f'ICER: ${icer_val:,.0f} per QALY')
print(f'Incremental QALYs: {cea["icer"]["Incremental QALYs"].iloc[0]:.2f}')
print(f'Incremental Cost:  ${cea["icer"]["Incremental Cost"].iloc[0]:,.0f}')
```

**Example Output:**
```
ICER: $50,249 per QALY
Incremental QALYs: 1.48
Incremental Cost:  $74,369
```

### Interpreting the ICER

**ICER Formula:**
```
ICER = (Cost_GLP1 - Cost_Metformin) / (QALY_GLP1 - QALY_Metformin)
     = $74,369 / 1.48 QALYs
     = $50,249 per QALY
```

**Compare against international thresholds:**

| Jurisdiction | Threshold | Decision |
|--------------|-----------|----------|
| **NICE (UK)** | £20K-£30K/QALY (~$25K-$38K USD) | ✗ Not cost-effective |
| **CADTH (Canada)** | ~$50K CAD/QALY (~$37K USD) | ✗ Borderline |
| **US (lower)** | $50K/QALY | ✓ Cost-effective |
| **US (mid)** | $100K/QALY | ✓✓ Highly cost-effective |

**Decision:** GLP-1 agonists are cost-effective in the US but may not be approved in UK/Canada at current prices.

---

## Step 4: Quantify Decision Uncertainty

ICER gives a point estimate but hides uncertainty. Use the **Cost-Effectiveness Acceptability Curve (CEAC)** to show the probability of cost-effectiveness at different WTP thresholds.

```python
# Extract CEAC probabilities at key thresholds
ceac = cea['ceac']
ceac_glp1 = ceac['GLP-1 Agonist']

print('Probability GLP-1 is Cost-Effective:')
print(f'  At $25K/QALY (NICE UK):     {ceac_glp1[25_000]:.1%}')
print(f'  At $37K/QALY (CADTH Canada): {ceac_glp1[37_000]:.1%}')
print(f'  At $50K/QALY (US lower):     {ceac_glp1[50_000]:.1%}')
print(f'  At $100K/QALY (US mid):      {ceac_glp1[100_000]:.1%}')
```

**Example Output:**
```
Probability GLP-1 is Cost-Effective:
  At $25K/QALY (NICE UK):     23.4%
  At $37K/QALY (CADTH Canada): 47.8%
  At $50K/QALY (US lower):     72.1%
  At $100K/QALY (US mid):      98.3%
```

**Interpretation:**
- At NICE threshold ($25K/QALY): Only 23% chance GLP-1 is cost-effective → **Don't approve**
- At US lower threshold ($50K/QALY): 72% chance cost-effective → **Likely approve**
- At US mid threshold ($100K/QALY): 98% chance cost-effective → **Definitely approve**

**Why uncertainty matters:** Decision changes from 23% to 98% depending on WTP threshold. Probabilistic analysis reveals this sensitivity.

---

## Step 5: Visualize the Cost-Effectiveness Plane

The CE plane shows joint uncertainty in incremental costs and QALYs.

```python
import plotly.graph_objects as go

plane = cea['ce_plane']['GLP-1 Agonist']

fig = go.Figure()

# Scatter plot of 10,000 simulations
fig.add_trace(go.Scatter(
    x=plane['Delta QALYs'],
    y=plane['Delta Cost'],
    mode='markers',
    marker=dict(size=2, opacity=0.2, color='blue'),
    name='Simulations',
))

# Add WTP threshold lines
x_range = [plane['Delta QALYs'].min(), plane['Delta QALYs'].max()]
fig.add_trace(go.Scatter(
    x=x_range, y=[x * 50_000 for x in x_range],
    mode='lines', line=dict(dash='dash', color='orange'),
    name='US Lower: $50K/QALY',
))

fig.add_hline(y=0, line_dash='dot', line_color='gray')
fig.add_vline(x=0, line_dash='dot', line_color='gray')

fig.update_layout(
    title='Cost-Effectiveness Plane',
    xaxis_title='Incremental QALYs',
    yaxis_title='Incremental Cost ($)',
    template='plotly_white',
)
fig.show()
```

**Quadrants:**
- **NE (North-East):** More effective, more costly → Trade-off (most points here)
- **SE (South-East):** More effective, less costly → Dominant (always adopt)
- **NW (North-West):** Less effective, more costly → Dominated (never adopt)
- **SW (South-West):** Less effective, less costly → Rare

**Result:** Nearly all simulations in NE quadrant means decision depends on WTP threshold.

---

## Step 6: Calculate Net Monetary Benefit (NMB)

NMB converts health gains to monetary terms for easier interpretation.

```python
# NMB at $100K/QALY threshold
wtp = 100_000
nmb = cea['nmb']

print(f'Net Monetary Benefit at ${wtp:,}/QALY threshold:')
print(f'  Metformin:     ${nmb.loc[wtp, "Metformin"]:,.0f}')
print(f'  GLP-1 Agonist: ${nmb.loc[wtp, "GLP-1 Agonist"]:,.0f}')
```

**Example Output:**
```
Net Monetary Benefit at $100,000/QALY threshold:
  Metformin:     $919,124
  GLP-1 Agonist: $992,856
```

**NMB Formula:**
```
NMB = WTP × QALYs - Cost
```

**Interpretation:**
- At $100K/QALY, GLP-1 has higher NMB ($992K vs. $919K)
- **Decision:** Choose GLP-1 (higher NMB = more valuable)
- NMB difference: $73,732 (value gained from switching to GLP-1)

---

## Step 7: Make Clinical and Policy Decisions

### For Healthcare Payers

**UK (NICE):**
```python
if icer_val < 25_000:
    print('Decision: Approve for NHS formulary')
elif icer_val < 38_000:
    print('Decision: Negotiate price reduction or restrict to high-risk patients')
else:
    print('Decision: Reject at current price')
```

**Canada (CADTH):**
```python
if icer_val < 37_000:
    print('Decision: Recommend for provincial formularies')
elif icer_val < 75_000:
    print('Decision: Conditional recommendation (price negotiation)')
else:
    print('Decision: Not recommended')
```

**US Payers:**
```python
if icer_val < 50_000:
    print('Decision: Include on preferred formulary tier (low copay)')
elif icer_val < 150_000:
    print('Decision: Include on non-preferred tier (higher copay)')
else:
    print('Decision: Exclude or require prior authorization')
```

### For Clinicians

**Shared Decision-Making:**
```python
# Check individual patient factors
high_cv_risk = True  # Patient has cardiovascular risk factors
high_hba1c = True    # Poor glycemic control (HbA1c >8%)
can_afford = True    # Insurance covers or patient can afford copay

if high_cv_risk and high_hba1c and can_afford:
    print('Recommendation: Consider GLP-1 agonist (higher benefit)')
elif not can_afford:
    print('Recommendation: Metformin (financial barrier to GLP-1)')
else:
    print('Recommendation: Start with metformin, escalate if needed')
```

**Population Health:**
- **High-risk patients:** GLP-1 (CV benefits justify cost)
- **Low-risk patients:** Metformin (cost-effective first-line)
- **Resource stewardship:** Tiered approach maximizes population health under budget constraint

---

## Advanced: Treatment Schedule Optimization

Find the optimal dosing regimen to maximize Net Monetary Benefit.

```python
from finbot.services.health_economics.treatment_optimizer import optimize_treatment

# Optimize dose frequency and duration
results = optimize_treatment(
    cost_per_dose=800.0,
    cost_per_dose_std=100.0,
    qaly_gain_per_dose=0.015,
    qaly_gain_per_dose_std=0.003,
    frequencies=[1, 2, 4, 12, 26, 52],  # doses per year
    durations=[1, 2, 3, 5, 10, 15],     # years of treatment
    baseline_utility=0.65,
    baseline_mortality=0.03,
    wtp_threshold=100_000,
    n_sims=5000,
    seed=42,
)

# Show top 5 schedules
print('Top 5 Treatment Schedules by NMB:')
top5 = results.head()
for _, row in top5.iterrows():
    print(f'  {int(row["Frequency"]):>2} doses/yr × {int(row["Duration"]):>2} yr  |  '
          f'ICER: ${row["ICER"]:>10,.0f}/QALY  |  NMB: ${row["NMB"]:>10,.0f}')
```

**Example Output:**
```
Top 5 Treatment Schedules by NMB:
  12 doses/yr × 15 yr  |  ICER: $45,234/QALY  |  NMB: $142,567
  12 doses/yr × 10 yr  |  ICER: $46,891/QALY  |  NMB: $138,234
  26 doses/yr × 10 yr  |  ICER: $52,145/QALY  |  NMB: $135,789
  ...
```

**Interpretation:** Monthly dosing (12/year) for 15 years maximizes NMB at $100K/QALY threshold.

---

## Interpreting Results for Different Audiences

### For Clinicians

**Key Message:** "GLP-1 agonists provide 1.5 additional years of quality-adjusted life at a cost of ~$50,000 per QALY gained compared to metformin. This is considered cost-effective in the US (where thresholds are $50K-$150K/QALY) but may not be approved in countries like the UK where thresholds are lower (~$25K/QALY)."

**Clinical Implication:** Use GLP-1 for high-risk patients where benefit is greatest, metformin for lower-risk patients where cost-effectiveness is marginal.

### For Policymakers

**Key Message:** "At current prices, GLP-1 agonists have an ICER of ~$50K/QALY. This exceeds NICE (UK) thresholds but falls within US acceptable ranges. Price negotiations could bring ICER below £20K/QALY for UK approval."

**Policy Implication:** Consider tiered formularies, negotiate rebates, or restrict to high-risk subgroups to improve cost-effectiveness.

### For Patients

**Key Message:** "GLP-1 medications are newer, more expensive diabetes drugs that provide better blood sugar control and weight loss compared to metformin. Whether they're worth the extra cost depends on your insurance coverage and personal health situation. Your doctor can help you decide."

**Shared Decision:** Discuss out-of-pocket costs, expected benefits, and personal values in consultation with physician.

---

## Limitations and Cautions

### Model Limitations

```python
# What the model DOES capture:
# ✓ Cost uncertainty from price variability
# ✓ Efficacy uncertainty from clinical trial confidence intervals
# ✓ Mortality and quality-of-life trade-offs
# ✓ Time discounting (3% per WHO/NICE guidelines)

# What the model DOES NOT capture:
# ✗ Disease progression states (e.g., complications like retinopathy, neuropathy)
# ✗ Treatment switching (e.g., metformin → GLP-1 if HbA1c not controlled)
# ✗ Real-world adherence (assumes 100% compliance, reality ~50-70%)
# ✗ Heterogeneity (all patients treated identically)
```

### Appropriate Uses

**✓ Good Uses:**
- Exploring cost-effectiveness trade-offs between treatments
- Identifying which patients benefit most (high-risk vs. low-risk)
- Estimating population-level budget impact
- Supporting formulary and clinical guideline decisions
- Pedagogical demonstrations for teaching health economics

**✗ Bad Uses:**
- Sole basis for individual treatment decisions (clinical judgment required)
- Assuming simulated outcomes will match real-world results exactly
- Ignoring patient preferences, values, and financial circumstances
- Treating ICERs as precise rather than estimates with uncertainty

---

## Further Reading

**Methodology:**
- [Health Economics Methodology](../../research/health-economics-methodology.md) - Full mathematical details, validation, 22 academic references

**Examples:**
- [Health Economics Notebook](../../notebooks/06_health_economics_demo.ipynb) - Interactive Jupyter notebook with visualizations

**Guidelines:**
- **NICE Methods Guide:** [nice.org.uk/process/pmg9](https://www.nice.org.uk/process/pmg9)
- **CADTH Guidelines:** [cadth.ca/guidelines](https://www.cadth.ca/guidelines-economic-evaluation-health-technologies-canada-4th-edition)
- **WHO CHOICE:** [who.int/choice](https://www.who.int/choice/publications/p_2003_generalised_cea.pdf)
- **Second Panel Report (JAMA):** Sanders GD, et al. JAMA 316.10 (2016): 1093-1103

**Academic Texts:**
- Drummond MF, et al. *Methods for the Economic Evaluation of Health Care Programmes*, 4th ed. Oxford, 2015.
- Briggs AH, et al. *Decision Modelling for Health Economic Evaluation.* Oxford, 2006.

---

## Summary

You've learned to:

1. ✓ Define health interventions with cost and efficacy parameters
2. ✓ Run Monte Carlo simulations to capture uncertainty
3. ✓ Calculate ICER, NMB, and CEAC using standard methods
4. ✓ Interpret results against international thresholds (NICE/CADTH/WHO/US)
5. ✓ Make evidence-based clinical and policy decisions
6. ✓ Optimize treatment schedules to maximize value

**Key Takeaway:** Cost-effectiveness analysis provides a rigorous framework for balancing health benefits against costs, but results are jurisdiction-dependent (different countries have different WTP thresholds) and should inform—not replace—clinical judgment.

**Next Steps:**
- Explore the [methodology document](../../research/health-economics-methodology.md) for theoretical foundations
- Run the [Jupyter notebook](../../notebooks/06_health_economics_demo.ipynb) for hands-on practice
- Apply to your own clinical scenarios by modifying intervention parameters
- Consider subgroup analysis (age, risk level, comorbidities) for more nuanced decisions

---

**Last Updated:** 2026-02-12
**Feedback:** Open an issue on [GitHub](https://github.com/jerdaw/finbot/issues) or contribute improvements via PR.
