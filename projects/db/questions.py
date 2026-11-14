import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return mo, ask


@app.cell
def _():
    as_of = "2026-11-08"
    return (as_of,)


@app.cell
def _(mo, as_of):
    mo.md(f"""
    # Babson Bean Café: Business Questions

    As-of date: **{as_of}**

    All date-based questions will use this reference date.
    "Last month" means the last full calendar month before it:
    October 2026.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Answers

    The ten questions and their answers will be added here
    after the prediction has been committed.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## How I Know These Numbers Are Right

    Verification checks will be added after answering the questions.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Working With the Agent

    The collaboration and verification notes will be added here.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Reading It Back

    **Chosen business question:**
    What are revenue, cost, and profit for each menu category,
    including options?

    **What I am predicting:**
    Before answering this question, I am predicting how many
    rows the table joins will produce before grouping,
    as required by the assignment.

    **Prediction before answering:**

    I expect the joins will produce 3,364 rows before grouping.

    The CSV files have 1,932 selected-option records and 1,432
    order lines with no options. A line with options will appear
    once for each option. A line without options will still appear
    once because I will use a LEFT JOIN.

    So my prediction is 1,932 + 1,432 = 3,364 rows.
    Joining the product and option details should not add more
    rows because their IDs are unique.

    **Actual join count and explanation:** To be added after
    this prediction is committed.

    **Meaning of one final result row:** To be added after
    answering the question.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Going Further

    I plan to chart one answer with both axes titled.
    The chart and findings will be added here.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Time Spent

    To be replaced with the actual number of hours spent
    on the whole project outside class.
    """)
    return


if __name__ == "__main__":
    app.run()