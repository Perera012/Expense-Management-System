import os
import tempfile
import pytest

from app import app, init_db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()

    app.config["TESTING"] = True

    # change database for testing
    import app as myapp
    myapp.DATABASE = db_path

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Expense" in response.data


def test_add_expense(client):
    response = client.post("/add", data={
        "date": "2026-03-31",
        "cost_gbp": "100.50",
        "description": "Bus ticket",
        "expense_type": "Transport"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Bus ticket" in response.data


def test_view_expenses(client):
    client.post("/add", data={
        "date": "2026-03-31",
        "cost_gbp": "200.00",
        "description": "Electricity bill",
        "expense_type": "Bills"
    }, follow_redirects=True)

    response = client.get("/expenses")
    assert response.status_code == 200
    assert b"Electricity bill" in response.data


def test_view_expense_detail(client):
    client.post("/add", data={
        "date": "2026-03-31",
        "cost_gbp": "300.00",
        "description": "Groceries",
        "expense_type": "Food"
    }, follow_redirects=True)

    response = client.get("/expenses/1")
    assert response.status_code == 200
    assert b"Groceries" in response.data


def test_delete_expense(client):
    client.post("/add", data={
        "date": "2026-03-31",
        "cost_gbp": "50.00",
        "description": "Coffee",
        "expense_type": "Food"
    }, follow_redirects=True)

    response = client.post("/delete/1", follow_redirects=True)
    assert response.status_code == 200
    assert b"Coffee" not in response.data