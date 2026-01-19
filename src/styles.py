def get_custom_css():
    return """
    <style>
        /* Import Google Font: Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Main Container Styling */
        .stApp {
            background-color: #ffffff; /* White Background */
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa; /* Very Light Gray (Standard Streamlit Sidebar) */
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span {
            color: #0f172a !important; /* Dark Text */
        }

        /* Custom Card for Metrics */
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
            border: 1px solid #e2e8f0;
            text-align: center;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-card h3 {
            margin: 0;
            font-size: 0.9rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }
        .metric-card h2 {
            margin: 10px 0 0 0;
            font-size: 1.6rem;
            color: #0f172a;
            font-weight: 700;
        }
        .metric-card .delta {
            font-size: 0.8rem;
            font-weight: 500;
            margin-top: 5px;
        }

        /* Headers with Accent */
        h1, h2, h3 {
            color: #0f172a;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #64748b;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #3b82f6; /* Blue Accent */
            border-bottom: 2px solid #3b82f6;
        }

        /* Download Button Polish */
        .stDownloadButton button {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            transition: all 0.2s;
        }
        .stDownloadButton button:hover {
            background-color: #2563eb;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        /* Link Button Styling (Match Info Box) */
        .stLinkButton a {
            background-color: #e0f2fe; /* Light Blue */
            color: #0f172a !important;
            border: 1px solid #bae6fd;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .stLinkButton a:hover {
            background-color: #bae6fd;
            border-color: #7dd3fc;
        }

        /* Hide Streamlit Anchor Links */
        [data-testid="stHeaderActionElements"],
        .anchor-link {
            display: none !important;
        }
    </style>
    """
