# Wholesale Customer Spending Segmentation (PCA + K-Means)

## Business Problem
A wholesale distributor sells across six product categories to varied 
client types (retailers, cafes, hotels) but has no clear way to group 
clients by purchasing behavior across all categories at once. The goal 
is to discover natural client segments to guide sales strategy, 
delivery frequency, and bulk discount offers.

## Approach
- Investigated and deliberately kept real spending outliers (large B2B 
  clients, not data errors)
- Applied a log transform to correct heavy right-skew common to 
  monetary/spending data, followed by standardization
- Used PCA to compress 6 correlated spending categories into 2 
  components (71.3% of variance retained), enabling direct 2D 
  visualization
- Used the Elbow Method and Silhouette Score together; selected K=4 
  as a reasoned trade-off when the two methods disagreed
- Cross-validated discovered clusters against real Channel (Horeca/
  Retail) and Region labels, which were withheld from the model
- Delivered a named persona and recommended action per segment

## Tools & Libraries
Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn

## Key Insight
Clustering on spending alone (with no access to Channel) independently 
rediscovered the real Horeca/Retail business split for 3 of 4 
segments, and further split "Horeca" into two meaningfully different 
sub-types — a more actionable segmentation than the official Channel 
label alone provides.

## Files
- `notebook.ipynb` — full analysis, code, and visualizations
- `data/Wholesale_customers_data.csv` — dataset used (UCI Wholesale 
  Customers dataset)
- `outputs/` — saved charts