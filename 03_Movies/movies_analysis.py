# ----Import and connect to the database----------------------
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

# --- Create tables and insert data ---------------------------
cursor.executescript("""
    DROP TABLE IF EXISTS movies;
    DROP TABLE IF EXISTS genres;
    DROP TABLE IF EXISTS ratings;
""")

# Movies table
cursor.execute("""
    CREATE TABLE movies (
        id INTEGER PRIMARY KEY,
        title TEXT,
        year INTEGER,
        genre_id INTEGER,
        budget_million REAL,
        revenue_million REAL
    )
""")

# Create genres table
cursor.execute("""
    CREATE TABLE genres (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
""")

# Create ratings table
cursor.execute("""
    CREATE TABLE ratings (
        movie_id INTEGER,
        imdb_score REAL,
        votes INTEGER
    )
""")

# Insert genres
genres = [
    (1, "Action"),
    (2, "Drama"),
    (3, "Comedy"),
    (4, "Sci-Fi"),
    (5, "Horror")
]
cursor.executemany("INSERT INTO genres VALUES (?, ?)", genres)

# Insert movies
movies = [
    (1,  "The Dark Knight",      2008, 1, 185,  1004),
    (2,  "Inception",            2010, 4, 160,   836),
    (3,  "Interstellar",         2014, 4, 165,   701),
    (4,  "The Avengers",         2012, 1, 220,  1519),
    (5,  "Parasite",             2019, 2,  11,   258),
    (6,  "Joker",                2019, 2,  55,  1079),
    (7,  "Get Out",              2017, 5,   4.5, 255),
    (8,  "Superbad",             2007, 3,  20,   121),
    (9,  "Knives Out",           2019, 3,  40,   311),
    (10, "Avengers: Endgame",    2019, 1, 356,  2798),
    (11, "A Quiet Place",        2018, 5,  17,   340),
    (12, "The Martian",          2015, 4, 108,   630),
    (13, "Mad Max: Fury Road",   2015, 1, 185,   375),
    (14, "La La Land",           2016, 2,  30,   446),
    (15, "Everything Everywhere",2022, 2,  14.3, 140),
]
cursor.executemany("INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)", movies)

# Insert ratings
ratings = [
    (1,  9.0, 2700000), (2,  8.8, 2400000), (3,  8.6, 1900000),
    (4,  8.0, 1300000), (5,  8.6,  850000), (6,  8.4, 1100000),
    (7,  7.7,  640000), (8,  7.6,  620000), (9,  7.9,  460000),
    (10, 8.4, 1100000), (11, 7.5,  470000), (12, 8.0,  940000),
    (13, 8.1,  980000), (14, 8.0,  700000), (15, 7.8,  390000),
]
cursor.executemany("INSERT INTO ratings VALUES (?, ?, ?)", ratings)

# Save everything to the file
conn.commit()
print("Database created successfully!")

# --- Query with SQL, load into Pandas -----------------------------
# Query 1: Average revenue by genre
query1 = """
    SELECT g.name AS genre,
           ROUND(AVG(m.revenue_million), 1) AS avg_revenue,
           ROUND(AVG(m.budget_million), 1)  AS avg_budget,
           COUNT(*) AS num_movies
    FROM movies m
    JOIN genres g ON m.genre_id = g.id
    GROUP BY g.name
    ORDER BY avg_revenue DESC
"""

df_genre = pd.read_sql_query(query1, conn)
print("\nRevenue by Genre:")
print(df_genre)

# Query 2: Top 5 movies by ROI (return on investment)
query2 = """
    SELECT m.title,
           m.year,
           g.name AS genre,
           m.budget_million,
           m.revenue_million,
           ROUND((m.revenue_million - m.budget_million) / m.budget_million * 100, 1) AS roi_percent,
           r.imdb_score
    FROM movies m
    JOIN genres g ON m.genre_id = g.id
    JOIN ratings r ON r.movie_id = m.id
    ORDER BY roi_percent DESC
    LIMIT 5
"""

df_roi = pd.read_sql_query(query2, conn)
print("\nTop 5 Movies by ROI:")
print(df_roi)

# Query 3: IMDb score vs budget
query3 = """
    SELECT m.title, m.budget_million, m.revenue_million,
           g.name AS genre, r.imdb_score
    FROM movies m
    JOIN genres g ON m.genre_id = g.id
    JOIN ratings r ON r.movie_id = m.id
"""
df_all = pd.read_sql_query(query3, conn)

# Query 4: Average IMDb score per genre
query4 = """
    SELECT g.name AS genre,
    ROUND(AVG(r.imdb_score), 2) AS avg_score
    FROM movies m
    JOIN genres g ON m.genre_id = g.id
    JOIN ratings r ON r.movie_id = m.id
    GROUP BY genre
    ORDER BY avg_score DESC
"""
df_score = pd.read_sql_query(query4, conn)
print("\nAvg IMDb Score by Genre:")
print(df_score)

# --- Visualize ---------------------------------------
fig = plt.figure(figsize=(14, 10))
fig.suptitle("Movie Database Analysis", fontsize=16, fontweight='bold', y=1.01)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

colors = ['#5DCAA5', '#378ADD', '#D85A30', '#D4537E', '#7F77DD']

# Chart 1: Avg revenue by genre
ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.bar(df_genre['genre'], df_genre['avg_revenue'], color=colors[:len(df_genre)])
ax1.bar(df_genre['genre'], df_genre['avg_budget'], color='lightgray', alpha=0.5, label='Avg Budget')
ax1.set_title("Avg Revenue vs Budget by Genre", fontsize=12)
ax1.set_ylabel("Million USD")
ax1.legend()
ax1.tick_params(axis='x', rotation=20)

# Chart 2: Top 5 ROI
ax2 = fig.add_subplot(gs[0, 1])
ax2.barh(df_roi['title'], df_roi['roi_percent'], color='#1D9E75')
ax2.set_title("Top 5 Movies by ROI (%)", fontsize=12)
ax2.set_xlabel("ROI %")
for i, v in enumerate(df_roi['roi_percent']):
    ax2.text(v + 50, i, f"{v}%", va='center', fontsize=9)

# Chart 3: Budget vs Revenue scatter
ax3 = fig.add_subplot(gs[1, 0])
genre_colors = {'Action':'#D85A30','Drama':'#378ADD','Comedy':'#1D9E75',
                'Sci-Fi':'#7F77DD','Horror':'#D4537E'}
for genre in df_all['genre'].unique():
    subset = df_all[df_all['genre'] == genre]
    ax3.scatter(subset['budget_million'], subset['revenue_million'],
                label=genre, color=genre_colors[genre], s=80, alpha=0.8)
ax3.plot([0, 400], [0, 400], 'k--', alpha=0.3, label='Break-even')
ax3.set_title("Budget vs Revenue", fontsize=12)
ax3.set_xlabel("Budget (M$)")
ax3.set_ylabel("Revenue (M$)")
ax3.legend(fontsize=8)

# Chart 4: IMDb score distribution by genre
ax4 = fig.add_subplot(gs[1, 1])
for i, genre in enumerate(df_all['genre'].unique()):
    subset = df_all[df_all['genre'] == genre]
    ax4.scatter([i]*len(subset), subset['imdb_score'],
                color=genre_colors[genre], s=80, alpha=0.8, zorder=3)
ax4.set_xticks(range(len(df_all['genre'].unique())))
ax4.set_xticklabels(df_all['genre'].unique(), rotation=20)
ax4.set_title("IMDb Score by Genre", fontsize=12)
ax4.set_ylabel("IMDb Score")
ax4.set_ylim(7, 9.5)
ax4.grid(axis='y', alpha=0.3)

# Chart 5: Avg IMDb score by genre (your query!)
ax5 = fig.add_subplot(gs[1, 2])
bars5 = ax5.bar(df_score['genre'], df_score['avg_score'], color=colors[:len(df_score)])
ax5.set_title("Avg IMDb Score by Genre", fontsize=12)
ax5.set_ylabel("Avg IMDb Score")
ax5.set_ylim(7, 9)
ax5.tick_params(axis='x', rotation=20)
for bar, val in zip(bars5, df_score['avg_score']):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             str(val), ha='center', fontsize=9)
    
plt.savefig("movie_analysis.png", dpi=150, bbox_inches='tight')
plt.show()
print("\nChart saved as movie_analysis.png")

conn.close()