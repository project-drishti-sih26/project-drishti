import pandas as pd
from scipy.spatial import distance_matrix
import os

def build_distance_matrix(atms_file="data/atms_master.csv", output_file="data/distance_matrix.csv"):
    print("🗺️ Computing spatial distance matrix for the WHERE Engine...")
    
    # Load the ATM data you generated earlier
    df = pd.read_csv(atms_file)
    
    # Extract coordinates
    coords = df[['latitude', 'longitude']].values
    
    # Compute the matrix (Euclidean for simulation speed)
    dist_mat = distance_matrix(coords, coords)
    
    # Save it with ATM IDs as rows and columns so the ML team can look it up instantly
    dist_df = pd.DataFrame(dist_mat, index=df['atm_id'], columns=df['atm_id'])
    dist_df.to_csv(output_file)
    print(f"✅ Distance matrix computed and saved to {output_file}")

if __name__ == "__main__":
    build_distance_matrix()
    