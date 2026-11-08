import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    from pathlib import Path

    return Path, duckdb


@app.cell
def _(Path):
    project_dir = Path("projects/db").resolve()
    data_dir = project_dir / "data"
    db_path = project_dir / "database.duckdb"

    print("Project folder:", project_dir)
    print("Data folder exists:", data_dir.is_dir())
    return data_dir, db_path


@app.cell
def _(db_path, duckdb):
    con = duckdb.connect(str(db_path))
    return (con,)


@app.cell
def _(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_id INTEGER PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        mobile_number VARCHAR NOT NULL,
        email VARCHAR,
        join_date DATE NOT NULL,
        points_balance INTEGER NOT NULL CHECK (points_balance >= 0)
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR NOT NULL,
        category VARCHAR NOT NULL
            CHECK (category IN ('coffee', 'tea', 'food', 'other')),
        price DECIMAL(10, 2) NOT NULL,
        cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0),
        available_today BOOLEAN NOT NULL,
        CHECK (price >= cost)
    );

    CREATE TABLE IF NOT EXISTS options (
        option_id INTEGER PRIMARY KEY,
        option_name VARCHAR NOT NULL,
        price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
        cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0)
    );

    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        order_datetime TIMESTAMP NOT NULL,
        member_id INTEGER REFERENCES members(member_id),
        channel VARCHAR NOT NULL
            CHECK (channel IN ('counter', 'app'))
    );

    CREATE TABLE IF NOT EXISTS order_lines (
        line_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        product_id INTEGER NOT NULL REFERENCES products(product_id),
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price_charged DECIMAL(10, 2) NOT NULL
            CHECK (unit_price_charged >= 0)
    );

    CREATE TABLE IF NOT EXISTS line_options (
        line_id INTEGER NOT NULL REFERENCES order_lines(line_id),
        option_id INTEGER NOT NULL REFERENCES options(option_id),
        unit_price_charged DECIMAL(10, 2) NOT NULL
            CHECK (unit_price_charged >= 0),
        PRIMARY KEY (line_id, option_id)
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL REFERENCES orders(order_id),
        method VARCHAR NOT NULL
            CHECK (method IN ('cash', 'card', 'app', 'points')),
        amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0)
    );
    """)

    print("All seven tables are ready.")
    return


@app.cell
def _(con):
    con.execute("SHOW TABLES").fetchall()
    return


@app.cell
def _(con, data_dir):
    table_names = [
        "members",
        "products",
        "options",
        "orders",
        "order_lines",
        "line_options",
        "payments",
    ]

    # Check that all seven CSV files exist.
    missing_files = [
        name + ".csv"
        for name in table_names
        if not (data_dir / (name + ".csv")).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(f"Missing CSV files: {missing_files}")

    # Avoid importing the same data twice.
    existing_rows = sum(
        con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        for name in table_names
    )

    if existing_rows > 0:
        print("The database already contains data. Import skipped.")
    else:
        con.execute("BEGIN TRANSACTION")

        try:
            for name in table_names:
                csv_path = str(data_dir / (name + ".csv")).replace("'", "''")

                con.execute(f"""
                    COPY {name}
                    FROM '{csv_path}'
                    (FORMAT CSV, HEADER TRUE, NULL '');
                """)

            con.execute("COMMIT")
            print("All seven CSV files were imported successfully.")

        except Exception:
            con.execute("ROLLBACK")
            raise
    return (table_names,)


@app.cell
def _(con, table_names):
    for _table in table_names:
        _count = con.execute(
            f"SELECT COUNT(*) FROM {_table}"
        ).fetchone()[0]

        print(f"{_table}: {_count} rows")
    return


@app.cell
def _(con):
    _check_results = con.execute("""
    WITH option_totals AS (
        SELECT
            line_id,
            SUM(unit_price_charged) AS option_price
        FROM line_options
        GROUP BY line_id
    ),
    order_totals AS (
        SELECT
            ol.order_id,
            SUM(
                ol.quantity * (
                    ol.unit_price_charged
                    + COALESCE(ot.option_price, 0)
                )
            ) AS order_total
        FROM order_lines AS ol
        LEFT JOIN option_totals AS ot
            ON ol.line_id = ot.line_id
        GROUP BY ol.order_id
    ),
    payment_totals AS (
        SELECT
            order_id,
            SUM(amount) AS payment_total
        FROM payments
        GROUP BY order_id
    )
    SELECT
        o.order_id,
        ot.order_total,
        pt.payment_total
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
    """).fetchall()

    print("Orders with missing lines, missing payments, or mismatched totals:",
          len(_check_results))

    if _check_results:
        print(_check_results[:10])
    else:
        print("Passed: every order has lines and matching payments.")
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
