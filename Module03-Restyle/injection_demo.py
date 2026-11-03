"""Show apostrophe failure and SQL injection, then verify bound parameters."""
import hashlib
import sqlite3
from pathlib import Path

here = Path(__file__).resolve().parent
db = here / "warehouse.db"
if not db.is_file():
    raise SystemExit("Run the Module03 setup first")
before = hashlib.sha256(db.read_bytes()).hexdigest()
conn = sqlite3.connect(db.as_uri()+"?mode=ro", uri=True)


def vulnerable(name):
    return conn.execute(f"SELECT customer_id, name FROM customer WHERE name = '{name}'").fetchall()


def safe(name):
    return conn.execute("SELECT customer_id, name FROM customer WHERE name = ?", (name,)).fetchall()


if __name__ == "__main__":
    payload = "' OR '1'='1"
    normal = vulnerable("Customer 1")
    assert normal == safe("Customer 1") == [(1, "Customer 1")]
    try:
        vulnerable("O'Brien")
    except sqlite3.OperationalError as error:
        apostrophe_error = str(error)
    else:
        raise AssertionError("Expected apostrophe syntax failure")
    injected = vulnerable(payload)
    assert len(injected) == conn.execute("SELECT COUNT(*) FROM customer").fetchone()[0] == 2000
    assert safe(payload) == []
    assert safe("O'Brien") == []
    # Prove parameterization supports an actual apostrophe-containing name.
    fixture = sqlite3.connect(":memory:")
    fixture.execute("CREATE TABLE customer(name TEXT)")
    fixture.execute("INSERT INTO customer VALUES (?)", ("O'Brien",))
    assert fixture.execute("SELECT name FROM customer WHERE name=?", ("O'Brien",)).fetchall() == [("O'Brien",)]
    fixture.close()
    conn.close()
    assert hashlib.sha256(db.read_bytes()).hexdigest() == before
    output = "\n".join([
        f"normal: {normal}", f"apostrophe input: O'Brien; vulnerable error: {apostrophe_error}",
        f"payload: {payload}", f"vulnerable payload result count: {len(injected)}",
        "safe payload result: []", "safe apostrophe lookup works in a fixture containing O'Brien",
        "PASS normal results, apostrophe failure, injection bypass, bound-parameter fix",
        "PASS source database opened read-only and hash unchanged", ""])
    (here/"injection-output.txt").write_text(output,encoding="utf-8")
    print(output)
