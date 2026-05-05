from datetime import date

today = date.today()
day_name = today.strftime("%A")

if today.weekday() < 5:
    print(f"Today is {day_name} — it's a Weekday.")
else:
    print(f"Today is {day_name} — it's a Weekend.")