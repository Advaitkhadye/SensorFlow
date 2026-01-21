import toml
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.toml')

def load_config():
    """
    Loads the project configuration from config.toml.
    Returns a dictionary.
    """
    try:
        if os.path.exists(CONFIG_PATH):
            return toml.load(CONFIG_PATH)
        else:
            # Fallback defaults if config is missing (Safety)
            return {
                'business': {'cost_per_minute': 500},
                'etl': {'anomaly_threshold_std': 2.0}
            }
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}
