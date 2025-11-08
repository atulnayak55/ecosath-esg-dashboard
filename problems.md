# Current Focus & Open Issues

## Active Focus
- Launch the new Aurora Renewables sustainability site (`index.html`) that highlights emissions, social, and governance pillars for a one-year-old company.
- Ensure the FastAPI simulator (`api/main.py`) keeps generating messy+clean ESG datasets and serves them to the front-end.
- Wire the front-end cards/charts so they pull interactive data from the running FastAPI instance and surface insights.

## ✅ Fixed Issues
1. **FastAPI running**: Confirmed `http://127.0.0.1:8000` is up, CORS middleware enabled, datasets refreshing every 5 minutes.
2. **Static server stable**: Running on port 5500 in background terminal.
3. **Error banner added**: Updated `fetchDataset()` to show visible banner + update status tag when API is unreachable.
4. **JavaScript syntax error**: Fixed `Unexpected token ']'` error in governance chart layout definition (line 877).

## 🔍 Remaining Issues
- **Need to verify data loads**: After fixing syntax error, need to reload page and confirm fetch requests reach FastAPI and charts render

## Next Steps
1. Open browser DevTools (F12) and check Console tab for JavaScript errors
2. Check Network tab to see if API requests are being made and what status they return
3. If no requests appear, check if `DOMContentLoaded` event is firing correctly
