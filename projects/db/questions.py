import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb

    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, mo


@app.cell
def _():
    as_of = "2026-11-08"
    return (as_of,)


@app.cell(hide_code=True)
def _(as_of, mo):
    mo.md(f"""
    # Babson Bean Café

    As-of date: **{as_of}**

    All date-based questions will use this reference date.
    "Last month" means the last full calendar month before it:
    October 2026.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. Answers 10 Questions

    1. The three best-selling products last month, by units.
    2. Revenue, cost and margin by menu category, with what the options earned counted in, each option under the category of the product on its line. (three tables or more)
    3. For each member: the number of orders, the total spent and the average order, keeping the members whose total spent is above the members' average. (three tables or more)
    4. Every order's payments checked against its total, and a list of the orders where they do not match. (three tables or more) (checks a rule)
    5. The members who joined and have never ordered.
    6. The share of orders paid at least partly with points, for each month.
    7. The products, available today or not, that have not sold in the last 60 days.
    8. For each coffee and tea product, the average number of options on its lines, counting a line with no options as zero. (three tables or more)
    9. Which three pairs of products are most often bought together? — My Own Question
    Count each pair once per order, regardless of quantities.
    10. How many days pass between purchases, on average, for each returning member? — My Own Question
    Include members with at least two orders and measure the time between consecutive orders.
    """)
    return


@app.cell
def _(as_of, ask, mo):
    q1 = ask(f"""
        SELECT
            p.product_name,
            SUM(ol.quantity) AS units_sold
        FROM orders AS o
        JOIN order_lines AS ol
            ON o.order_id = ol.order_id
        JOIN products AS p
            ON ol.product_id = p.product_id
        WHERE
            o.order_datetime >=
                DATE_TRUNC('month', DATE '{as_of}')
                - INTERVAL '1 month'
            AND o.order_datetime <
                DATE_TRUNC('month', DATE '{as_of}')
        GROUP BY
            p.product_id,
            p.product_name
        ORDER BY
            units_sold DESC,
            p.product_id
        LIMIT 3
    """)

    mo.vstack([
        mo.md("#### 1. Which three products sold the most units last month?"),
        q1,
        mo.md("""
        In October 2026, Matcha Latte and Hot Chocolate each sold
        27 units, followed by Green Tea with 23 units; sales are
        measured by quantity, with ties ordered by product ID.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q2 = ask("""
        WITH joined_rows AS (
            SELECT
                ol.line_id,
                p.category,
                ol.quantity,
                ol.unit_price_charged AS product_price,
                p.cost AS product_cost,
                COALESCE(lo.unit_price_charged, 0) AS option_price,
                COALESCE(op.cost, 0) AS option_cost,
                ROW_NUMBER() OVER (
                    PARTITION BY ol.line_id
                    ORDER BY lo.option_id
                ) AS option_row
            FROM order_lines AS ol
            JOIN products AS p
                ON ol.product_id = p.product_id
            LEFT JOIN line_options AS lo
                ON ol.line_id = lo.line_id
            LEFT JOIN options AS op
                ON lo.option_id = op.option_id
        ),
        category_totals AS (
            SELECT
                category,
                SUM(
                    quantity * (
                        CASE
                            WHEN option_row = 1 THEN product_price
                            ELSE 0
                        END
                        + option_price
                    )
                ) AS revenue,
                SUM(
                    quantity * (
                        CASE
                            WHEN option_row = 1 THEN product_cost
                            ELSE 0
                        END
                        + option_cost
                    )
                ) AS cost
            FROM joined_rows
            GROUP BY category
        )
        SELECT
            category,
            revenue,
            cost,
            revenue - cost AS profit,
            ROUND(
                100.0 * (revenue - cost) / NULLIF(revenue, 0),
                2
            ) AS margin_percentage
        FROM category_totals
        ORDER BY category
    """)

    mo.vstack([
        mo.md("#### 2. What are revenue, cost, and margin by menu category?"),
        q2,
        mo.md("""
        Including options under their product categories, gross profit
        is $5,358.15 for coffee, $2,957.45 for food, $1,722.65 for other,
        and $3,344.35 for tea; margin means gross profit divided by
        revenue, using the constant product and option costs assumed
        in Part A.
        """),
    ])
    return (q2,)


@app.cell
def _(ask, mo):
    q3 = ask("""
        WITH option_totals AS (
            SELECT
                line_id,
                SUM(unit_price_charged) AS option_price
            FROM line_options
            GROUP BY line_id
        ),
        order_spending AS (
            SELECT
                o.order_id,
                o.member_id,
                SUM(
                    ol.quantity * (
                        ol.unit_price_charged
                        + COALESCE(ot.option_price, 0)
                    )
                ) AS order_total
            FROM orders AS o
            JOIN order_lines AS ol
                ON o.order_id = ol.order_id
            LEFT JOIN option_totals AS ot
                ON ol.line_id = ot.line_id
            GROUP BY
                o.order_id,
                o.member_id
        ),
        member_spending AS (
            SELECT
                m.member_id,
                m.first_name,
                COUNT(os.order_id) AS order_count,
                COALESCE(SUM(os.order_total), 0) AS total_spent,
                ROUND(AVG(os.order_total), 2) AS average_order
            FROM members AS m
            LEFT JOIN order_spending AS os
                ON m.member_id = os.member_id
            GROUP BY
                m.member_id,
                m.first_name
        )
        SELECT
            *,
            ROUND(
                (SELECT AVG(total_spent) FROM member_spending),
                2
            ) AS member_average_spending
        FROM member_spending
        WHERE total_spent > (
            SELECT AVG(total_spent)
            FROM member_spending
        )
        ORDER BY
            total_spent DESC,
            member_id
    """)

    mo.vstack([
        mo.md("#### 3. Which members spent more than the member average?"),
        q3,
        mo.md("""
        Twenty-five members spent more than the average total spending
        of $405.18 across all 40 members, including non-buyers as zero;
        spending means product and option charges regardless of
        payment method.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q4 = ask("""
        WITH payment_totals AS (
            SELECT
                order_id,
                COUNT(*) AS payment_count,
                SUM(amount) AS payment_total
            FROM payments
            GROUP BY order_id
        ),
        line_counts AS (
            SELECT
                order_id,
                COUNT(*) AS line_count
            FROM order_lines
            GROUP BY order_id
        )
        SELECT
            o.order_id,
            COALESCE(lc.line_count, 0) AS line_count,
            COALESCE(pt.payment_count, 0) AS payment_count,
            ot.order_total,
            pt.payment_total,
            pt.payment_total - ot.order_total AS difference
        FROM orders AS o
        LEFT JOIN order_totals AS ot
            ON o.order_id = ot.order_id
        LEFT JOIN payment_totals AS pt
            ON o.order_id = pt.order_id
        LEFT JOIN line_counts AS lc
            ON o.order_id = lc.order_id
        WHERE
            ot.order_total IS NULL
            OR pt.payment_total IS NULL
            OR ot.order_total <> pt.payment_total
        ORDER BY o.order_id
    """)

    mo.vstack([
        mo.md("#### 4. Which orders have mismatched payment totals?"),
        q4,
        mo.md("""
        Exactly two orders fail the check: order 1 has charges of
        $13.50 and payments of $14.50, while order 2 has charges of
        $22.75 and payments of $24.75, matching the intentional
        overpayments of $1.00 and $2.00 documented in Part A.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q5 = ask("""
        SELECT
            m.member_id,
            m.first_name,
            m.join_date
        FROM members AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders AS o
            WHERE o.member_id = m.member_id
        )
        ORDER BY m.member_id
    """)

    mo.vstack([
        mo.md("#### 5. Which loyalty members have never placed an order?"),
        q5,
        mo.md("""
        Four members—37, 38, 39, and 40—have never placed an order
        in the recorded data.
        """),
    ])
    return (q5,)


@app.cell
def _(ask, mo):
    q6 = ask("""
        WITH points_orders AS (
            SELECT DISTINCT order_id
            FROM payments
            WHERE method = 'points'
        )
        SELECT
            CAST(
                DATE_TRUNC('month', o.order_datetime) AS DATE
            ) AS month,
            COUNT(*) AS total_orders,
            COUNT(po.order_id) AS points_orders,
            ROUND(
                100.0 * COUNT(po.order_id) / COUNT(*),
                2
            ) AS points_order_pct
        FROM orders AS o
        LEFT JOIN points_orders AS po
            ON o.order_id = po.order_id
        GROUP BY DATE_TRUNC('month', o.order_datetime)
        ORDER BY month
    """)

    mo.vstack([
        mo.md("#### 6. What percentage of orders each month used points?"),
        q6,
        mo.md("""
        The monthly share of orders paid at least partly with points
        ranges from 10.20% in November 2025 to 33.33% in March 2026,
        counting each order once and including the partial months
        at the beginning and end of the dataset.
        """),
    ])
    return


@app.cell
def _(as_of, ask, mo):
    q7 = ask(f"""
        SELECT
            p.product_id,
            p.product_name,
            p.available_today
        FROM products AS p
        WHERE NOT EXISTS (
            SELECT 1
            FROM order_lines AS ol
            JOIN orders AS o
                ON ol.order_id = o.order_id
            WHERE
                ol.product_id = p.product_id
                AND o.order_datetime >=
                    DATE '{as_of}' - INTERVAL '59 days'
                AND o.order_datetime <
                    DATE '{as_of}' + INTERVAL '1 day'
        )
        ORDER BY p.product_id
    """)

    mo.vstack([
        mo.md("#### 7. Which products have not sold in the last 60 days?"),
        q7,
        mo.md("""
        Two products had no sales during the 60 calendar days ending
        November 8, 2026, inclusive: Seasonal Tea (19), which is
        available today, and Seasonal Brownie (20), which is not.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q8 = ask("""
        WITH line_counts AS (
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                ol.line_id,
                COUNT(lo.option_id) AS option_count
            FROM products AS p
            LEFT JOIN order_lines AS ol
                ON p.product_id = ol.product_id
            LEFT JOIN line_options AS lo
                ON ol.line_id = lo.line_id
            WHERE p.category IN ('coffee', 'tea')
            GROUP BY
                p.product_id,
                p.product_name,
                p.category,
                ol.line_id
        )
        SELECT
            product_id,
            product_name,
            category,
            COUNT(line_id) AS line_count,
            ROUND(
                AVG(
                    CASE
                        WHEN line_id IS NOT NULL THEN option_count
                    END
                ),
                2
            ) AS average_options_per_line
        FROM line_counts
        GROUP BY
            product_id,
            product_name,
            category
        ORDER BY product_id
    """)

    mo.vstack([
        mo.md("#### 8. How many options are selected per coffee or tea order line?"),
        q8,
        mo.md("""
        Among the 10 coffee and tea products with sales, average options
        per line range from 1.27 for Black Tea to 1.56 for Cold Brew,
        including zero-option lines without weighting by quantity;
        Seasonal Tea has no lines, so its average is unavailable.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q9 = ask("""
        WITH order_products AS (
            SELECT DISTINCT
                order_id,
                product_id
            FROM order_lines
        )
        SELECT
            p1.product_name AS product_1,
            p2.product_name AS product_2,
            COUNT(*) AS orders_together
        FROM order_products AS a
        JOIN order_products AS b
            ON a.order_id = b.order_id
            AND a.product_id < b.product_id
        JOIN products AS p1
            ON a.product_id = p1.product_id
        JOIN products AS p2
            ON b.product_id = p2.product_id
        GROUP BY
            p1.product_id,
            p1.product_name,
            p2.product_id,
            p2.product_name
        ORDER BY
            orders_together DESC,
            p1.product_id,
            p2.product_id
        LIMIT 3
    """)

    mo.vstack([
        mo.md("#### 9. Which three product pairs are bought together most often? — My Own Question"),
        q9,
        mo.md("""
        The leading pairs are Cappuccino with Blueberry Muffin
        (28 orders), Croissant with Hot Chocolate (27), and Espresso
        with Green Tea (22), counting each pair once per order
        regardless of quantity and breaking ties by product IDs.
        """),
    ])
    return


@app.cell
def _(ask, mo):
    q10 = ask("""
        WITH ordered_visits AS (
            SELECT
                member_id,
                order_id,
                order_datetime,
                LAG(order_datetime) OVER (
                    PARTITION BY member_id
                    ORDER BY order_datetime, order_id
                ) AS previous_order
            FROM orders
            WHERE member_id IS NOT NULL
        )
        SELECT
            m.member_id,
            m.first_name,
            COUNT(*) AS order_count,
            COUNT(v.previous_order) AS gap_count,
            ROUND(
                AVG(
                    EPOCH(v.order_datetime - v.previous_order)
                    / 86400.0
                ),
                2
            ) AS average_days_between_orders
        FROM ordered_visits AS v
        JOIN members AS m
            ON v.member_id = m.member_id
        GROUP BY
            m.member_id,
            m.first_name
        HAVING COUNT(*) >= 2
        ORDER BY
            average_days_between_orders,
            m.member_id
    """)

    mo.vstack([
        mo.md("#### 10. How many days pass between purchases for each returning member? — My Own Question"),
        q10,
        mo.md("""
        Across 36 members with at least two orders, individual average
        purchase gaps range from 11.00 days for member 23 to 29.91 days
        for member 15, measured as elapsed time between consecutive
        orders and allowing fractional days.
        """),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. How I Know These Numbers Are Right

    ###Check Questions 2 and 5 using different calculations.
    Each check displays both results and uses assert to report
    an error if they do not agree.
    """)
    return


@app.cell
def _(ask, q2):
    # Calculate product revenue and cost separately.
    product_check = ask("""
        SELECT
            SUM(ol.quantity * ol.unit_price_charged) AS revenue,
            SUM(ol.quantity * p.cost) AS cost
        FROM order_lines AS ol
        JOIN products AS p
            ON ol.product_id = p.product_id
    """)

    # Calculate option revenue and cost separately.
    option_check = ask("""
        SELECT
            SUM(ol.quantity * lo.unit_price_charged) AS revenue,
            SUM(ol.quantity * op.cost) AS cost
        FROM order_lines AS ol
        JOIN line_options AS lo
            ON ol.line_id = lo.line_id
        JOIN options AS op
            ON lo.option_id = op.option_id
    """)

    # Add the two parts.
    checked_revenue = (
        product_check.item(0, "revenue")
        + option_check.item(0, "revenue")
    )

    checked_cost = (
        product_check.item(0, "cost")
        + option_check.item(0, "cost")
    )

    # Compare with the actual answer from Question 2.
    print("Question 2 revenue:", q2["revenue"].sum())
    print("Independent revenue:", checked_revenue)

    print("Question 2 cost:", q2["cost"].sum())
    print("Independent cost:", checked_cost)

    assert q2["revenue"].sum() == checked_revenue, "Revenue check failed."
    assert q2["cost"].sum() == checked_cost, "Cost check failed."

    print("PASS: Both revenue and cost agree.")
    return


@app.cell
def _():
    #For Question 2, the category totals equal the independently calculated product-plus-option totals: $21,334.75 in revenue and $7,952.15 in cost.
    return


@app.cell
def _(ask, q5):
    member_check = ask("""
        SELECT
            (SELECT COUNT(*) FROM members) AS total_members,
            (
                SELECT COUNT(DISTINCT member_id)
                FROM orders
                WHERE member_id IS NOT NULL
            ) AS buying_members
    """)

    total_members = member_check.item(0, "total_members")
    buying_members = member_check.item(0, "buying_members")
    expected_nonbuyers = total_members - buying_members

    print("Total members:", total_members)
    print("Members who ordered:", buying_members)
    print("Non-buyers from subtraction:", expected_nonbuyers)
    print("Non-buyers listed in Question 5:", q5.height)

    assert q5.height == expected_nonbuyers, "Member count check failed."

    # Part A deliberately gives these four members no orders.
    assert sorted(q5["member_id"].to_list()) == [37, 38, 39, 40], (
        "The member IDs do not match the expected Part A data."
    )

    print("PASS: Both the member count and member IDs agree.")
    return


@app.cell
def _():
    #For Question 5, 40 total members minus 36 members who ordered gives 4 non-buyers, matching the four returned rows and the member IDs 37–40 deliberately left without orders in Part A.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. Working With the Agent

    The collaboration and verification notes will be added here.
    """)
    return


@app.cell
def _():
    # One piece of AI output I did not accept is on the going further part, the visualization it created it not sorted. So I add it on my own. 

    # About the code in general. I reviewed the code myself first to see if any outstanding mistakes. And then ask my agent to write verification checks code seperately to make sure.

    # I also changed the wording in Question 2. The term “margin” was confusing to me because reader may not sure whether it meant a dollar amount or a percentage. So I changed the wording to “margin percentage” to make the meaning clearer. Also, I organize the notebook layout myself. The original headings and structure AI gave me made it difficult to follow, so I reorganized the presentation into six clear sections and made the question list more compact.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Reading It Back
    **Chosen business question:**
    What are revenue, cost, and profit for each menu category,
    including options?

    **What I am predicting:**
    Before answering this question, I am predicting how many
    rows the table joins will produce before grouping,
    as required by the assignment.

    **Actual join count and explanation**

    **Meaning of one final result row**
    """)
    return


@app.cell
def _():
    # I expect the joins will produce 3,364 rows before grouping. The CSV files have 1,932 selected-option records and 1,432 order lines with no options. A line with options will appear once for each option. A line without options will still appear once because I will use a LEFT JOIN. So my prediction is 1,932 + 1,432 = 3,364 rows. Joining the product and option details should not add more rows because their IDs are unique. Actual join count and explanation: To be added after this prediction is committed. Meaning of one final result row: To be added after answering the question.
    return


@app.cell
def _(ask):
    join_check = ask("""
        SELECT COUNT(*) AS actual_join_rows
        FROM order_lines AS ol
        JOIN products AS p
            ON ol.product_id = p.product_id
        LEFT JOIN line_options AS lo
            ON ol.line_id = lo.line_id
        LEFT JOIN options AS op
            ON lo.option_id = op.option_id
    """)

    join_check
    return


@app.cell
def _():
    # Actual join count and explanation:

    #The joins produced 3,364 rows, matching my prediction. The 1,932 selected-option records each produce one row, and the 1,432 order lines without options each remain as one row because of the LEFT JOIN. Joining product and option details does not create extra matches because their IDs are unique.
    return


@app.cell
def _():
    # Meaning of one final result row:

    # One row in the final result for Question 2 represents one menu category. It shows the total revenue, cost, gross profit, and margin percentage for that category across the recorded data, including the options attached to its products.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Going Further

    I turned the results of Question 2 into a bar chart to compare
    gross profit across menu categories, including options.
    """)
    return


@app.cell
def _(q2):
    import matplotlib.pyplot as plt

    # Use the results already calculated in Question 2.
    _sorted_q2 = q2.sort("profit", descending=True)

    _categories = _sorted_q2["category"].to_list()
    _profits = _sorted_q2["profit"].to_list()

    _fig, _ax = plt.subplots(figsize=(7, 4))

    _ax.bar(_categories, _profits)

    _ax.set_title("Gross Profit by Menu Category")
    _ax.set_xlabel("Menu Category")
    _ax.set_ylabel("Gross Profit ($)")

    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    # The chart shows that coffee generated the highest gross profit ($5,358.15), followed by tea ($3,344.35), food ($2,957.45), and other products ($1,722.65). This makes the differences between categories easier to compare than reading the table alone.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Time Spent
    """)
    return


@app.cell
def _():
    # 5 hour in total. 
    # I spend 1 hour for Part A, and then Another 1 hour to fix Part A. And 3 hours for part B.
    return


if __name__ == "__main__":
    app.run()
