from pathlib import Path
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Skin Clinic Campaign API")

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "skin clinic campaign.csv"

# Load dataset
skin_data = pd.read_csv(CSV_PATH)

# Calculate summary tables safely
response_table = (
    (
        skin_data.groupby("Gender")["Response_to_Campaign"].count()
        / skin_data["Gender"].count()
    )
    * 100
).reset_index(name="Response Rate (%)")

age_response = (
    (
        skin_data.groupby("AgeGroup")["Response_to_Campaign"].count()
        / skin_data["AgeGroup"].count()
    )
    * 100
).reset_index(name="Response Rate (%)")

last_q = (
    (
        skin_data.groupby("Purchase_Last_Quarter")["Response_to_Campaign"].count()
        / skin_data["Purchase_Last_Quarter"].count()
    )
    * 100
).reset_index(name="Response Rate (%)")

uniq_cats = skin_data["Unique_Products_Purchased"].apply(
    lambda x: (
        "1-4"
        if 1 <= x <= 4
        else "5–8" if 5 <= x <= 8 else ">8" if x > 8 else "Other"
    )
)
uniq_products = (
    (uniq_cats.value_counts(normalize=True) * 100)
    .reset_index()
)
uniq_products.columns = ["Unique Products Range", "Distribution (%)"]


@app.get("/campaign-analysis", response_class=HTMLResponse)
def get_data_tables():
    style = """
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
        h2 { color: #333; margin-top: 25px; }
        table { border-collapse: collapse; width: 50%; margin-bottom: 20px; background: white; }
        th, td { padding: 10px 15px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #007bff; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
    """

    html_content = f"""
    <html>
        <head>
            <title>Skin Clinic Campaign Breakdown</title>
            {style}
        </head>
        <body>
            <h1>Skin Clinic Campaign Breakdown</h1>
            
            <h2>1. Gender Response Rate</h2>
            {response_table.to_html(index=False)}
            
            <h2>2. Age Group Response Rate</h2>
            {age_response.to_html(index=False)}
            
            <h2>3. Purchase Last Quarter Response Rate</h2>
            {last_q.to_html(index=False)}
            
            <h2>4. Unique Products Purchased Distribution</h2>
            {uniq_products.to_html(index=False)}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Skin Clinic Campaign API!",
        "endpoints": ["/docs", "/health", "/skin-clinic-campaign-breakdown"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)