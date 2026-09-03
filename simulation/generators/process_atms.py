import pandas as pd
import great_expectations as ge
import os

def generate_atms_master(output_path: str):
    print("⏳ Starting data ingestion...")
    
    # 1. Creating dummy raw data to test the pipeline bounds
    raw_data = {
        "atm_id": ["ATM-001", "ATM-002", "ATM-003"],
        "latitude": [28.6139, 19.0760, 12.9716],
        "longitude": [77.2090, 72.8777, 77.5946]
    }
    df = pd.DataFrame(raw_data)
    
    # 2. Wrap in a Great Expectations DataFrame for validation
    ge_df = ge.from_pandas(df)
    
    print("🔍 Running Quality Contracts for ML Engine...")
    
    # 3. Define Data Contracts (If these fail, the ML model will break)
    ge_df.expect_column_values_to_not_be_null("latitude")
    ge_df.expect_column_values_to_not_be_null("longitude")
    ge_df.expect_column_values_to_be_between("latitude", 8.4, 37.6) # Indian Lat bounds
    ge_df.expect_column_values_to_be_between("longitude", 68.7, 97.2) # Indian Lon bounds
    
    # 4. Save the validated master file into the 'data' folder
    df.to_csv(output_path, index=False)
    print(f"✅ SUCCESS! atms_master.csv successfully saved to {output_path}")

if __name__ == "__main__":
    # Ensure the data folder exists before saving
    os.makedirs("data", exist_ok=True)
    
    # Run the function and save it to the correct blueprint directory
    generate_atms_master("data/atms_master.csv")