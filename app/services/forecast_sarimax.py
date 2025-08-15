import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from app.services.data_loader import process_raw_data

def forecast_sarimax(column_name: str, periods: int = 12) -> dict:
    df = process_raw_data(column_name=column_name)

    if df.empty or len(df) < 6:
        return {
            "model": "sarimax",
            "category": column_name,
            "forecast": []
        }

    y = df.set_index('ds')["y"]

    try:
        model = SARIMAX(y, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12))
        model_fit = model.fit(disp=False)

        forecast_res = model_fit.get_forecast(steps=periods)
        forecast_df = forecast_res.summary_frame()

        forecast_df.reset_index(inplace=True)
        forecast_df.rename(columns={'index': 'ds'}, inplace=True)

        forecast_json = [
            {
                "ds": row["ds"].strftime("%a, %d %b %Y"),
                "yhat": round(row["mean"], 3),
                "yhat_lower": round(row["mean_ci_lower"], 3),
                "yhat_upper": round(row["mean_ci_upper"], 3)
            }
            for _, row in forecast_df.iterrows()
        ]

        return {
            "model": "sarimax",
            "category": column_name,
            "forecast": forecast_json
        }
    except Exception as e:
        return {
            "model": "sarimax",
            "category": column_name,
            "error": str(e),
            "forecast": []
        }
