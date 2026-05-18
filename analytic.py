import pandas as pd
import matplotlib

# Read file
df = pd.read_csv("dataset_links.csv")

# Initial inspection
print(df.info())
print(df.describe())

#Rows/columns
print("Total links:")
print(len(df))

print("\nTotal redirections:")
print(df["Redirected"].value_counts())

print("\nStatus categories:")
print(df["Status Category"].value_counts())

print("\nAverage response time:")
print(df["Response_time"].mean())

print("\nRegion success rate:")
print(df.groupby("Region")["OK"].mean())

print("\nSlowest links:")
slowest_links = df.sort_values(by="Response_time",ascending=False)
print(slowest_links [["Absolute URL","Response_time"]].head(20))