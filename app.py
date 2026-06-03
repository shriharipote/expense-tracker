"""
Personal Expense Tracker
Supports both CLI and Web UI (Flask)
Data stored in CSV file
"""

import csv
import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
import io

app = Flask(__name__)

CSV_FILE = "expenses.csv"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Education", "Other"]
FIELDNAMES = ["id", "date", "amount", "category", "description"]


# ─── CSV Helpers ────────────────────────────────────────────────────────────────

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_expenses():
    init_csv()
    with open(CSV_FILE, "r", newline="") as f:
        return list(csv.DictReader(f))


def write_expenses(expenses):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def next_id(expenses):
    if not expenses:
        return 1
    return max(int(e["id"]) for e in expenses) + 1


# ─── Core Logic ─────────────────────────────────────────────────────────────────

def add_expense(amount, category, description, date=None):
    expenses = read_expenses()
    date = date or datetime.today().strftime("%Y-%m-%d")
    expense = {
        "id": next_id(expenses),
        "date": date,
        "amount": round(float(amount), 2),
        "category": category,
        "description": description
    }
    expenses.append(expense)
    write_expenses(expenses)
    return expense


def delete_expense(expense_id):
    expenses = read_expenses()
    new = [e for e in expenses if str(e["id"]) != str(expense_id)]
    if len(new) == len(expenses):
        return False
    write_expenses(new)
    return True


def get_monthly_summary(year=None, month=None):
    expenses = read_expenses()
    now = datetime.today()
    year = year or now.year
    month = month or now.month

    filtered = [
        e for e in expenses
        if datetime.strptime(e["date"], "%Y-%m-%d").year == year
        and datetime.strptime(e["date"], "%Y-%m-%d").month == month
    ]

    total = sum(float(e["amount"]) for e in filtered)
    by_category = {}
    for e in filtered:
        cat = e["category"]
        by_category[cat] = round(by_category.get(cat, 0) + float(e["amount"]), 2)

    return {
        "year": year,
        "month": month,
        "total": round(total, 2),
        "by_category": by_category,
        "expenses": filtered
    }


# ─── Web Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)


@app.route("/api/expenses", methods=["GET"])
def api_get_expenses():
    return jsonify(read_expenses())


@app.route("/api/expenses", methods=["POST"])
def api_add_expense():
    data = request.json
    try:
        expense = add_expense(
            amount=data["amount"],
            category=data["category"],
            description=data.get("description", ""),
            date=data.get("date")
        )
        return jsonify({"success": True, "expense": expense})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def api_delete_expense(expense_id):
    success = delete_expense(expense_id)
    return jsonify({"success": success})


@app.route("/api/summary")
def api_summary():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    return jsonify(get_monthly_summary(year, month))


@app.route("/api/export")
def api_export():
    expenses = read_expenses()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(expenses)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="expenses.csv"
    )


# ─── CLI Interface ───────────────────────────────────────────────────────────────

def cli():
    init_csv()
    print("\n💰 Expense Tracker CLI")
    print("=" * 35)

    while True:
        print("\n1. Add Expense")
        print("2. Delete Expense")
        print("3. Monthly Summary")
        print("4. List All Expenses")
        print("5. Export to CSV")
        print("6. Exit")
        choice = input("\nChoice: ").strip()

        if choice == "1":
            try:
                amount = float(input("Amount (₹): "))
                print("Categories:", ", ".join(CATEGORIES))
                category = input("Category: ").strip().capitalize()
                if category not in CATEGORIES:
                    category = "Other"
                description = input("Description: ").strip()
                e = add_expense(amount, category, description)
                print(f"✅ Added: ₹{e['amount']} - {e['category']} ({e['date']})")
            except ValueError:
                print("❌ Invalid amount.")

        elif choice == "2":
            expenses = read_expenses()
            if not expenses:
                print("No expenses found.")
            else:
                for e in expenses[-10:]:
                    print(f"  [{e['id']}] ₹{e['amount']} - {e['category']} - {e['description']} ({e['date']})")
                eid = input("Enter ID to delete: ").strip()
                if delete_expense(eid):
                    print("✅ Deleted.")
                else:
                    print("❌ ID not found.")

        elif choice == "3":
            now = datetime.today()
            year = input(f"Year [{now.year}]: ").strip() or now.year
            month = input(f"Month [{now.month}]: ").strip() or now.month
            summary = get_monthly_summary(int(year), int(month))
            print(f"\n📊 Summary for {summary['month']}/{summary['year']}")
            print(f"   Total: ₹{summary['total']}")
            print("   By Category:")
            for cat, amt in summary["by_category"].items():
                print(f"     {cat}: ₹{amt}")

        elif choice == "4":
            expenses = read_expenses()
            if not expenses:
                print("No expenses yet.")
            else:
                for e in expenses:
                    print(f"  [{e['id']}] {e['date']} | ₹{e['amount']} | {e['category']} | {e['description']}")

        elif choice == "5":
            print(f"✅ Data already in: {os.path.abspath(CSV_FILE)}")

        elif choice == "6":
            print("Bye! 👋")
            break
        else:
            print("Invalid choice.")


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        cli()
    else:
        print("🌐 Starting web server at http://localhost:5000")
        app.run(debug=True)
