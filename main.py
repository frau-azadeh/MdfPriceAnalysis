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
