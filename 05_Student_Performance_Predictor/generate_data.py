import numpy as np
import pandas as pd

# We get same random nubmers every time we run the code
np.random.seed(42)

# No. of Students in our dataset
n = 500

# Generating Features
study_hours   = np.random.uniform(1, 10, n)       # 1 to 10 hours/day
attendance    = np.random.uniform(50, 100, n)      # 50% to 100%
previous_score = np.random.uniform(30, 100, n)     # last exam score
sleep_hours   = np.random.uniform(4, 9, n)         # 4 to 9 hours/night
motivation    = np.random.randint(1, 11, n)        # 1 to 10 (whole numbers)

# Adding some randomness (noise) because real life isn't perfectly predictable
noise = np.random.normal(0,5,n)   # small random variation

final_score = (
    3.5 * study_hours +
    0.3 * attendance  +
    0.4 * previous_score + 
    1.0 * sleep_hours + 
    0.8 * motivation  + 
    noise
)

# Clipping the score so it stays between 0 and 100
final_score = np.clip(final_score,0,100)

# Put everything into a DataFrame
df = pd.DataFrame({
    'study_hours': study_hours,
    'attendance': attendance,
    'previous_score': previous_score,
    'sleep_hours': sleep_hours,
    'motivation': motivation,
    'final_score': final_score
})

# Round everything to 2 decimal places for cleanliness
df = df.round(2)

# Save to csv file
df.to_csv('student_data.csv', index=False)

print("Dataset created! Shape:",df.shape)
print(df.head())