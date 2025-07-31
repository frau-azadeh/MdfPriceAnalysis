from fastapi import FastAPI
import requests
import pandas as pd

app = FastAPI()

# آدرس API بک اند ASP.NET
DOTNET_API_URL = "https://localhost:7142/api/Products"

@app.get("/")
def home():
    return {"message": "سرویس تحلیل قیمت فعال است"}

@app.get("/analyze")
def analyze_prices():
    try:
        # گرفتن داده‌ها از API بک اند
        response = requests.get(DOTNET_API_URL, verify=False)  # verify=False برای SSL لوکال
        products = response.json()

        # تبدیل به دیتافریم برای تحلیل
        df = pd.DataFrame(products)

        if df.empty:
            return {"error": "هیچ داده‌ای موجود نیست"}

        # محاسبه آماری ساده
        avg_price = df["price"].mean()
        max_price = df["price"].max()
        min_price = df["price"].min()

        # گروه‌بندی بر اساس استاندارد
        grouped = df.groupby("standard")["price"].count().to_dict()

        return {
            "summary": {
                "average_price": round(avg_price, 2),
                "max_price": max_price,
                "min_price": min_price
            },
            "by_standard": grouped,
            "total_records": len(df)
        }
    

    except Exception as e:
        return {"error": str(e)}
    
    
@app.get("/analyze-latest")
def analyze_latest_prices():
    try:
        response = requests.get(DOTNET_API_URL, verify=False)
        if response.status_code != 200:
            return {"error": f"خطا در دریافت داده ({response.status_code})"}

        products = response.json()
        if not products:
            return {"error": "هیچ داده‌ای موجود نیست"}

        df = pd.DataFrame(products)

        if 'id' not in df.columns or 'lastPriceDate' not in df.columns:
            return {"error": "ستون‌های لازم یافت نشد"}

        # تبدیل تاریخ و انتخاب آخرین رکورد هر محصول
        df['lastPriceDate'] = pd.to_datetime(df['lastPriceDate'], errors='coerce')
        df = df.dropna(subset=['lastPriceDate'])

        latest_df = df.sort_values(by='lastPriceDate').groupby('id').tail(1)

        # محاسبه آمار فقط برای آخرین رکوردها
        avg_price = latest_df["price"].mean()
        max_price = latest_df["price"].max()
        min_price = latest_df["price"].min()
        grouped = latest_df.groupby("standard")["price"].count().to_dict()

        return {
            "summary": {
                "average_price": round(float(avg_price), 2),
                "max_price": float(max_price),
                "min_price": float(min_price)
            },
            "by_standard": grouped,
            "total_records": int(len(latest_df))
        }

    except Exception as e:
        return {"error": f"مشکل در تحلیل داده: {str(e)}"}

