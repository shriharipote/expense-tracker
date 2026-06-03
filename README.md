# 💰 Personal Expense Tracker

A Python-based expense tracker with both CLI and Web UI support.

## Features
- Add & delete expenses
- View monthly summary
- Category-wise breakdown with bar chart
- Export all data to CSV
- Supports CLI and Web (Flask)

## Tech Stack
- Python 3
- Flask (web framework)
- CSV (data storage)
- Vanilla JS + HTML/CSS (frontend)

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Web UI
python app.py

# 3. Run CLI
python app.py cli
```

Then open http://localhost:5000 in your browser for the web UI.

## Project Structure
```
expense_tracker/
├── app.py              # Main app (Flask routes + CLI logic)
├── expenses.csv        # Auto-created data file
├── requirements.txt
└── templates/
    └── index.html      # Web UI
```

## Categories
Food, Transport, Shopping, Bills, Health, Entertainment, Education, Other

---
Built by Shrihari Pote | github.com/shriharipote
