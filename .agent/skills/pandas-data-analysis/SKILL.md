---
name: pandas-data-analysis
description: Master data analysis with Pandas. Learn to clean, transform, analyze, and visualize data effectively.
---

# Pandas Data Analysis

## Learning Objectives

- Load and manipulate data from various sources (CSV, Excel, SQL, APIs)
- Clean and transform messy datasets
- Perform exploratory data analysis (EDA)
- Aggregate and group data for insights
- Create compelling visualizations
- Optimize performance for large datasets

## Core Topics

### 1. Pandas DataFrames & Series

- Creating DataFrames
- Indexing (`loc`, `iloc`)
- Filtering
- Adding/removing columns

```python
import pandas as pd
df = pd.DataFrame(data)
# Filter
it_employees = df[df['department'] == 'IT']
# Select columns
high_earners = df.loc[df['salary'] > 55000, ['name', 'salary']]
```

### 2. Data Cleaning & Transformation

- Handling missing data (`fillna`, `dropna`)
- Removing duplicates
- String operations
- Date/time parsing

```python
# Handle missing
df['price'].fillna(df['price'].median(), inplace=True)
# Clean text
df['name'] = df['name'].str.strip().str.lower()
# Dates
df['date'] = pd.to_datetime(df['date'])
```

### 3. Aggregation & Grouping

- `groupby`
- Pivot tables
- Window functions

```python
# GroupBy
dept_stats = df.groupby('department').agg({'salary': ['mean', 'count']})
# Rolling average
df['ma_7d'] = df.groupby('id')['sales'].transform(lambda x: x.rolling(7).mean())
```

### 4. Data Visualization

- Matplotlib interaction
- Seaborn
- Built-in plotting

```python
# Bar plot
df.groupby('category')['sales'].sum().plot(kind='bar')
```

## Best Practices

- Use vectorized operations over loops.
- Chain methods for readable pipelines.
- Use explicit copies (`.copy()`) to avoid SettingWithCopyWarning.
- Optimize memory usage (category types for low cardinality strings).
