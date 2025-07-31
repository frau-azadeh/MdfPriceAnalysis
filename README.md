# 📊 Rebar Price Analysis

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-blue?logo=pandas)
![License](https://img.shields.io/badge/License-MIT-orange)

## 🚀 Overview
Rebar Price Analysis is a **data processing and analysis service** designed to fetch, clean, and analyze rebar product data from an external API.  
It provides endpoints for:
- Price trend analysis  
- Latest price summaries  
- Forecast data generation for daily, weekly, and monthly periods  

---

## ⚡ Features
- 📥 **Fetch live data** from ASP.NET backend  
- 🔄 **Convert dates** between Gregorian & Jalali calendars  
- 📈 **Summarize and analyze** rebar pricing data  
- 🤖 **Forecast future prices** using trend-based calculation  

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **FastAPI** (REST API)
- **Pandas** for data processing
- **Requests** for external API calls
- **Jdatetime** for date conversion

---

## 📌 Endpoints
| Method | Endpoint        | Description                       |
|--------|----------------|-----------------------------------|
| `GET`  | `/`            | Service health check              |
| `GET`  | `/analyze`     | Analyze all price data            |
| `GET`  | `/analyze-latest` | Get last date price summary     |
| `GET`  | `/forecast`    | Forecast daily, weekly, monthly prices |

---

## ⚙️ Installation

# Clone the repo
    git clone https://github.com/frau-azadeh/RebarPriceAnalysis.git
    cd RebarPriceAnalysis

# Create venv and install dependencies
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt

# Run FastAPI server
    uvicorn main:app --reload

---

## 🤝 Contributing

Contributions are warmly welcomed!

Feel free to fork this repo, create a feature branch, and submit a pull request.

---

## 🌻Developed by

Azadeh Sharifi Soltani
