Local Food Wastage Management System
📌 Overview

The Local Food Wastage Management System is a Streamlit-based web application designed to minimize food wastage by connecting food providers (e.g., restaurants, households, shops) with receivers (e.g., NGOs, shelters, needy people).

The system helps track, manage, and visualize surplus food, enabling users to list, claim, and monitor food distribution while generating business insights.

🚀 Features

Dashboard – KPIs and visual analytics for providers, receivers, listings, and claims.

CRUD Operations – Add, update, and delete Providers, Receivers, and Food Listings.

Claims Management – Track food claims and monitor their status.

Business Insights – Identify unclaimed food, expired stock, and waste-prone provider types.

Data Preparation – Load CSV data into an SQLite database automatically.

Query Testing – Validate SQL queries for debugging and consistency.

🗂️ Project Structure
Local-Food-Wastage-System/
│── app.py                # Main Streamlit app (dashboard, CRUD, insights)
│── crud_operations.py    # CRUD helper functions (future expansion)
│── sql_queries.py        # Centralized SQL query definitions
│── data_preparation.py   # Script to load CSV data into SQLite DB
│── test_queries.py       # Test runner for SQL queries
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
│── database/food_wastage.db   # SQLite database (generated)
│── data/                 # Folder for CSV input files

⚙️ Installation & Setup

Clone the repository

git clone https://github.com/SadhnaShukla/Local-Food-Wastage-System.git
cd Local-Food-Wastage-System


Create a virtual environment (recommended)

python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows


Install dependencies

pip install -r requirements.txt


Prepare the database

Place your CSV files inside the data/ folder:

providers_data.csv

receivers_data.csv

food_listings_data.csv

claims_data.csv

Run:

python data_preparation.py


Run the application

streamlit run app.py

📊 Usage

Dashboard → View key statistics and food wastage insights.

CRUD → Add/manage providers, receivers, and food listings.

Insights → Explore unclaimed food percentage, expired stock, and waste-prone providers.

🧪 Testing SQL Queries

To validate all SQL queries defined in sql_queries.py, run:

python test_queries.py

📦 Requirements

Main dependencies (see requirements.txt):

streamlit

pandas

matplotlib

👩‍💻 Author

Name: Sadhna Shukla
Email: shuklasadhna72@gmail.com

✨ This project was built as part of an initiative to reduce food wastage by leveraging technology for social good.
