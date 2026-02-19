"""
app.py
------
Lightweight Flask server.

Routes:
  GET  /           → editor UI
  GET  /data        → load current cv_data.yaml as text
  POST /save        → write edited YAML back to cv_data.yaml
  POST /generate    → generate + return PDF for download
  POST /validate    → parse YAML and return any errors (no PDF)
"""

import os
import traceback
from pathlib import Path

import yaml
from flask import Flask, jsonify, request, send_file, render_template
import io

from generate_pdf import generate

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "cv_data.yaml"


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_yaml_text() -> str:
    return DATA_FILE.read_text(encoding="utf-8")


def parse_yaml(text: str) -> dict:
    return yaml.safe_load(text)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    return jsonify({"yaml": load_yaml_text()})


@app.route("/save", methods=["POST"])
def save_data():
    body = request.get_json(force=True)
    text = body.get("yaml", "")
    try:
        parse_yaml(text)          # validate before saving
    except yaml.YAMLError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    DATA_FILE.write_text(text, encoding="utf-8")
    return jsonify({"ok": True})


@app.route("/validate", methods=["POST"])
def validate_data():
    body = request.get_json(force=True)
    text = body.get("yaml", "")
    try:
        parse_yaml(text)
        return jsonify({"ok": True})
    except yaml.YAMLError as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/generate", methods=["POST"])
def generate_pdf():
    body = request.get_json(force=True)
    text = body.get("yaml", load_yaml_text())   # fall back to file if no body
    try:
        data = parse_yaml(text)
        pdf_bytes = generate(data)
        filename = data.get("meta", {}).get("output_filename", "cv.pdf")
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception:
        tb = traceback.format_exc()
        return jsonify({"ok": False, "error": tb}), 500


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  CV Builder running →  http://localhost:{port}\n")
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
