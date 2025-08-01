# Reefing Memory Dashboard

## Usage

1. Start the app:
   ```bash
   python src/app.py
   ```
2. Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

## Features

- Responsive dashboard for water parameters (Chart.js)
- Floating elements list with color-coded progress bars and percentage text
- Modal for adding new entries (with drag/click bar input, previous/next navigation)
- Data overwrite: saving an entry with an existing date will update (not duplicate) the record
- Weekly and real-time charts for PH, ORP, Nitrate, Phosphate, Calcium, Magnesium, Alkalinity
- UI/UX polish: custom fonts, spacing, mobile/desktop layout, stable modal navigation

## Project Structure

- `src/app.py`: Flask backend, API endpoints, data overwrite logic
- `src/chart_data_store.py`: Data load/save helpers
- `src/data.json`: Water parameter data
- `src/templates/index.html`: Main dashboard, charts, modal, UI logic
- `src/static/`: Static files (future use)

## Next Steps

- Add an edit page for modifying/saving data
- Add authentication if needed
- Further UI/UX improvements

---
For questions or feature requests, ask GitHub Copilot!
