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
    data = download_individual_stock_data(symbol)

    return data