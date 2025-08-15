from prophet import Prophet
from app.services.data_loader import process_raw_data

def forecast_prophet(column_name: str, periods: int = 12) -> dict:
    df = process_raw_data(column_name=column_name)

    if df.empty or len(df) < 6:
        return {
            "model": "prophet",
            "category": column_name,
            "forecast": []
        }

    model = Prophet(interval_width=0.80)
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast_df = model.predict(future)

    forecast_result = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

    forecast_json = [
        {
            "ds": row["ds"].strftime("%a, %d %b %Y"),
            "yhat": round(row["yhat"], 3),
            "yhat_lower": round(row["yhat_lower"], 3),
            "yhat_upper": round(row["yhat_upper"], 3)
        }
        for _, row in forecast_result.iterrows()
    ]

    return {
        "model": "prophet",
        "category": column_name,
        "forecast": forecast_json
    }
