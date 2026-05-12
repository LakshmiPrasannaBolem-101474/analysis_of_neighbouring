import pandas as pd
from datetime import timedelta
import json


def load_dataset(training_data ):
    """
    Read JSON Lines dataset and return DataFrame
    """
    with open(training_data, "r") as f:
        data = [json.loads(line) for line in f]

    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("Dataset is empty")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def analyze_neighbor_cells(
        df,
        anomaly_record,
        neighbor_map,
        window_minutes=10,
        records_limit=10
):
    """
    Neighbor RCA Analysis
    """
    # Validate Required Columns
   
    required_cols = [
        "cell_id",
        "timestamp",
        "prb_dl",
        "availability",
        "is_anomaly"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    
    # Step 1 — Find Neighbor Cells
    
    anomaly_cell = anomaly_record["cell_id"]
    anomaly_time = pd.to_datetime(anomaly_record["timestamp"])

    neighbors = neighbor_map.get(anomaly_cell, [])

    if not neighbors:
        return {
            "neighbor_status": "Unknown",
            "rca_interpretation": "No neighbor definition available"
        }

    # Step 2 — Fetch Last 10 Records Within 10 Min Window
   
    window_start = anomaly_time - timedelta(minutes=window_minutes)

    neighbor_datasets = []
    missing_neighbors = []

    for neighbor in neighbors:

        neighbor_df = df[
            (df["cell_id"] == neighbor) &
            (df["timestamp"] >= window_start) &
            (df["timestamp"] <= anomaly_time)
        ].sort_values("timestamp", ascending=False).head(records_limit)

        if neighbor_df.empty:
            missing_neighbors.append(neighbor)
        else:
            neighbor_datasets.append(neighbor_df)

    # Step 3 — Unknown Case
   
    if len(neighbor_datasets) == 0:
        return {
            "anomaly_cell": anomaly_cell,
            "neighbor_status": "Unknown",
            "rca_interpretation": "No neighbor data available"
        }

   
    # Step 4 — Combine Neighbor Records
    
    combined_neighbors = pd.concat(
        neighbor_datasets,
        ignore_index=True
    )

    
    # Step 5 — Compute Key Metrics
    
    avg_prb_dl = combined_neighbors["prb_dl"].mean()
    avg_availability = combined_neighbors["availability"].mean()
    neighbor_anomaly_count = combined_neighbors["is_anomaly"].sum()

    
    # Step 6 — Classify Neighbor Status
    
    if missing_neighbors:
        neighbor_status = "Partial Data"

    elif avg_prb_dl >= 80:
        neighbor_status = "Congested"

    elif avg_availability < 95:
        neighbor_status = "Degraded"

    else:
        neighbor_status = "Normal"

    
    # Step 7 — RCA Interpretatioyn
    
    if neighbor_status == "Normal":
        rca = "Issue likely cell-level"

    elif neighbor_status == "Degraded":
        rca = "Possible site-level / infrastructure issue"

    elif neighbor_status == "Congested":
        rca = "Possible traffic shift / overload"

    else:
        rca = "RCA confidence lower due to partial/unknown data"

    
    # Final Result
    
    return {
        "anomaly_cell": anomaly_cell,
        "analysis_time": anomaly_time,
        "neighbors_checked": neighbors,
        "missing_neighbors": missing_neighbors,
        "avg_neighbor_prb_dl": round(avg_prb_dl, 2),
        "avg_neighbor_availability": round(avg_availability, 2),
        "neighbor_anomaly_count": int(neighbor_anomaly_count),
        "neighbor_status": neighbor_status,
        "rca_interpretation": rca
    }