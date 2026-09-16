"""Data quality tests for synthetically generated source data."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "generated"


def read_csv(file_name: str) -> list[dict[str, Any]]:
    """Read a generated CSV file into a list of dictionaries."""

    file_path = DATA_DIRECTORY / file_name

    assert file_path.exists(), (
        f"{file_name} does not exist. Run the data generator first."
    )

    with file_path.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


@pytest.fixture(scope="session")
def customers() -> list[dict[str, Any]]:
    """Return generated customer records."""

    return read_csv("customers.csv")


@pytest.fixture(scope="session")
def accounts() -> list[dict[str, Any]]:
    """Return generated account records."""

    return read_csv("accounts.csv")


def test_customer_row_count(
    customers: list[dict[str, Any]],
) -> None:
    """The generator should produce exactly 5,000 customers."""

    assert len(customers) == 5_000


def test_every_customer_has_an_account(
    customers: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
) -> None:
    """Every generated customer should own at least one account."""

    customer_ids = {
        customer["customer_id"]
        for customer in customers
    }

    account_customer_ids = {
        account["customer_id"]
        for account in accounts
    }

    assert customer_ids == account_customer_ids


def test_customer_primary_keys_are_unique(
    customers: list[dict[str, Any]],
) -> None:
    """Customer IDs must be populated and unique."""

    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    assert all(customer_ids)
    assert len(customer_ids) == len(set(customer_ids))


def test_account_primary_keys_are_unique(
    accounts: list[dict[str, Any]],
) -> None:
    """Account IDs must be populated and unique."""

    account_ids = [
        account["account_id"]
        for account in accounts
    ]

    assert all(account_ids)
    assert len(account_ids) == len(set(account_ids))


def test_account_customer_relationship(
    customers: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
) -> None:
    """Every account must reference a valid customer."""

    valid_customer_ids = {
        customer["customer_id"]
        for customer in customers
    }

    invalid_customer_ids = {
        account["customer_id"]
        for account in accounts
        if account["customer_id"] not in valid_customer_ids
    }

    assert not invalid_customer_ids


def test_customer_domain_values(
    customers: list[dict[str, Any]],
) -> None:
    """Customer categorical fields must use accepted values."""

    valid_statuses = {"ACTIVE", "SUSPENDED", "CLOSED"}
    valid_kyc_statuses = {"VERIFIED", "PENDING", "REJECTED"}
    valid_risk_ratings = {"LOW", "MEDIUM", "HIGH"}

    assert all(
        customer["customer_status"] in valid_statuses
        for customer in customers
    )

    assert all(
        customer["kyc_status"] in valid_kyc_statuses
        for customer in customers
    )

    assert all(
        customer["risk_rating"] in valid_risk_ratings
        for customer in customers
    )


def test_account_domain_values(
    accounts: list[dict[str, Any]],
) -> None:
    """Account categorical fields must use accepted values."""

    valid_types = {"CHECKING", "SAVINGS"}
    valid_tiers = {"STANDARD", "PREMIUM"}
    valid_statuses = {"ACTIVE", "FROZEN", "CLOSED"}

    assert all(
        account["account_type"] in valid_types
        for account in accounts
    )

    assert all(
        account["account_tier"] in valid_tiers
        for account in accounts
    )

    assert all(
        account["account_status"] in valid_statuses
        for account in accounts
    )

    assert all(
        account["currency"] == "USD"
        for account in accounts
    )


def test_customer_timestamp_order(
    customers: list[dict[str, Any]],
) -> None:
    """Customer updates cannot occur before customer creation."""

    for customer in customers:
        created_at = datetime.fromisoformat(customer["created_at"])
        updated_at = datetime.fromisoformat(customer["updated_at"])

        assert updated_at >= created_at


def test_account_date_consistency(
    accounts: list[dict[str, Any]],
) -> None:
    """Account dates must agree with account status."""

    for account in accounts:
        opened_at = datetime.fromisoformat(account["opened_at"])
        updated_at = datetime.fromisoformat(account["updated_at"])
        closed_at_value = account["closed_at"]

        assert updated_at >= opened_at

        if account["account_status"] == "CLOSED":
            assert closed_at_value

            closed_at = datetime.fromisoformat(closed_at_value)

            assert closed_at >= opened_at
            assert updated_at >= closed_at
        else:
            assert not closed_at_value