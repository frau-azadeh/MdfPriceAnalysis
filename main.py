from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
import urllib3
import jdatetime
from datetime import datetime

# غیر فعال کردن هشدارهای SSL برای درخواست‌های لوکال
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# ✅ تنظیم CORS
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:7142"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# آدرس بک‌اند ASP.NET
DOTNET_API_URL = "https://localhost:7142/api/Products"


# ✅ تبدیل تاریخ شمسی به میلادی
def convert_jalali_to_gregorian(jdate_str):
    try:
        if not isinstance(jdate_str, str):
            return pd.NaT
        date_part = jdate_str.split("T")[0]
        jy, jm, jd = map(int, date_part.split("-"))
        g_date = jdatetime.date(jy, jm, jd).togregorian()
        return datetime(g_date.year, g_date.month, g_date.day)
    except:
        return pd.NaT


@app.get("/")
def home():
    return {"message": "✅ سرویس تحلیل قیمت فعال است"}


# 📌 1️⃣ تحلیل کل داده‌ها
@app.get("/analyze")
def analyze_prices():
    try:
        response = requests.get(DOTNET_API_URL, verify=False)
        response.raise_for_status()
        products = response.json()

        if not products:
            return {"error": "هیچ داده‌ای موجود نیست"}

        df = pd.DataFrame(products)

        # تبدیل تاریخ شمسی به میلادی
        if "lastPriceDate" in df.columns:
            df["lastPriceDate"] = df["lastPriceDate"].apply(convert_jalali_to_gregorian)

        avg_price = df["price"].mean()
        max_price = df["price"].max()
        min_price = df["price"].min()
        grouped = df.groupby("standard")["price"].count().to_dict()

        return {
            "summary": {
                "average_price": round(avg_price, 2),
                "max_price": float(max_price),
                "min_price": float(min_price)
            },
            "by_standard": grouped,
            "total_records": int(len(df))
        }
    except Exception as e:
        return {"error": f"مشکل در تحلیل داده: {str(e)}"}


# 📌 2️⃣ تحلیل فقط آخرین رکوردها بر اساس آخرین تاریخ موجود
@app.get("/analyze-latest")
def analyze_latest():
    try:
        response = requests.get(DOTNET_API_URL, verify=False)
        response.raise_for_status()
        products = response.json()

        if not products:
            return {"error": "هیچ داده‌ای موجود نیست"}

        df = pd.DataFrame(products)

        if "lastPriceDate" not in df.columns:
            return {"error": "ستون تاریخ موجود نیست"}

        # تبدیل تاریخ شمسی به میلادی
        df["lastPriceDate"] = df["lastPriceDate"].apply(convert_jalali_to_gregorian)
        df = df.dropna(subset=["lastPriceDate"])

        # ✅ پیدا کردن آخرین تاریخ
        latest_date = df["lastPriceDate"].max()

        # فیلتر فقط رکوردهای آخرین تاریخ
        latest_df = df[df["lastPriceDate"] == latest_date]

        if latest_df.empty:
            return {"error": "داده‌ای برای آخرین تاریخ پیدا نشد"}

        avg_price = latest_df["price"].mean()
        max_price = latest_df["price"].max()
        min_price = latest_df["price"].min()
        grouped = latest_df.groupby("standard")["price"].count().to_dict()

        return {
            "latest_date": latest_date.strftime("%Y-%m-%d"),
            "summary": {
                "average_price": round(avg_price, 2),
                "max_price": float(max_price),
                "min_price": float(min_price)
            },
            "by_standard": grouped,
            "total_records": int(len(latest_df))
        }

    except Exception as e:
        return {"error": f"مشکل در تحلیل داده: {str(e)}"}
