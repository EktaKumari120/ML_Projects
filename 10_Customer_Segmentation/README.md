# Customer Segmentation using K-Means Clustering

## Business Problem
A shopping mall wants to move from one-size-fits-all marketing to 
targeted campaigns by identifying distinct customer segments based on 
income and spending behavior, instead of treating all customers as one group.

## Approach
- Cleaned and preprocessed the real Mall Customers dataset (200 records)
- Investigated outliers using the IQR method and made a reasoned decision to keep them (real high-value customers, not data errors)
- Scaled features (Annual Income, Spending Score) since K-Means is a distance-based algorithm
- Used the Elbow Method and Silhouette Score together to determine the optimal number of clusters (K=5)
- Built a K-Means model and visualized the resulting customer segments
- Performed cross-segment analysis on Age and Gender to add demographic context to each behavioral cluster
- Delivered business recommendations tailored to each segment

## Tools & Libraries
Python, Pandas, Scikit-learn, Matplotlib, Seaborn

## Key Insight
Identified a high-income, low-spending segment (Cluster 3) representing 
the largest untapped revenue opportunity — customers with spending 
capacity who aren't currently being converted, ideal for targeted, 
non-discount campaigns.

## Files
- `notebook.ipynb` — full analysis, code, and visualizations
- `data/Mall_Customers.csv` — dataset used
- `outputs/` — saved charts (elbow plot, silhouette plot, cluster plot, segment breakdowns)