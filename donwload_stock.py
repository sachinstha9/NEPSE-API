import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
import time

def scrape_nepse_stock(url):
    """Scrape NEPSE stock history table from the page."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        # Dismiss notification alert if present
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            time.sleep(1)
        except NoAlertPresentException:
            pass

        # Wait for History button and click
        history_btn = wait.until(EC.element_to_be_clickable(
            (By.ID, "ctl00_ContentPlaceHolder1_CompanyDetail1_lnkHistoryTab")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", history_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", history_btn)
        time.sleep(2)

        # Dismiss alert again if it appears
        try:
            alert = driver.switch_to.alert
            alert.dismiss()
            time.sleep(1)
        except NoAlertPresentException:
            pass

        # Wait for table
        table_div = wait.until(EC.presence_of_element_located(
            (By.ID, "ctl00_ContentPlaceHolder1_CompanyDetail1_divDataPrice")
        ))

        # Extract table
        table = table_div.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        if not rows:
            print(f"No data found for this stock.")
            return pd.DataFrame()  # return empty DataFrame

        # Extract headers safely
        headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")] if len(rows) > 0 else []

        # Extract rows
        data = []
        for row in rows[1:]:
            cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")]
            data.append(cols)

        df = pd.DataFrame(data, columns=headers)

        # Remove first column (serial number)
        df = df.iloc[:, 1:]
        return df

    finally:
        driver.quit()


def convert_stock_data_to_float(df):
    """Convert all numeric columns to float (except Date column)."""
    numeric_cols = df.columns[1:]  # skip Date column
    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "")
            .str.replace('"', "")
            .str.strip()
            .replace("", "0")
            .astype(float)
        )
    return df


def download_individual_stock_data(symbol):
    df_new = scrape_nepse_stock(f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}")
    df_new = convert_stock_data_to_float(df_new)
    df_new['Date'] = pd.to_datetime(df_new['Date'], errors='coerce')
    csv_filename = f"./{symbol}.csv"

    if os.path.exists(csv_filename):
        # Load existing CSV
        df_existing = pd.read_csv(csv_filename)
        df_existing['Date'] = pd.to_datetime(df_existing['Date'], errors='coerce')
        last_date = df_existing['Date'].max()

        # Keep only new rows
        df_to_add = df_new[df_new['Date'] > last_date]

        if not df_to_add.empty:
            df_updated = pd.concat([df_existing, df_to_add], ignore_index=True)
            # Optional: sort by Date descending
            df_updated = df_updated.sort_values(by='Date', ascending=False)
            save_stock_data_csv(df_updated, csv_filename)
            print(f"{len(df_to_add)} new rows added to {csv_filename}")
        else:
            print("No new data to update.")
    else:
        # CSV does not exist, save all
        df_new = df_new.sort_values(by='Date', ascending=False)
        
        return df_new.to_json()
        # save_stock_data_csv  } created with all data.")
        
print(download_individual_stock_data("SHIVM"))