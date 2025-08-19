from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import os

BACKEND_URL = os.getenv('BACKEND_URL')

app = Flask(__name__, static_folder="static", template_folder="templates")

# Enable CORS for all routes and origins
# send_wildcard True will send Access-Control-Allow-Origin: *
CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)

# Helper to proxy to backend with JSON headers
def proxy_request(method, path, params=None, json_body=None):
    url = f"{BACKEND_URL}{path}"
    print(f"\n\n***Log: {url}\n\n")
    #headers = {"Accept": "application/json", "Content-Type": "application/json"}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_body,
            headers=headers,
            #timeout=10,
        )
        return Response(resp.content, status=resp.status_code, content_type="application/json")
    except requests.RequestException as e:
        payload = {"error": "backend_unreachable", "detail": str(e)}
        print(f"\n\n***Log: {url}\n\n")
        return Response(json.dumps(payload), status=502, content_type="application/json")

# --- Public UI routes ---
@app.route("/")
def index():
    return render_template("index.html", backend_url=BACKEND_URL)

# --- API routes used by the frontend (proxying to OpenAPI backend) ---

@app.route("/api/flights", methods=["GET"])
def api_get_flights():
    return proxy_request("GET", "/flights")

@app.route("/api/register", methods=["POST"])
def api_register():
    body = request.get_json(force=True)
    print(f"\n\n***Log register: {body}")
    return proxy_request("POST", "/register", json_body=body)

@app.route("/api/get_user", methods=["GET"])
def api_get_user():
    name = request.args.get("name")
    email = request.args.get("email")
    params = {"name": name, "email": email}
    return proxy_request("GET", "/user_id", params=params)

@app.route("/api/book", methods=["POST"])
def api_book():
    body = request.get_json(force=True)
    return proxy_request("POST", "/book", json_body=body)

@app.route("/api/bookings/<int:user_id>", methods=["GET"])
def api_get_bookings(user_id):
    return proxy_request("GET", f"/bookings/{user_id}")

@app.route("/api/cancel/<int:booking_id>", methods=["POST"])
def api_cancel(booking_id):
    return proxy_request("POST", f"/cancel/{booking_id}")

# Simple health endpoint
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "proxy_to": BACKEND_URL})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=True)