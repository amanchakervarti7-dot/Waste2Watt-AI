from flask import Flask, jsonify, render_template, request, send_file
from pathlib import Path
from datetime import datetime
import json
import csv
import io

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("data.json")

SEED_BINS = [
    {"id": "WB-1042", "loc": "Central Market", "fill": 92, "material": "Mixed waste"},
    {"id": "WB-0871", "loc": "Riverside Park", "fill": 78, "material": "Organic"},
    {"id": "WB-1120", "loc": "Tech District", "fill": 43, "material": "Plastic"},
    {"id": "WB-0644", "loc": "North Avenue", "fill": 26, "material": "Paper"},
    {"id": "WB-0912", "loc": "Old Town Square", "fill": 84, "material": "Mixed waste"},
    {"id": "WB-0763", "loc": "Greenway Station", "fill": 58, "material": "Organic"},
]

def load_bins():
    if not DATA_FILE.exists():
        save_bins(SEED_BINS)
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else SEED_BINS.copy()
    except (json.JSONDecodeError, OSError):
        return SEED_BINS.copy()

def save_bins(bins):
    DATA_FILE.write_text(json.dumps(bins, indent=2), encoding="utf-8")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Waste2Watt AI", "time": datetime.utcnow().isoformat() + "Z"})

@app.get("/api/dashboard")
def dashboard():
    bins = load_bins()
    needing = sum(1 for b in bins if int(b.get("fill", 0)) >= 75)
    return jsonify({
        "total_bins": 1284 + max(0, len(bins) - len(SEED_BINS)),
        "needing_collection": 86 + needing - 4,
        "collected_today": 18.6,
        "recycling_rate": 64.8,
        "data_mode": "demo"
    })

@app.get("/api/bins")
def get_bins():
    return jsonify({"bins": load_bins()})

@app.post("/api/bins")
def add_bin():
    payload = request.get_json(silent=True) or {}
    bin_id = str(payload.get("id", "")).strip()
    location = str(payload.get("loc", "")).strip()
    try:
        fill = int(payload.get("fill", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Fill level must be a number from 0 to 100."}), 400
    material = str(payload.get("material", "Mixed waste")).strip() or "Mixed waste"
    if not bin_id or not location:
        return jsonify({"error": "Bin ID and location are required."}), 400
    if not 0 <= fill <= 100:
        return jsonify({"error": "Fill level must be between 0 and 100."}), 400
    bins = load_bins()
    if any(str(b.get("id", "")).lower() == bin_id.lower() for b in bins):
        return jsonify({"error": "That bin ID already exists."}), 409
    new_bin = {"id": bin_id, "loc": location, "fill": fill, "material": material}
    bins.insert(0, new_bin)
    save_bins(bins)
    return jsonify({"message": "Bin created", "bin": new_bin, "total_bins": 1284 + max(0, len(bins) - len(SEED_BINS))}), 201

@app.patch("/api/bins/<bin_id>")
def update_bin(bin_id):
    payload = request.get_json(silent=True) or {}
    bins = load_bins()
    target = next((b for b in bins if b.get("id", "").lower() == bin_id.lower()), None)
    if target is None:
        return jsonify({"error": "Bin not found."}), 404
    if "fill" in payload:
        try:
            fill = int(payload["fill"])
        except (TypeError, ValueError):
            return jsonify({"error": "Fill level must be a number from 0 to 100."}), 400
        if not 0 <= fill <= 100:
            return jsonify({"error": "Fill level must be between 0 and 100."}), 400
        target["fill"] = fill
    if "loc" in payload and str(payload["loc"]).strip():
        target["loc"] = str(payload["loc"]).strip()
    if "material" in payload and str(payload["material"]).strip():
        target["material"] = str(payload["material"]).strip()
    save_bins(bins)
    return jsonify({"bin": target})

@app.delete("/api/bins/<bin_id>")
def delete_bin(bin_id):
    bins = load_bins()
    updated = [b for b in bins if b.get("id", "").lower() != bin_id.lower()]
    if len(updated) == len(bins):
        return jsonify({"error": "Bin not found."}), 404
    save_bins(updated)
    return jsonify({"message": "Bin deleted", "bins": updated})

@app.get("/api/reports/bins.csv")
def export_bins():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Bin ID", "Location", "Fill level (%)", "Material", "Status"])
    for b in load_bins():
        fill = int(b.get("fill", 0))
        status = "Critical" if fill >= 90 else "Pickup" if fill >= 75 else "Normal"
        writer.writerow([b.get("id"), b.get("loc"), fill, b.get("material"), status])
    mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="waste2watt-bin-inventory.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
