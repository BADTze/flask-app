from flask import Blueprint, jsonify, request
from app.services.data_loader import fetch_api_data, process_raw_data
from app.services.forecast_prophet import forecast_prophet
from app.services.forecast_sarimax import forecast_sarimax 
from app.services.var_corr import compute_var_correlation

api_bp = Blueprint("api", __name__)

# 1. Ambil data mentah dari API eksternal
@api_bp.route('/raw_data')
def get_raw_data():
    data = fetch_api_data()
    if not data:
        return jsonify({"error": "No data available"}), 500
    return jsonify(data)

# 2. Ambil actual data bersih dari backend
@api_bp.route('/actual_data')
def get_actual_data():
    category = request.args.get("category", "indexEnergy")
    df = process_raw_data(column_name=category)
    if df.empty:
        return jsonify({"error": f"No valid actual data for category '{category}'"}), 404
    return jsonify(df.to_dict(orient="records"))

@api_bp.route('/forecast')
def get_forecast():
    category = request.args.get("category", "indexEnergy")
    model = request.args.get("model", "prophet").lower()
    horizon = int(request.args.get("horizon", 12)) 

    if model == "prophet":
        result = forecast_prophet(column_name=category, periods=horizon)
    elif model == "sarimax":
        result = forecast_sarimax(column_name=category, periods=horizon)
    else:
        return jsonify({"error": f"Unknown model '{model}'"}), 400

    if not result.get("forecast"):
        return jsonify({"error": f"No forecast data for {category} with model {model}"}), 500

    return jsonify(result)

@api_bp.route('/var_correlation')
def get_var_correlation():
    result = compute_var_correlation()
    return jsonify(result)