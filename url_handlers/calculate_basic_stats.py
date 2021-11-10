# to avoid key error
import pandas as pd


def calculation_basic(numeric_df):
    counts = numeric_df.groupby("measurement").count().reset_index()
    counts = counts.melt(id_vars="measurement", var_name='Key', value_name="count")
    mean = numeric_df.groupby("measurement").mean().round(decimals=2).reset_index()
    mean = mean.melt(id_vars="measurement", var_name='Key', value_name="mean")
    df = pd.merge(counts, mean, on=["Key", "measurement"])
    min = numeric_df.groupby("measurement").min().reset_index()
    min = min.melt(id_vars="measurement", var_name='Key', value_name="min")
    df = pd.merge(df, min, on=["Key", "measurement"])
    max = numeric_df.groupby("measurement").max().reset_index()
    max = max.melt(id_vars="measurement", var_name='Key', value_name="max")
    df = pd.merge(df, max, on=["Key", "measurement"])
    std_dev = numeric_df.groupby("measurement").std().round(decimals=2).reset_index()
    std_dev = std_dev.melt(id_vars="measurement", var_name='Key', value_name="stddev")
    df = pd.merge(df, std_dev, on=["Key", "measurement"])
    std_err = numeric_df.groupby("measurement").sem().round(decimals=2).reset_index()
    std_err = std_err.melt(id_vars="measurement", var_name='Key', value_name="stderr")
    df = pd.merge(df, std_err, on=["Key", "measurement"])
    median = numeric_df.groupby("measurement").median().round(decimals=2).reset_index()
    median = median.melt(id_vars="measurement", var_name='Key', value_name="median")
    df = pd.merge(df, median, on=["Key", "measurement"])

    return df

