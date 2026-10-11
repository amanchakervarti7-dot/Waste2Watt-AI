WASTE2WATT AI — ENHANCED STARTER (Windows)

RUN:
1. Extract this ZIP.
2. Open the extracted Waste2Watt_AI_Project folder.
3. Click the File Explorer address bar, type cmd, press Enter.
4. Run these commands one by one:

   py -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   python app.py

5. Open http://127.0.0.1:5000

FEATURES:
- Dashboard with Flask backend integration
- Smart bin add and persistent JSON data
- Smart collection alert thresholds (75% pickup, 90% critical)
- Enhanced Waste Hotspots page with interactive schematic map markers and live-from-demo-data priority queue
- Enhanced AI Analytics page with illustrative trend visualization and transparent rule-based pickup forecast
- Enhanced Collection Route Planner with pickup ordering and route CSV export
- CSV inventory report export

HONEST LIMITATIONS:
- Map points and chart trend are illustrative demo data, not live GPS/municipal data.
- The pickup forecast is rule-based; there is no trained machine-learning model.
- No physical IoT sensors, authentication, or production database is configured.
- AWS deployment is not done by this local ZIP; it is the next step.
- AWS services can incur charges; review costs before creating resources.
