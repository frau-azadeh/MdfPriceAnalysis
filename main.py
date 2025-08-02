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


# ✅ تبدیل تاریخ شمسی به میلادی برای محاسبات
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


# ✅ تبدیل میلادی به شمسی برای خروجی
def convert_gregorian_to_jalali(g_date):
    try:
        if isinstance(g_date, (datetime, pd.Timestamp)):
            j_date = jdatetime.date.fromgregorian(date=g_date)
            return f"{j_date.year}/{j_date.month:02}/{j_date.day:02}"
        return ""
    except:
        return ""


# ✅ تابع کمکی برای تاریخ‌های پیش‌بینی (خروجی شمسی)
def future_jalali(days):
    future_date = datetime.today() + pd.Timedelta(days=days)
    jdate = jdatetime.datetime.fromgregorian(
        year=future_date.year, month=future_date.month, day=future_date.day
    )
    # خروجی در فرمت استاندارد برای فرانت
    return jdate.strftime("%Y/%m/%d")


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


# 📌 2️⃣ تحلیل آخرین رکوردها (با تاریخ شمسی)
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

        df["lastPriceDate"] = df["lastPriceDate"].apply(convert_jalali_to_gregorian)
        df = df.dropna(subset=["lastPriceDate"])

        latest_date = df["lastPriceDate"].max()
        latest_df = df[df["lastPriceDate"] == latest_date]

        if latest_df.empty:
            return {"error": "داده‌ای برای آخرین تاریخ پیدا نشد"}

        avg_price = latest_df["price"].mean()
        max_price = latest_df["price"].max()
        min_price = latest_df["price"].min()
        grouped = latest_df.groupby("standard")["price"].count().to_dict()

        return {
            "latest_date": convert_gregorian_to_jalali(latest_date),
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


# 📌 3️⃣ پیش‌بینی قیمت (خروجی تاریخ شمسی صحیح)
@app.get("/forecast")
def forecast_prices():
    try:
        response = requests.get(DOTNET_API_URL, verify=False)
        response.raise_for_status()
        products = response.json()

        if not products:
            return {"error": "هیچ داده‌ای موجود نیست"}

        df = pd.DataFrame(products)

        if "lastPriceDate" in df.columns:
            df["lastPriceDate"] = df["lastPriceDate"].apply(convert_jalali_to_gregorian)

        df = df.dropna(subset=["lastPriceDate"])
        df = df.sort_values(by="lastPriceDate")

        recent_data = df.tail(7)
        base_price = recent_data["price"].mean()

        # ✅ پیش‌بینی روزانه
        daily_forecast = []
        for i in range(1, 7):
            daily_forecast.append({
                "date": future_jalali(i),
                "type": "183*366",
                "size": 16,
                "predictedPrice": int(base_price * (1 + (0.005 * i)))
            })

        # ✅ پیش‌بینی هفتگی
        weekly_forecast = []
        for i in range(7, 29, 7):
            weekly_forecast.append({
                "date": future_jalali(i),
                "type": "183*366",
                "size": 16,
                "predictedPrice": int(base_price * (1 + (0.01 * i / 7)))
            })

        # ✅ پیش‌بینی ماهانه
        monthly_forecast = []
        for i in range(30, 121, 30):
            monthly_forecast.append({
                "date": future_jalali(i),
                "type": "183*366",
                "size": 16,
                "predictedPrice": int(base_price * (1 + (0.02 * i / 30)))
            })

        return {
            "daily": daily_forecast,
            "weekly": weekly_forecast,
            "monthly": monthly_forecast
        }

    except Exception as e:
        return {"error": f"مشکل در پیش‌بینی قیمت: {str(e)}"}
