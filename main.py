from fastapi import FastAPI
from donwload_stock import download_individual_stock_data
import csv
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/stock/{symbol}")
def get_data(symbol: str):
    data = []
    
    # file_path = f"{symbol}.csv"
    # download_individual_stock_data(file_path)

    # with open(file_path, newline="", encoding="utf-8") as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         data.append(row)
            
    # if os.path.exists(file_path):
    #     os.remove(file_path)

    return {symbol: symbol}