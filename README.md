# SensorFlow: Anomaly Detection

Hey there! Welcome to **SensorFlow**.

This is a data dashboard designed to help engineers monitoring water pumps (or really, any machine with sensors) figure out **when and why** things are breaking.

Instead of staring at 50 different charts for 50 different sensors, this app does the heavy lifting for you. It uses **Principal Component Analysis (PCA)** to crunch all that noisy data into a simple "Health Score."

### What does it actually do?
*   **Visualizes History**: See the raw data from all 52 sensors over time.
*   **Finds the anomalies**: Uses statistical analysis to highlight "weird" behavior (anomalies) that might indicate a failure is about to happen.
*   **Simplifies Complexity**: Projects high-dimensional data into a 2D "Health Space" so you can visually see if the machine is drifting into a "Broken" state.

---

### The Tech Stack
*   **Streamlit**: For building the interactive web dashboard.
*   **Pandas & NumPy**: For slicing, dicing, and cleaning the data.
*   **Plotly Express**: For those interactive, zoomable charts.
*   **Scikit-Learn**: The brain of the operation – handles the PCA and standardization.

### How to Run it
1.  Clone this repo.
2.  Install the requirements: `pip install -r requirements.txt`
3.  Run the app: `streamlit run app.py`

Kaggle Dataset Used: https://www.kaggle.com/datasets/nphantawee/pump-sensor-data
