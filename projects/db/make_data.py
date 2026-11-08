import csv
import random
from pathlib import Path
from datetime import datetime, timedelta

# Use a fixed seed so each run produces the same data.
random.seed(42)

# Save CSV files in the data folder next to this script.
data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)


def save_csv(filename, rows):
    with (data_dir / filename).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"{filename}: {len(rows)} rows")


def dollars(cents):
    return f"{cents / 100:.2f}"


# 1. Members
members = []

for member_id in range(1, 41):
    members.append({
        "member_id": member_id,
        "first_name": f"Member{member_id}",
        "mobile_number": f"202555{100 + member_id:04d}",
        "email": (
            f"member{member_id}@example.com"
            if member_id % 4 != 0 else ""
        ),
        "join_date": (
            datetime(2025, 9, 1) + timedelta(days=member_id)
        ).date().isoformat(),
        "points_balance": random.randint(0, 500),
    })


# 2. Products
# Prices and costs below are in cents.
menu = [
    ("Espresso", "coffee", 300, 90),
    ("Americano", "coffee", 350, 100),
    ("Latte", "coffee", 500, 180),
    ("Cappuccino", "coffee", 475, 170),
    ("Mocha", "coffee", 550, 210),
    ("Cold Brew", "coffee", 450, 140),
    ("Black Tea", "tea", 300, 70),
    ("Green Tea", "tea", 325, 80),
    ("Chai Latte", "tea", 500, 180),
    ("Matcha Latte", "tea", 550, 220),
    ("Croissant", "food", 375, 150),
    ("Blueberry Muffin", "food", 350, 130),
    ("Bagel", "food", 300, 110),
    ("Breakfast Sandwich", "food", 650, 280),
    ("Cookie", "food", 250, 90),
    ("Hot Chocolate", "other", 400, 150),
    ("Bottled Water", "other", 200, 60),
    ("Orange Juice", "other", 350, 140),
    ("Seasonal Tea", "tea", 400, 120),
    ("Seasonal Brownie", "food", 450, 180),
]

products = []

for product_id, (name, category, price, cost) in enumerate(menu, 1):
    products.append({
        "product_id": product_id,
        "product_name": name,
        "category": category,
        "price": dollars(price),
        "cost": dollars(cost),
        "available_today": product_id != 20,
    })


# 3. Options
option_menu = [
    ("Extra Shot", 100, 30),
    ("Oat Milk", 75, 30),
    ("Soy Milk", 50, 25),
    ("Almond Milk", 75, 35),
    ("Vanilla Syrup", 50, 10),
    ("Caramel Syrup", 50, 10),
    ("Whipped Cream", 50, 15),
    ("Cinnamon", 0, 5),
]

options = []

for option_id, (name, price, cost) in enumerate(option_menu, 1):
    options.append({
        "option_id": option_id,
        "option_name": name,
        "price": dollars(price),
        "cost": dollars(cost),
    })


# 4–7. Orders, order lines, line options and payments
orders = []
order_lines = []
line_options = []
payments = []

# Fixed reference date for reproducible project data.
reference_date = datetime(2026, 11, 8)

for order_id in range(1, 1001):
    order_time = reference_date - timedelta(
        days=random.randint(1, 180)
    )
    order_time = order_time.replace(
        hour=random.randint(7, 18),
        minute=random.randint(0, 59),
    )

    # Members 37–40 have never ordered.
    # A blank member_id represents a non-member.
    member_id = (
        random.randint(1, 36) if random.random() < 0.75 else ""
    )

    orders.append({
        "order_id": order_id,
        "order_datetime": order_time.isoformat(sep=" "),
        "member_id": member_id,
        "channel": random.choice(["counter", "app"]),
    })

    order_total = 0

    for _ in range(random.randint(1, 4)):
        line_id = len(order_lines) + 1

        # Products 19 and 20 have no sales.
        product_id = random.randint(1, 18)
        name, category, current_price, cost = menu[product_id - 1]
        quantity = random.randint(1, 3)

        # Some older purchases had a slightly lower price.
        unit_price = current_price
        if order_time < datetime(2026, 9, 1):
            unit_price -= 25

        order_lines.append({
            "line_id": line_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price_charged": dollars(unit_price),
        })

        selected_options = []

        if category in ["coffee", "tea"]:
            # At most one milk choice.
            if random.random() < 0.4:
                selected_options.append(random.choice([2, 3, 4]))

            # Between zero and two other options, without duplicates.
            selected_options += random.sample(
                [1, 5, 6, 7, 8],
                k=random.randint(0, 2),
            )

        option_total = 0

        for option_id in selected_options:
            option_price = option_menu[option_id - 1][1]
            option_total += option_price

            line_options.append({
                "line_id": line_id,
                "option_id": option_id,
                "unit_price_charged": dollars(option_price),
            })

        # Each option is charged once per unit on the line.
        order_total += quantity * (unit_price + option_total)

    # Some members pay partly with points.
    points_amount = 0

    if member_id != "" and random.random() < 0.3:
        points_amount = random.randint(1, min(300, order_total - 1))

        payments.append({
            "payment_id": len(payments) + 1,
            "order_id": order_id,
            "method": "points",
            "amount": dollars(points_amount),
        })

    # Pay the remaining amount using another method.
    payment_method = (
        "app" if orders[-1]["channel"] == "app"
        else random.choice(["cash", "card"])
    )

    payments.append({
        "payment_id": len(payments) + 1,
        "order_id": order_id,
        "method": payment_method,
        "amount": dollars(order_total - points_amount),
    })


# Write all seven CSV files.
save_csv("members.csv", members)
save_csv("products.csv", products)
save_csv("options.csv", options)
save_csv("orders.csv", orders)
save_csv("order_lines.csv", order_lines)
save_csv("line_options.csv", line_options)
save_csv("payments.csv", payments)

print("Done! All seven CSV files have been created.")