import bmi

people = [
    {"name": "Alice", "height": 1.75, "weight": 70},
    {"name": "Bob", "height": 1.80, "weight": 80},
    {"name": "Charlie", "height": 1.68, "weight": 65},
    {"name": "Diana", "height": 1.62, "weight": 55},
    {"name": "Ethan", "height": 1.85, "weight": 90},
    {"name": "Fiona", "height": 1.70, "weight": 60},
    {"name": "George", "height": 1.78, "weight": 75},
    {"name": "Hannah", "height": 1.65, "weight": 58},
    {"name": "Ian", "height": 1.72, "weight": 68},
    {"name": "Julia", "height": 1.60, "weight": 52},
]

for person in people:
    weight = person["weight"]
    height = person["height"]
    bmi_value = bmi.compute_bmi(weight, height)
    category = bmi.classify_bmi(bmi_value)
    print(f"{person['name']} has a BMI of {bmi_value:.2f}, which classifies them as {category}.")
