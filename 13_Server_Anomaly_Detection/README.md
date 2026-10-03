# Server Anomaly Detection in AWS CloudWatch Metrics

## Business Problem
A cloud infrastructure team monitors hundreds of servers producing 
continuous metrics. Manually watching every metric is impossible at 
scale, and by the time a human notices a problem, an outage may 
already be affecting customers. The goal: automatically flag unusual 
server behavior without any pre-labeled examples of what a "problem" 
looks like in advance.

## Approach
- Worked with real AWS CloudWatch CPU utilization data (14 days, 
  5-minute intervals) from the Numenta Anomaly Benchmark (NAB)
- Discovered a genuine daily pattern (a ~3 AM recurring spike, likely 
  a scheduled job) that could easily be mistaken for an anomaly
- Tested three unsupervised detection methods: Rolling Z-score, STL 
  Decomposition, and Isolation Forest
- Built a reusable, data-driven threshold finder (locating the 
  biggest natural gap among extreme scores) instead of guessing fixed 
  cutoffs, and applied it consistently across all three methods
- Validated all methods against the real, documented incident window, 
  withheld until the final step
- Investigated why standard Precision/Recall/F1 can be misleading for 
  this type of problem, backed by NAB's own published documentation

## Tools & Libraries
Python, Pandas, NumPy, Matplotlib, Seaborn, Statsmodels (STL), 
Scikit-learn (Isolation Forest)

## Key Insight
Isolation Forest, paired with an automatically-determined threshold, 
correctly flagged the real incident with zero false alarms -- while 
fixed-threshold methods repeatedly mistook a harmless daily routine 
for a genuine problem. Evaluating anomaly detection also required 
recognizing that standard classification metrics can undersell a 
method that correctly finds the right moment, rather than every 
point in a labeled window.

## Files
- `notebook.ipynb` — full analysis, code, and visualizations
- `data/ec2_cpu_utilization_24ae8d.csv` — real AWS CloudWatch metric 
  (from Numenta Anomaly Benchmark)
- `data/combined_windows.json` — true incident labels (used only for 
  final validation)
- `outputs/` — saved charts