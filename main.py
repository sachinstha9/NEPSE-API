import requests
import pandas as pd
from bs4 import BeautifulSoup

def download_individual_stock_data(symbol: str):
    url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", class_="table table-bordered table-hover")
    if not table:
        return []

    rows = table.find_all("tr")
    headers = [th.text.strip() for th in rows[0].find_all("th")]

    data = []
    for row in rows[1:]:
        cols = [td.text.strip().replace(",", "") for td in row.find_all("td")]
        data.append(cols)

    df = pd.DataFrame(data, columns=headers)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.sort_values("Date", ascending=False)

    return df.to_dict(orient="records")


from fastapi import FastAPI

app = FastAPI()

@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    return download_individual_stock_data(symbol)
