import pandas as pd
df = pd.read_csv("C:/Users/mlaxm/Downloads/Procurement KPI Analysis Dataset.csv")


# Data Cleaning

#Covert dates
df["Order_Date"] = pd.to_datetime(df["Order_Date"], dayfirst=True)
df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"], dayfirst=True)


## replace missing defects with 0
df["Defective_Units"] = df["Defective_Units"].fillna(0)
df["Delivery_Date"] = df["Delivery_Date"].ffill()


df["Lead_time"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days
df["Defect_rate"] = df["Defective_Units"] / df["Quantity"]
df["Compliance"] = df["Compliance"].str.strip().str.lower()
df["Compliance_Flag"] = df["Compliance"].map({"yes":1, "no":0})
df["Cost_Savings"] = df["Unit_Price"] - df["Negotiated_Price"]
df["On_Time_Delivery"] = (df["Lead_time"] <= 7).astype(int)


supplier_metrics = df.groupby("Supplier").agg({
    "Lead_time": "mean",
    "Defect_rate": "mean",
    "Compliance_Flag": "mean",
    "On_Time_Delivery": "mean",
    "Cost_Savings": "mean"
})

supplier_metrics = df.groupby("Supplier").agg(
    Avg_Lead_Time=("Lead_time", "mean"),
    Lead_Time_Variability=("Lead_time", "std"),
    Avg_Defect_Rate=("Defect_rate", "mean"),
    Compliance_Rate=("Compliance_Flag", "mean"),
    On_Time_Delivery_Rate=("On_Time_Delivery", "mean"),
    Avg_Cost_Savings=("Cost_Savings", "mean"),
    Total_Orders=("PO_ID", "count")
)

supplier_metrics = supplier_metrics.reset_index()

supplier_metrics["Quality_Score"] = 1 - supplier_metrics["Avg_Defect_Rate"]
supplier_metrics["Consistency_Score"] = 1 / (1 + supplier_metrics["Lead_Time_Variability"])

supplier_metrics["Reliability_Score"] = (
    0.4 * supplier_metrics["On_Time_Delivery_Rate"] +
    0.3 * supplier_metrics["Quality_Score"] +
    0.2 * supplier_metrics["Consistency_Score"] +
    0.1 * supplier_metrics["Compliance_Rate"]
)

supplier_metrics["Supplier_Rank"] = supplier_metrics["Reliability_Score"].rank(ascending=False)
supplier_metrics = supplier_metrics.sort_values(by="Reliability_Score", ascending=False)
print(supplier_metrics)

supplier_metrics.to_csv("C:/Users/mlaxm/Downloads/supplier_reliability_scores.csv", index=False)






