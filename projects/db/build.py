import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import matplotlib.pyplot as plt

    database = mo.notebook_dir() / "database.duckdb"
    data_dir = mo.notebook_dir() / "data"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return mo, duckdb, pl, plt, database, data_dir, ask


@app.cell
def _(mo):
    mo.md("""
    ## The Tables

    Seven tables store members, products, options, orders,
    order lines, line options, and payments.
    """)
    return


@app.cell
def _(database, data_dir, duckdb):
    # Delete the old database before building a new one.
    if database.exists():
        database.unlink()

    with duckdb.connect(database) as _con:
        _con.execute("""
            CREATE TABLE members (
                member_id INTEGER PRIMARY KEY,
                first_name VARCHAR NOT NULL,
                mobile_number VARCHAR NOT NULL,
                email VARCHAR,
                join_date DATE NOT NULL,
                points_balance INTEGER NOT NULL
                    CHECK (points_balance >= 0)
            );

            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                product_name VARCHAR NOT NULL,
                category VARCHAR NOT NULL
                    CHECK (
                        category IN ('coffee', 'tea', 'food', 'other')
                    ),
                price DECIMAL(10, 2) NOT NULL,
                cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0),
                available_today BOOLEAN NOT NULL,
                CHECK (price >= cost)
            );

            CREATE TABLE options (
                option_id INTEGER PRIMARY KEY,
                option_name VARCHAR NOT NULL,
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0)
            );

            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                order_datetime TIMESTAMP NOT NULL,
                member_id INTEGER REFERENCES members(member_id),
                channel VARCHAR NOT NULL
                    CHECK (channel IN ('counter', 'app'))
            );

            CREATE TABLE order_lines (
                line_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(order_id),
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price_charged DECIMAL(10, 2) NOT NULL
                    CHECK (unit_price_charged >= 0)
            );

            CREATE TABLE line_options (
                line_id INTEGER NOT NULL REFERENCES order_lines(line_id),
                option_id INTEGER NOT NULL REFERENCES options(option_id),
                unit_price_charged DECIMAL(10, 2) NOT NULL
                    CHECK (unit_price_charged >= 0),
                PRIMARY KEY (line_id, option_id)
            );

            CREATE TABLE payments (
                payment_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(order_id),
                method VARCHAR NOT NULL
                    CHECK (method IN ('cash', 'card', 'app', 'points')),
                amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0)
            );
        """)

        _tables = [
            "members",
            "products",
            "options",
            "orders",
            "order_lines",
            "line_options",
            "payments",
        ]

        for _table in _tables:
            _csv_path = str(
                data_dir / f"{_table}.csv"
            ).replace("'", "''")

            _con.execute(f"""
                COPY {_table}
                FROM '{_csv_path}'
                (FORMAT CSV, HEADER TRUE, NULL '');
            """)

        # This view is also used in the payment check.
        _con.execute("""
            CREATE VIEW order_totals AS
            WITH option_totals AS (
                SELECT
                    line_id,
                    SUM(unit_price_charged) AS option_price
                FROM line_options
                GROUP BY line_id
            )
            SELECT
                o.order_id,
                o.order_datetime,
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
                o.order_datetime,
                o.member_id;
        """)

    build_done = True
    print("Database rebuilt from CSV files. Connection closed.")
    return (build_done,)


@app.cell
def _(mo):
    mo.md("""
    ## The Data

    The seven CSV files were generated by `make_data.py`
    using random seed 42 and loaded in the build cell above.

    The as_of date is November 8, 2026. The data covers
    November 8, 2025, inclusive, to November 8, 2026, exclusive.

    The generator creates 40 members, 20 products, 8 options,
    and 1,000 orders, plus their lines, options, and payments.

    Members 37–40 are deliberately given no orders.
    Products 19 and 20 are deliberately given no sales.
    The data also includes non-member orders, lines without
    options, and payments partly made with points.

    Exactly two payment records deliberately break the
    payment-total rule:

    - Order 1: payment total is $1.00 too high.
    - Order 2: payment total is $2.00 too high.

    The query below checks for missing lines, missing payments,
    and mismatched totals. It should return only orders 1 and 2.
    """)
    return


@app.cell
def _(ask, build_done):
    ask("""
        WITH payment_totals AS (
            SELECT
                order_id,
                SUM(amount) AS payment_total
            FROM payments
            GROUP BY order_id
        )
        SELECT
            o.order_id,
            ot.order_total,
            pt.payment_total,
            pt.payment_total - ot.order_total AS difference
        FROM orders AS o
        LEFT JOIN order_totals AS ot
            ON o.order_id = ot.order_id
        LEFT JOIN payment_totals AS pt
            ON o.order_id = pt.order_id
        WHERE
            ot.order_total IS NULL
            OR pt.payment_total IS NULL
            OR ot.order_total <> pt.payment_total
        ORDER BY o.order_id
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A Look at the Data

    This chart shows the number of orders by hour,
    read directly from `orders.csv` with Polars.
    """)
    return


@app.cell
def _(data_dir, pl, plt):
    _orders = pl.read_csv(
        data_dir / "orders.csv",
        try_parse_dates=True,
    )

    _hours = (
        _orders
        .with_columns(
            pl.col("order_datetime").dt.hour().alias("hour")
        )
        .group_by("hour")
        .agg(pl.len().alias("orders"))
        .sort("hour")
    )

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.bar(
        _hours["hour"].to_list(),
        _hours["orders"].to_list(),
    )
    _ax.set_xlabel("Hour of day")
    _ax.set_ylabel("Number of orders")
    _ax.set_title("Orders by Hour")
    _ax.set_xticks(range(7, 19))
    _fig.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md("""
    The breakfast and lunch peaks seem plausible for a campus
    café; I changed `make_data.py` from equally likely opening
    hours to weighted hours to represent these busier periods.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Row Counts
    """)
    return


@app.cell
def _(ask, build_done):
    ask("""
        SELECT 'members' AS table_name, COUNT(*) AS row_count
        FROM members
        UNION ALL
        SELECT 'products', COUNT(*) FROM products
        UNION ALL
        SELECT 'options', COUNT(*) FROM options
        UNION ALL
        SELECT 'orders', COUNT(*) FROM orders
        UNION ALL
        SELECT 'order_lines', COUNT(*) FROM order_lines
        UNION ALL
        SELECT 'line_options', COUNT(*) FROM line_options
        UNION ALL
        SELECT 'payments', COUNT(*) FROM payments
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A Row It Refuses

    This insert attempts to add an option with a negative price.
    I expect the database to reject it because option prices
    must be zero or greater.
    """)
    return


@app.cell
def _(database, duckdb, build_done):
    try:
        with duckdb.connect(database) as _con:
            _con.execute("""
                INSERT INTO options (
                    option_id,
                    option_name,
                    price,
                    cost
                )
                VALUES (
                    999,
                    'Invalid test option',
                    -1.00,
                    0.25
                );
            """)

    except duckdb.ConstraintException as _error:
        print("Expected refusal:")
        print(_error)

    return


@app.cell
def _(mo):
    mo.md("""
    ## Answers You Already Knew

    **Query 1 — Expected answer: 40 members.**

    The generator creates member IDs 1 through 40.
    """)
    return


@app.cell
def _(ask, build_done):
    ask("SELECT COUNT(*) AS member_count FROM members")
    return


@app.cell
def _(mo):
    mo.md("""
    **Query 2 — Expected answer: members 37, 38, 39, and 40.**

    The generator deliberately gives these members no orders.
    """)
    return


@app.cell
def _(ask, build_done):
    ask("""
        SELECT member_id
        FROM members
        WHERE member_id NOT IN (
            SELECT member_id
            FROM orders
            WHERE member_id IS NOT NULL
        )
        ORDER BY member_id
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    **Query 3 — Expected answer: products 19 and 20.**

    The generator deliberately gives these products no sales.
    """)
    return


@app.cell
def _(ask, build_done):
    ask("""
        SELECT product_id, product_name
        FROM products
        WHERE product_id NOT IN (
            SELECT product_id
            FROM order_lines
        )
        ORDER BY product_id
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A View

    Weekly business question: How much sales revenue did the
    café earn on each day of the past seven days?

    The `order_totals` view is created in the build cell.
    It calculates revenue from order lines and their options,
    regardless of payment method.

    This query shows the seven days before the as_of date.
    The view will also be used for the payment reconciliation
    question in Part B.
    """)
    return


@app.cell
def _(ask, build_done):
    ask("""
        SELECT
            CAST(order_datetime AS DATE) AS sales_date,
            COUNT(*) AS order_count,
            SUM(order_total) AS revenue
        FROM order_totals
        WHERE order_datetime >= TIMESTAMP '2026-11-01 00:00:00'
          AND order_datetime < TIMESTAMP '2026-11-08 00:00:00'
        GROUP BY CAST(order_datetime AS DATE)
        ORDER BY sales_date
    """)
    return


if __name__ == "__main__":
    app.run()