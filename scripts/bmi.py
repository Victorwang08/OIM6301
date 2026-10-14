def compute_bmi(weight, height):
    """Compute the Body Mass Index (BMI) given weight and height."""
    bmi = weight / (height ** 2)
    return bmi


def classify_bmi(bmi):
    """Classify the BMI value into categories."""
    if bmi >= 30:
        category = "Obese"
    elif bmi >= 25:
        category = "Overweight"
    elif bmi >= 18.5:
        category = "Normal"
    else:
        category = "Underweight"
    return category
# return category is important because it allows the function to output the classification result based on the BMI value provided. 
# This enables other parts of the program to use this result for further processing or display.

def main():
    weight = float(input("Enter your weight in kg: "))
    height = float(input("Enter your height in meters: "))
    bmi_value = compute_bmi(weight, height)
    result = classify_bmi(bmi_value)
    print(f"Your BMI is {bmi_value:.2f}, which classifies you as {result}.")
# this is for testing purpose
if __name__ == "__main__":
    main()
# use this long one instead of simple main(). so you can get the functon and def in other file if you import this file. 