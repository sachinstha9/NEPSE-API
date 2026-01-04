from fastapi import FastAPI
import csv
import os

app = FastAPI()

@app.get("/stock/{symbol}")
def get_data(symbol: str):
    data = []
    file_path = f"{symbol}.csv"

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
            
    if os.path.exists(file_path):
        os.remove(file_path)

    return data