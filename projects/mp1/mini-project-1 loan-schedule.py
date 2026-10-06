# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of project, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    *Who would use this, and what decision does it help them make? Two or three sentences, in words somebody outside this course would understand.*
    """)
    return


@app.cell
def _():
    # This tool is for housebuyers, who are choosing between the 15 years or a 30 years loan, to compare the monthly payment and total interest for both options. It will help poeple to decide whether lower monthly payments or lower overall interest costs better fit their budget and goals. 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these two questions:*

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*
    - *Which check will you use in section 6, and which two numbers should agree?*

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell
def _():
    # Plan: 
    # 1. enter loan amount $400,000 and the interest rate for 15 and 30 years. and change the rate from year-based to month-based.
    # 2. Use the formula provided to find out monthly payment for each plan and use a loop to calculate one month at a time. For each month, calculate the interst and how much of a payment pays back the money borrowed。
    # 3. update how much is still owed and add the month's interest to the total. round to 2 decimal places. and adjust the last payment stp make sure nothing left.
    # 4. put each month result in a table to compare. 
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your project from the Mini Project 1 page. If you chose your own project, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Your inputs.
    loan_amount = 400000
    return (loan_amount,)


@app.cell
def _():
    annual_rates = {30: 0.0703, 15: 0.0642}
    return (annual_rates,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(annual_rates, loan_amount):
    # Store the results for both loans
    loan_results = {}

    # Calculate each loan separately
    for _years, _annual_rate in annual_rates.items():

        # Convert years to months and annual rate to monthly rate
        _months = _years * 12
        _monthly_rate = _annual_rate / 12

        # Calculate the regular monthly payment
        _monthly_payment = round(
            loan_amount * _monthly_rate
            / (1 - (1 + _monthly_rate) ** (-_months)),
            2
        )

        # Start this loan with the full balance
        _balance = loan_amount
        _total_interest = 0
        _schedule = []

        # Calculate one month at a time
        for _month in range(1, _months + 1):

            # Interest is based on the balance still owed
            _interest = round(_balance * _monthly_rate, 2)

            # Adjust the final payment to pay off the loan
            if _month == _months:
                _payment = round(_balance + _interest, 2)
            else:
                _payment = _monthly_payment

            # Find how much of the payment repays principal
            _principal_paid = round(_payment - _interest, 2)

            # Update the balance and total interest
            _balance = round(_balance - _principal_paid, 2)
            _total_interest = round(_total_interest + _interest, 2)

            # Save this month's results as one row
            _schedule.append({
                "month": _month,
                "payment": _payment,
                "interest": _interest,
                "principal_paid": _principal_paid,
                "balance": _balance
            })

        # Save the finished results for this loan
        loan_results[_years] = {
            "monthly_payment": _monthly_payment,
            "total_interest": _total_interest,
            "schedule": _schedule
        }
    return (loan_results,)


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(loan_results):
    # Print a summary table
    print("LOAN COMPARISON (USD)")
    print(f"{'Years':<8}{'Monthly payment':>20}{'Total interest':>20}")

    for _years, _result in loan_results.items():
        print(
            f"{_years:<8}"
            f"{_result['monthly_payment']:>20,.2f}"
            f"{_result['total_interest']:>20,.2f}"
        )

    # Print the monthly schedule for each loan
    for _years, _result in loan_results.items():
        print()
        print(f"{_years}-YEAR LOAN SCHEDULE (USD)")
        print(
            f"{'Month':<8}"
            f"{'Payment':>14}"
            f"{'Interest':>14}"
            f"{'Principal':>14}"
            f"{'Balance':>16}"
        )

        for _row in _result["schedule"]:
            print(
                f"{_row['month']:<8}"
                f"{_row['payment']:>14,.2f}"
                f"{_row['interest']:>14,.2f}"
                f"{_row['principal_paid']:>14,.2f}"
                f"{_row['balance']:>16,.2f}"
            )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _(loan_amount, loan_results):
    for _years, _result in loan_results.items():

        # Add up the principal repaid each month
        _total_principal = 0

        for _row in _result["schedule"]:
            _total_principal = _total_principal + _row["principal_paid"]

        _total_principal = round(_total_principal, 2)

        # Show both numbers and compare them
        print(f"{_years}-year loan")
        print(f"Total principal repaid: ${_total_principal:,.2f}")
        print(f"Original loan amount: ${loan_amount:,.2f}")
        print(f"Do they match? {_total_principal == loan_amount}")
        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell
def _():
    # The agent gave me the calculation code in Section 4. Before accepting it, I asked why the balance started at the loan amount, how it decreased each month, why the loop used months + 1, and how the last payment cleared the balance. After understanding these steps, I kept the calculation code unchanged. In Section 6, I checked that the principal repaid added up to the original $400,000 for both loans, and both checks returned True.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


@app.cell
def _():
    extra_payment = 200
    return (extra_payment,)


@app.cell
def _(annual_rates, extra_payment, loan_amount, loan_results):
    print("PAYING EXTRA EACH MONTH")
    print(f"Extra monthly payment: ${extra_payment:,.2f}")
    print()

    for _years, _annual_rate in annual_rates.items():

        # Start again with the original loan amount
        _balance = loan_amount
        _monthly_rate = _annual_rate / 12
        _month = 0
        _total_interest = 0

        # Add the extra amount to the regular monthly payment
        _new_payment = round(
            loan_results[_years]["monthly_payment"] + extra_payment,
            2
        )

        # Keep going while there is money left to repay
        while _balance > 0:
            _month = _month + 1
            _interest = round(_balance * _monthly_rate, 2)

            # Do not pay more than the remaining balance plus interest
            _payment = min(
                _new_payment,
                round(_balance + _interest, 2)
            )

            _principal_paid = round(_payment - _interest, 2)
            _balance = round(_balance - _principal_paid, 2)
            _total_interest = round(_total_interest + _interest, 2)

        # Compare with the original loan
        _months_saved = _years * 12 - _month
        _interest_saved = round(
            loan_results[_years]["total_interest"] - _total_interest,
            2
        )

        print(f"{_years}-year loan")
        print(f"New regular monthly payment: ${_new_payment:,.2f}")
        print(f"Months needed to repay: {_month}")
        print(f"Months saved: {_months_saved}")
        print(f"Total interest with extra payments: ${_total_interest:,.2f}")
        print(f"Interest saved: ${_interest_saved:,.2f}")
        print()
    return


if __name__ == "__main__":
    app.run()
