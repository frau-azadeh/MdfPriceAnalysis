from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

# مدل داده دریافتی از ASP.NET
class PriceData(BaseModel):
    date: str
    price: float

@app.get("/")
def home():
    return {"message": "سرویس تحلیل قیمت فعال است"}

@app.post("/analyze")
def analyze(prices: list[PriceData]):
    # تبدیل داده‌ها به DataFrame
    df = pd.DataFrame([p.dict() for p in prices])

    # محاسبه میانگین قیمت
    avg_price = df["price"].mean()
    max_price = df["price"].max()
    min_price = df["price"].min()

    return {
        "میانگین قیمت": avg_price,
        "بیشترین قیمت": max_price,
        "کمترین قیمت": min_price
    }
