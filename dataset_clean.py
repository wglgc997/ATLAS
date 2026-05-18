import pandas as pd

df = pd.read_csv("dataset_links.csv")
df = df.dropna(how='all', axis=0)

print(df.head())
print(df.info())

df = df.drop_duplicates(subset=["Absolute URL"])
df = df.dropna(subset="Absolute URL")

#Convert columns from true/false to 1/0
df["OK"] = df["OK"].astype(int)
df["Redirected"] = df["Redirected"].astype(int)
df["HTTPS"] = df["HTTPS"].astype(int)
df["Internal"] = df["Internal"].astype(int)

# Convert upper case in lower case
df["Region"] = (df["Region"].astype(str).str.lower())

df["Status Category"] = (df["Status Category"].fillna("unknown"))

df["Response_time"] = (df["Response_time"].fillna(0))

df.to_csv("clean_dataset.csv", index=False)

print("Dataset created!")