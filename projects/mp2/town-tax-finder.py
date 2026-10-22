import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import requests

    return mo, pl, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # MP2: Town Tax Finder
    """)
    return


app._unparsable_cell(
    r"""
    ## 1. The Question

    TODO: Who would use this tool, and what decision does it help them make?
    Write 2-3 sentences, in words someone outside this course would understand.
    """,
    column=None, disabled=False, hide_code=True, name="_"
)


@app.cell
def _():
    # This tool can help people who is looking to buy a house to find a house within budget and anual property tax within their expectation. The tool also helps them decide where to focus their house search, ranked from the cheapest tax bill to the most expensive, so they can narrow a whole county down to a short list of towns worth visiting.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. My Plan Before AI

    TODO: Open the API's address in your browser and read what comes back.
    Then write, in plain words, the steps you will take, in order (five lines or more).

    Then answer:
    - Which functions will your tool need? For each, what goes in and what comes out?
    - Which addresses will they request?
    - How will you know you have every record?
    - Which check will you use in section 6, and which two numbers should agree?

    Commit with the message: mp2: plan before AI
    """)
    return


@app.cell
def _():
    # 1. Open oim.zhili.dev/ma and oim.zhili.dev/docs first to see what fields the API returns.
    # 2. Request /ma/towns?county=Middlesex, and check the page info based on the pagination to make sure the code I wrote will be able to collected all info I need.
    # 3. For each town's dor_code, request /ma/towns/{dor_code}/history, and keep only the record where fiscal_year equals 2026.
    # 4. Keep towns where the average home value is at or under $700,000 and the average bill is at or under $8,000.
    # 5. Sort the towns that pass by average bill, cheapest first, build the table, and write a summary.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. Inputs

    Every input your tool needs (town name, API address, tax rate field, etc.) goes in one cell below.
    """)
    return


@app.cell
def _():
    county = "Middlesex"
    budget_dollars = 700000
    tax_limit_dollars = 8000
    fiscal_year = 2026
    api_base = "https://oim.zhili.dev"
    return budget_dollars, county, fiscal_year, tax_limit_dollars


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. The Work

    TODO: Define the functions you need, then write the code that calls them
    to collect your data into a result table.
    """)
    return


@app.cell
def _(budget_dollars, county, fiscal_year, requests, tax_limit_dollars):
    # Define a function to get all towns in the county.
    def get_towns(county_name):
        towns = []
        page = 1

        while True:
            response = requests.get(
                "https://oim.zhili.dev/ma/towns",
                params={
                    "county": county_name,
                    "per_page": 100,
                    "page": page
                },
                timeout=30
            )

            # Report an error if the HTTP request fails.
            # 如果网站请求失败，程序在这里停止并报告问题。
            response.raise_for_status()

            # Convert the JSON response into a Python dictionary.
            # 把网站返回的 JSON 转换成 Python 字典。
            data = response.json()

            # Use extend to add each town separately.
            # extend 把这一页的城镇逐个加入名单，
            # 避免用 append 把整页列表作为一个项目加入。
            towns.extend(data["items"])

            # Stop the loop if there are no more pages.
            if not data["pagination"]["has_next"]:
                break

            # Otherwise, move to the next page.
            page = page + 1

        # Double-check that we have all towns.
        if len(towns) != data["pagination"]["total"]:
            raise ValueError(
                "Town list incomplete. Check the request and run again."
            )

        return towns


    # Define a function to get town information for a given year.
    def get_year_data(town_code, year):
        response = requests.get(
            f"https://oim.zhili.dev/ma/towns/{town_code}/history",
            params={
                "from_year": year,
                "to_year": year
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        # Find the record for the requested fiscal year.
        # 找到与指定年份一致的记录。
        for record in data["years"]:
            if record["fiscal_year"] == year:
                return record

        # Return None if the requested year is not available.
        # 如果找不到，返回 None，表示没有该年份的数据。
        return None


    # Get all towns and filter them.
    towns = get_towns(county)

    # Store towns that meet both limits.
    results = []

    # Store towns that cannot be compared because of missing data.
    # 保存缺少数据、无法判断的城镇。
    missing_towns = []

    for town in towns:
        # Use the town code to request data for the selected year.
        record = get_year_data(town["dor_code"], fiscal_year)

        # If the year is missing, record the town name and skip it.
        if record is None:
            missing_towns.append(town["name"])
            continue

        # Read the average home value, residential tax rate,
        # and average annual tax bill from the same year's record.
        home_value = record["average_single_family_value_dollars"]
        tax_rate = record["residential_rate_per_thousand"]
        tax_bill = record["average_single_family_bill_dollars"]

        # Skip incomplete records instead of treating missing values as 0.
        if home_value is None or tax_rate is None or tax_bill is None:
            missing_towns.append(town["name"])
            continue

        # Add the town only if it meets BOTH limits.
        # 平均房屋价值不超过预算，且平均年度税单低于上限。
        if home_value <= budget_dollars and tax_bill < tax_limit_dollars:
            results.append({
                "Town": town["name"],
                "Average home value ($)": home_value,
                "Tax rate ($ per $1,000)": tax_rate,
                "Average annual bill ($)": tax_bill
            })


    # Show how many towns were checked, how many qualified,
    # and any missing data.
    print(
        f"Checked {len(towns)} towns in {county} County "
        f"for FY{fiscal_year}."
    )
    print(f"Found {len(results)} towns that meet both limits.")

    if len(missing_towns) > 0:
        print("Missing data: " + ", ".join(missing_towns))

    return (results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. The Answer

    TODO: Print your result table with `print` and f-strings, with the columns lined up.
    Then print one sentence that answers the question in section 1, with the numbers in it.
    Print the sentence from code with an f-string, so that it changes when the data does.
    """)
    return


@app.cell
def _(budget_dollars, county, fiscal_year, pl, results, tax_limit_dollars):
    # Create the summary and table.
    if len(results) > 0:
        # Sort the results by annual tax bill, lowest first.
        # 按平均年度税单从低到高排序。
        result_table = pl.DataFrame(results).sort(
            "Average annual bill ($)"
        )

        # Print the column headings with fixed widths.
        # < 表示左对齐，> 表示右对齐，数字表示这一列占多少个字符。
        print(
            f"{'Town':<20}"
            f"{'Home value ($)':>18}"
            f"{'Rate ($/1,000)':>18}"
            f"{'Annual bill ($)':>18}"
        )

        # Print a dividing line.
        print("-" * 74)

        # Print each town as one row.
        # named=True 让我们用列名读取每一行的数据。
        for _row in result_table.iter_rows(named=True):
            print(
                f"{_row['Town']:<20}"
                f"{_row['Average home value ($)']:>18,.0f}"
                f"{_row['Tax rate ($ per $1,000)']:>18.2f}"
                f"{_row['Average annual bill ($)']:>18,.0f}"
            )

        # Get the first row: the qualifying town with the lowest bill.
        cheapest = result_table.row(0, named=True)

        # Print a blank line before the conclusion.
        print()

        # Print one sentence that updates when the inputs or data change.
        # 用 f-string 打印一句包含实际数字的结论。
        print(
            f"In FY{fiscal_year}, {len(results)} towns in {county} County "
            f"have an average home value at or below ${budget_dollars:,.0f} "
            f"and an average annual tax bill below ${tax_limit_dollars:,.0f}; "
            f"among these qualifying towns, {cheapest['Town']} has the "
            f"lowest average annual bill of "
            f"${cheapest['Average annual bill ($)']:,.0f}, "
            f"with an average home value of "
            f"${cheapest['Average home value ($)']:,.0f}."
        )

    else:
        # Print a message if no towns qualify.
        print(
            f"In FY{fiscal_year}, no towns with complete data in "
            f"{county} County have both an average home value at or below "
            f"${budget_dollars:,.0f} and an average annual tax bill "
            f"below ${tax_limit_dollars:,.0f}."
        )
    return (cheapest,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. How I Know These Numbers Are Right

    TODO: Reach at least one result a second way, in this notebook, and show that the two agree.
    Write a cell that gets the same number from other fields, or open the raw reply in your
    browser and find each number of one row of your table there.

    For instance: an average bill is close to the average value times the tax rate divided by
    1,000; an order's total equals the sum of its lines; the number of records you collected
    equals the total the API reports.

    At least one of those checks runs as code, and shows both numbers.
    """)
    return


@app.cell
def _(cheapest):
    # Check the cheapest town's bill using home value × tax rate ÷ 1,000.
    print(f"Calculated bill: ${cheapest['Average home value ($)'] * cheapest['Tax rate ($ per $1,000)'] / 1000:,.2f}")
    print(f"API bill: ${cheapest['Average annual bill ($)']:,.2f}")
    return


@app.cell
def _():
    # There is a 39 cent difference because the API reports the bill in whole dollars. 
    # Displaying it with two decimal places only adds ".00"; it does not add precision. 
    # In this check, $4,952.388 rounds to $4,952, matching the API bill, 
    # the small difference is consistent with rounding to whole dollars.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 7. Working With the Agent

    TODO: Pick one piece of AI output you did not accept as-is. What did it give you, what did you
    change, and how did you know? Point to the commit or the cell.

    If the agent got it right the first time: What did you do to verify that? Pointing to your
    check in section 6 is enough.
    """)
    return


@app.cell
def _():
    # The code part, My agent got it right the first time. I checked in Section 6 by multiplying the average home value by the tax rate and dividing by 1,000. The calculated amount was $4,952.39, which matches the API bill of $4,952 when rounded to the nearest dollar.

    # Another thing is my agent initially used mo.ui.table() to display the results which I never seen this way of printing and the result does not match the instruction. Instructions in Section 5 required print and f-strings with aligned columns, so I asked the agent to revise the output code.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 8. Reading It Back

    TODO: Pick two functions in your notebook that your agent wrote or helped write. For each,
    write in your own words what goes in, what comes out, and one line you had to ask about.

    Then choose one change to what the tool does, such as another county, another week or
    another rule. Changing one value in your Inputs cell is enough. Write what you expect to
    change in the answer. Commit with the message: mp2: prediction

    Make the change, run it, and write what happened and whether it matched.
    """)
    return


@app.cell
def _():
    # Function 1: get_towns(county_name)
    # Input: the name of a county, such as "Middlesex".
    # Output: a list of all towns in that county.
    # It reads every page and checks that the number of towns is complete.
    # I asked why use.extend instead of .append, and noticed It adds each town to the list instead of adding the whole page as one item.

    # Function 2: get_year_data(town_code, year)
    # Inputs: a town's code and the fiscal year.
    # Output: that town's record for the selected year,
    # or None if the year is not available.
    # I asked about record["residential_rate_per_thousand"] because i do not see this key in the website and i noticed that This field comes from the history endpoint, not the town-list endpoint.
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 9. Going Further

    TODO: What you tried past the main task, what you found, and where it is in the notebook.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 10. Time Spent

    TODO: About how many hours this project took you outside class, as one number. It is not graded.
    """)
    return


if __name__ == "__main__":
    app.run()
