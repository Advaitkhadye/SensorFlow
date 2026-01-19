import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging
import os

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SensorFlow_ETL")

class ReliabilityPipeline:
    def __init__(self, input_path='sensor.csv', output_path='processed_data.parquet'):
        self.input_path = input_path
        self.output_path = output_path
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        
    def load_data(self):
        """Loads and cleans the initial dataset."""
        logger.info(f"Loading data from {self.input_path}...")
        try:
            df = pd.read_csv(self.input_path)
            # Fix Timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, errors='coerce')
                df = df.sort_values('timestamp')
            
            # Drop empty columns (like Unnamed: 0)
            df = df.drop(columns=[c for c in df.columns if 'Unnamed' in c], errors='ignore')
            
            # Initial shape
            logger.info(f"Initial Metrics: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def preprocess(self, df):
        """Feature engineering and data cleaning."""
        logger.info("Starting preprocessing...")
        
        # 1. Handle Missing Values
        # For sensor data, we first fill forward (sensors hold value), then fill backward
        df = df.ffill().bfill()
        
        # Drop columns that are still empty (completely dead sensors)
        df = df.dropna(axis=1, how='all')
        
        # 2. Separate Features and Targets
        sensor_cols = [c for c in df.columns if 'sensor' in c]
        meta_cols = [c for c in df.columns if c not in sensor_cols]
        
        # 3. Dimensionality Reduction (PCA)
        # Creates a "Health Index" from valid sensors
        logger.info(f"Running PCA on {len(sensor_cols)} sensors...")
        x_scaled = self.scaler.fit_transform(df[sensor_cols])
        principal_components = self.pca.fit_transform(x_scaled)
        
        # Add PCA components back to dataframe
        df['PCA_1'] = principal_components[:, 0]
        df['PCA_2'] = principal_components[:, 1]
        
        # 4. Simple Mahalanobis-like Distance (Anomaly Score)
        # Distance from the origin in PCA space
        df['anomaly_score'] = np.sqrt(df['PCA_1']**2 + df['PCA_2']**2)
        
        logger.info("Preprocessing complete.")
        return df

    def run(self):
        """Executes the full pipeline."""
        df = self.load_data()
        df_clean = self.preprocess(df)
        
        logger.info(f"Saving processed data to {self.output_path}...")
        df_clean.to_parquet(self.output_path, index=False)
        logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    pipeline = ReliabilityPipeline()
    pipeline.run()
