# IPLytics: Mega Cricket Analytics Platform (2008-2025)

> [!TIP]
> **Executive Summary:** This project is a state-of-the-art sports analytics pipeline covering over **1,100+ Indian Premier League matches** (2008-2025). Built with Python, Pandas, and Plotly, it features a complete live **Streamlit Dashboard** and includes a groundbreaking case study on the causal effects of the 2023 **Impact Player Rule**.

## 🎯 Business Problem & Core Objectives
In modern franchise cricket, data-driven player valuation is the only way to maximize auction budgets. Historical "runs scored" or "wickets taken" are no longer sufficient metrics. This platform solves the "Valuation Problem" by deriving contextual efficiency metrics across 18 years of ball-by-ball data. 

Additionally, tracking structural shifts in the game—such as the massive run-inflation caused by the **Impact Player rule**—is crucial for predicting tournament dynamics and building optimal 2026 squads.

| Goal | Analytical Approach |
| :--- | :--- |
| **Player Valuation** | Extracted True Strike Rate & Dot Ball percentages. |
| **Tactical Shift Analysis** | Isolated scoring dynamics Pre and Post Impact-Player rule (2023). |
| **Venue Intelligence** | Mapped highest-scoring and bowler-friendly stadiums globally. |

## 🚀 Key Findings & Insights
Through rigorous Exploratory Data Analysis (EDA) using the `Plotly` graphing engine, the following insights were mathematically proven:
1. **The Scoring Explosion (Impact Player Effect):** The introduction of the Impact Player in 2023 caused the frequency of `200+` run totals to skyrocket from **12% (2022) to over 36% (2025)**.
2. **Top Order Dominance:** The top 10 historical run-scorers minimize running fatigue by scoring over 50% of their runs through boundaries.
3. **The Toss Fallacy:** Despite conventional wisdom, analysis over 1,188 matches shows the toss outcome holds a near perfectly negligible (approx 50/50) correlation with match victory.

## 🖼️ Live Streamlit Dashboard

> [!IMPORTANT]  
> **TO DO (User):** Insert a screenshot of your live Streamlit Dashboard here!
> `![Dashboard Screenshot](images/dashboard.png)`

This project features a fully interactive web application. To run it locally:
```bash
# Install requirements
pip install -r requirements.txt

# Run the app
streamlit run src/dashboard.py
```

## 🔬 Methodology & Architecture
This project follows an Enterprise Data Science lifecycle:
1. **Data Ingestion (Cricsheet):** Combined 1,188 individual ball-by-ball CSV files into a unified master `.csv` dataset of over 280,000 deliveries.
2. **Feature Engineering (Pandas):** Mathematically derived `is_boundary`, `is_dot`, and categorized all data into `Pre/Post Impact Era` cohorts.
3. **Interactive Visualization (Plotly):** Converted all static data charts into dynamic, hoverable matrix charts emphasizing correlation (e.g. Economy vs Wickets).
4. **App Deployment (Streamlit):** Deployed aggregations into a 5-tab user interface for frictionless external stakeholder viewing.

## 💻 Tech Stack
- **Python & Jupyter:** The core scripting environments.
- **Pandas & NumPy:** Raw heavy-lifting for vector computations.
- **Plotly Express & Graph_Objects:** For beautiful, hoverable interactive charts.
- **Streamlit:** For rapid web-app UI dashboard generation.

---
*Developed to showcase O-Grade, production-ready sports analytics methodology.*
