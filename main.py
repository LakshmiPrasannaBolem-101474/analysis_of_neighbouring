from neighbor_rca_analysis import load_dataset, analyze_neighbor_cells


# STEP 1 — Load JSON Lines Dataset

DATA_FILE = "training_data.json"

df = load_dataset(DATA_FILE)

print("\n Dataset Loaded Successfully")
print("Total Records:", len(df))



# STEP 2 — Define Neighbor Mapping
# (Modify according to your network)

neighbor_map = {
    "CELL-027": ["CELL-026", "CELL-028", "CELL-029"],
    "CELL-026": ["CELL-027"],
    "CELL-028": ["CELL-027"],
    "CELL-029": ["CELL-027"]
}



# STEP 3 — Select an Anomalous Record

anomaly_rows = df[df["is_anomaly"] == True]

if anomaly_rows.empty:
    print(" No anomaly records found.")
    exit()

# Pick first anomaly
anomaly_record = anomaly_rows.iloc[0]

print(
    f"\n Analyzing anomaly for "
    f"{anomaly_record['cell_id']} "
    f"at {anomaly_record['timestamp']}"
)



# STEP 4 — Run Neighbor RCA Analysis

result = analyze_neighbor_cells(
    df=df,
    anomaly_record=anomaly_record,
    neighbor_map=neighbor_map,
    window_minutes=10,
    records_limit=10
)



# STEP 5 — Display RCA Result

print("\n===== RCA RESULT =====")

for key, value in result.items():
    print(f"{key}: {value}")