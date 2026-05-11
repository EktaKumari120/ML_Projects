import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the Dataset
df = pd.read_csv('student_data.csv')

#  ── Step 1: Basic overview ────────────────────────────────────────────── 
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

print("\nBasic Statistics:")
print(df.describe().round(2))

print("\nMissing Values:")
print(df.isnull().sum())

# ── Step 2: Distribution of final score ────────────────────────────────
plt.figure(figsize=(7,4))
sns.histplot(df['final_score'], bins = 30, kde=True, color = 'teal')
plt.title('Distribution of final scores')
plt.xlabel('Final score')
plt.ylabel('Number of students')
plt.tight_layout()
plt.savefig('plot_score_distribution.png')
plt.show()

# ── Step 3: Correlation heatmap ─────────────────────────────────────────
plt.figure(figsize=(7, 5))
sns.heatmap(df.corr(), annot=True, fmt='.2f', cmap='coolwarm', linewidths=0.5)
plt.title('Correlation between all features')
plt.tight_layout()
plt.savefig('plot_correlation.png')
plt.show()

# ── Step 4: Scatter plots — each feature vs final score ─────────────────
features = ['study_hours', 'attendance', 'previous_score', 'sleep_hours', 'motivation']

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()   # makes it easy to loop through

for i, feature in enumerate(features):
    axes[i].scatter(df[feature], df['final_score'], alpha=0.3, color='teal', s=15)
    axes[i].set_xlabel(feature)
    axes[i].set_ylabel('Final score')
    axes[i].set_title(f'{feature} vs final score')

# Hide the 6th subplot (we only have 5 features)
axes[5].set_visible(False)

plt.suptitle('Each feature vs final score', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig('plot_scatter.png')
plt.show()