from datetime import date
import matplotlib.pyplot as plt
from db_connection import get_connection
from sklearn.linear_model import LinearRegression
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def get_or_create_user():
    conn = get_connection()
    cur = conn.cursor()
    name = Prompt.ask("Enter your name")
    cur.execute("SELECT user_id FROM users WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        city = Prompt.ask("Enter your city")
        cur.execute("INSERT INTO users (name, city) VALUES (%s, %s)", (name, city))
        conn.commit()
        user_id = cur.lastrowid
        console.print(f"[bold green]New user '{name}' created.[/bold green]")
    cur.close()
    conn.close()
    return user_id, name


def add_log(user_id):
    console.print(Panel("Add Today's Log", style="bold green"))
    log_date = Prompt.ask("Date (YYYY-MM-DD)", default="")
    if log_date == "":
        log_date = date.today().isoformat()

    transport_mode = Prompt.ask(
        "Transport mode", choices=["walk", "cycle", "bus", "bike", "car"]
    )
    distance_km = float(Prompt.ask("Distance travelled (km)", default="0"))
    electricity_units = float(Prompt.ask("Electricity used (units/kWh)", default="0"))
    meal_type = Prompt.ask(
        "Main meal type", choices=["veg", "non-veg", "vegan"]
    )
    waste_kg = float(Prompt.ask("Waste generated (kg)", default="0"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO daily_log
        (user_id, log_date, transport_mode, distance_km, electricity_units, meal_type, waste_kg)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_id, log_date, transport_mode, distance_km, electricity_units, meal_type, waste_kg))
    conn.commit()
    console.print(f"[bold green]Log added successfully with ID {cur.lastrowid}.[/bold green]")
    cur.close()
    conn.close()


def delete_log(user_id):
    console.print(Panel("Delete a Log", style="bold red"))
    view_logs(user_id)
    log_id = Prompt.ask("Enter Log ID to delete")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM daily_log WHERE log_id = %s AND user_id = %s", (log_id, user_id))
    if cur.fetchone() is None:
        console.print("[bold red]No such log found for you.[/bold red]")
    else:
        confirm = Prompt.ask("Are you sure you want to delete this entry?", choices=["y", "n"])
        if confirm == "y":
            cur.execute("DELETE FROM daily_log WHERE log_id = %s", (log_id,))
            conn.commit()
            console.print("[bold green]Log deleted successfully.[/bold green]")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")
    cur.close()
    conn.close()


def update_log(user_id):
    console.print(Panel("Modify a Log", style="bold cyan"))
    view_logs(user_id)
    log_id = Prompt.ask("Enter Log ID to modify")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM daily_log WHERE log_id = %s AND user_id = %s", (log_id, user_id))
    row = cur.fetchone()
    if row is None:
        console.print("[bold red]No such log found for you.[/bold red]")
        cur.close()
        conn.close()
        return

    console.print("[dim]Leave a field blank to keep it unchanged.[/dim]")
    transport_mode = Prompt.ask("Transport mode", default=row[3])
    distance_km = Prompt.ask("Distance km", default=str(row[4]))
    distance_km = float(distance_km)
    electricity_units = Prompt.ask("Electricity units", default=str(row[5]))
    electricity_units = float(electricity_units)
    meal_type = Prompt.ask("Meal type", default=row[6])
    waste_kg = Prompt.ask("Waste kg", default=str(row[7]))
    waste_kg = float(waste_kg)

    cur.execute("""
        UPDATE daily_log
        SET transport_mode = %s, distance_km = %s, electricity_units = %s,
            meal_type = %s, waste_kg = %s
        WHERE log_id = %s
    """, (transport_mode, distance_km, electricity_units, meal_type, waste_kg, log_id))
    conn.commit()
    console.print("[bold green]Log updated successfully.[/bold green]")
    cur.close()
    conn.close()


def search_log(user_id):
    console.print(Panel("Search Logs", style="bold magenta"))
    choice = Prompt.ask(
        "Search by",
        choices=["date", "transport", "meal", "range"],
    )

    conn = get_connection()
    cur = conn.cursor()

    if choice == "date":
        d = Prompt.ask("Enter date (YYYY-MM-DD)")
        cur.execute("SELECT * FROM daily_log WHERE user_id=%s AND log_date=%s", (user_id, d))
    elif choice == "transport":
        mode = Prompt.ask("Enter transport mode")
        cur.execute("SELECT * FROM daily_log WHERE user_id=%s AND transport_mode=%s", (user_id, mode))
    elif choice == "meal":
        meal = Prompt.ask("Enter meal type")
        cur.execute("SELECT * FROM daily_log WHERE user_id=%s AND meal_type=%s", (user_id, meal))
    elif choice == "range":
        start = Prompt.ask("Start date (YYYY-MM-DD)")
        end = Prompt.ask("End date (YYYY-MM-DD)")
        cur.execute("""SELECT * FROM daily_log
                       WHERE user_id=%s AND log_date BETWEEN %s AND %s
                       ORDER BY log_date""", (user_id, start, end))

    results = cur.fetchall()
    if not results:
        console.print("[yellow]No matching records found.[/yellow]")
    else:
        print_log_table(results)
    cur.close()
    conn.close()


def view_logs(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM daily_log WHERE user_id = %s ORDER BY log_date", (user_id,))
    rows = cur.fetchall()
    print_log_table(rows)
    cur.close()
    conn.close()


def print_log_table(rows):
    if not rows:
        console.print("[yellow]No logs to display.[/yellow]")
        return
    table = Table(show_header=True, header_style="bold green")
    table.add_column("ID")
    table.add_column("Date")
    table.add_column("Transport")
    table.add_column("Dist (km)")
    table.add_column("Elec")
    table.add_column("Meal")
    table.add_column("Waste (kg)")
    for r in rows:
        table.add_row(str(r[0]), str(r[2]), r[3], str(r[4]), str(r[5]), r[6], str(r[7]))
    console.print(table)


def get_monthly_totals(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(log_date, '%Y-%m') AS month,
               SUM(distance_km * ef1.factor_per_unit) AS transport_co2,
               SUM(electricity_units * ef2.factor_per_unit) AS elec_co2,
               SUM(waste_kg * ef3.factor_per_unit) AS waste_co2
        FROM daily_log dl
        JOIN emission_factors ef1 ON dl.transport_mode = ef1.category
        JOIN emission_factors ef2 ON ef2.category = 'electricity'
        JOIN emission_factors ef3 ON ef3.category = 'waste'
        WHERE dl.user_id = %s
        GROUP BY month
        ORDER BY month
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def monthly_report(user_id):
    rows = get_monthly_totals(user_id)
    if not rows:
        console.print("[yellow]No data available for report.[/yellow]")
        return

    table = Table(title="Monthly CO2 Report (kg CO2)", header_style="bold green")
    table.add_column("Month")
    table.add_column("Transport")
    table.add_column("Electricity")
    table.add_column("Waste")
    table.add_column("Total")
    for month, t, e, w in rows:
        t, e, w = t or 0, e or 0, w or 0
        total = t + e + w
        table.add_row(month, f"{t:.2f}", f"{e:.2f}", f"{w:.2f}", f"{total:.2f}")
    console.print(table)


def eco_streak(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT log_date,
               (distance_km * (SELECT factor_per_unit FROM emission_factors WHERE category = transport_mode))
               + (electricity_units * 0.82) + (waste_kg * 0.50) AS daily_co2
        FROM daily_log
        WHERE user_id = %s
        ORDER BY log_date
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        console.print("[yellow]No data yet to calculate streak.[/yellow]")
        return

    values = [r[1] for r in rows]
    avg_co2 = sum(values) / len(values)

    current_streak = 0
    best_streak = 0
    for v in values:
        if v < avg_co2:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0

    console.print(f"Your average daily CO2: [bold]{avg_co2:.2f} kg[/bold]")
    console.print(f"Your best Eco Streak: [bold green]{best_streak} day(s)[/bold green]")


def visualize_trends(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT log_date,
               (distance_km * (SELECT factor_per_unit FROM emission_factors WHERE category = transport_mode))
               + (electricity_units * 0.82) + (waste_kg * 0.50) AS daily_co2
        FROM daily_log
        WHERE user_id = %s
        ORDER BY log_date
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        console.print("[yellow]No data to visualize yet.[/yellow]")
        return

    dates = [str(r[0]) for r in rows]
    co2_values = [r[1] for r in rows]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, co2_values, marker='o', color='green')
    plt.title("Daily CO2 Emissions Over Time")
    plt.xlabel("Date")
    plt.ylabel("CO2 (kg)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            SUM(distance_km * (SELECT factor_per_unit FROM emission_factors WHERE category = transport_mode)) AS transport,
            SUM(electricity_units * 0.82) AS electricity,
            SUM(waste_kg * 0.50) AS waste
        FROM daily_log WHERE user_id = %s
    """, (user_id,))
    cat_row = cur.fetchone()
    cur.close()
    conn.close()

    categories = ["Transport", "Electricity", "Waste"]
    totals = [v or 0 for v in cat_row]

    plt.figure(figsize=(6, 4))
    plt.bar(categories, totals, color=['#4CAF50', '#FF9800', '#795548'])
    plt.title("CO2 Contribution by Category")
    plt.ylabel("CO2 (kg)")
    plt.tight_layout()
    plt.show()


def what_if_simulator(user_id):
    console.print(Panel("What If Simulator", style="bold blue"))
    km_per_week = float(Prompt.ask("How many km/week do you currently drive by car"))
    days_switch = int(Prompt.ask("How many days/week could you switch to cycling instead"))

    car_factor = 0.21
    weekly_saving = (km_per_week / 5) * days_switch * car_factor
    monthly_saving = weekly_saving * 4.3

    console.print(
        f"Switching {days_switch} day(s)/week to cycling could save you approximately "
        f"[bold green]{monthly_saving:.2f} kg[/bold green] of CO2 per month."
    )


def predict_next_month(user_id):
    console.print(Panel("AI Prediction: Next Month's CO2", style="bold magenta"))
    rows = get_monthly_totals(user_id)

    if len(rows) < 2:
        console.print(
            "[yellow]Not enough monthly data yet. Log activity across at least two "
            "different months before requesting a prediction.[/yellow]"
        )
        return

    totals = []
    for month, t, e, w in rows:
        t, e, w = t or 0, e or 0, w or 0
        totals.append(t + e + w)

    X = np.array(range(len(totals))).reshape(-1, 1)
    y = np.array(totals)

    model = LinearRegression()
    model.fit(X, y)

    next_index = np.array([[len(totals)]])
    prediction = model.predict(next_index)[0]
    prediction = max(prediction, 0)

    last_actual = totals[-1]
    trend_color = "green" if prediction < last_actual else "red"
    trend_word = "lower" if prediction < last_actual else "higher"

    console.print(
        f"Based on your last {len(totals)} months, your predicted CO2 for next month is "
        f"[bold {trend_color}]{prediction:.2f} kg[/bold {trend_color}], "
        f"which is {trend_word} than your most recent month ({last_actual:.2f} kg)."
    )
    console.print(
        "[dim]This estimate uses a simple linear regression model (scikit-learn) "
        "fitted on your past monthly totals, and improves as you log more months.[/dim]"
    )


def show_menu():
    menu_text = (
        "[bold]1[/bold]. Add Data (new daily log)\n"
        "[bold]2[/bold]. Delete Data (remove a log)\n"
        "[bold]3[/bold]. Modify Data (update a log)\n"
        "[bold]4[/bold]. Search Data (find specific logs)\n"
        "[bold]5[/bold]. View All My Logs\n"
        "[bold]6[/bold]. Monthly CO2 Report\n"
        "[bold]7[/bold]. Eco Streak Calculator\n"
        "[bold]8[/bold]. Visualize Trends (charts)\n"
        "[bold]9[/bold]. What If Simulator\n"
        "[bold]10[/bold]. AI Prediction (next month CO2)\n"
        "[bold]11[/bold]. Exit"
    )
    console.print(Panel(menu_text, title="[bold green]EcoLocator Menu[/bold green]", border_style="green"))


def main():
    user_id, name = get_or_create_user()
    console.print(f"\n[bold green]Welcome to EcoLocator, {name}.[/bold green]\n")

    while True:
        show_menu()
        choice = Prompt.ask("Enter your choice", choices=[str(i) for i in range(1, 12)])

        if choice == "1":
            add_log(user_id)
        elif choice == "2":
            delete_log(user_id)
        elif choice == "3":
            update_log(user_id)
        elif choice == "4":
            search_log(user_id)
        elif choice == "5":
            view_logs(user_id)
        elif choice == "6":
            monthly_report(user_id)
        elif choice == "7":
            eco_streak(user_id)
        elif choice == "8":
            visualize_trends(user_id)
        elif choice == "9":
            what_if_simulator(user_id)
        elif choice == "10":
            predict_next_month(user_id)
        elif choice == "11":
            console.print("[bold green]Thank you for using EcoLocator. Stay green.[/bold green]")
            break


if __name__ == "__main__":
    main()
