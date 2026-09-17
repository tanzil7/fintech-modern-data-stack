"""Data quality tests for synthetically generated source data."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data" / "generated"
AS_OF_DATE = datetime(2026, 8, 31, 23, 59, 59)

VALID_MERCHANT_CATEGORIES = {
    "5411": "GROCERY",
    "5812": "RESTAURANTS",
    "5912": "DRUG_STORES",
    "5541": "SERVICE_STATIONS",
    "5732": "ELECTRONICS",
    "5311": "DEPARTMENT_STORES",
    "5999": "MISCELLANEOUS_RETAIL",
    "4111": "LOCAL_TRANSIT",
    "4814": "TELECOMMUNICATIONS",
    "7011": "HOTELS",
    "4511": "AIRLINES",
    "4899": "DIGITAL_SERVICES",
}


def read_csv(
    file_name: str,
) -> list[dict[str, Any]]:
    """Read a generated CSV file into dictionaries."""

    file_path = DATA_DIRECTORY / file_name

    assert file_path.exists(), (
        f"{file_name} does not exist. "
        "Run the data generator first."
    )

    with file_path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


@pytest.fixture(scope="session")
def customers() -> list[dict[str, Any]]:
    """Return generated customer records."""

    return read_csv("customers.csv")


@pytest.fixture(scope="session")
def accounts() -> list[dict[str, Any]]:
    """Return generated account records."""

    return read_csv("accounts.csv")


@pytest.fixture(scope="session")
def cards() -> list[dict[str, Any]]:
    """Return generated card records."""

    return read_csv("cards.csv")


@pytest.fixture(scope="session")
def merchants() -> list[dict[str, Any]]:
    """Return generated merchant records."""

    return read_csv("merchants.csv")


def test_customer_row_count(
    customers: list[dict[str, Any]],
) -> None:
    """The generator should produce 5,000 customers."""

    assert len(customers) == 5_000


def test_every_customer_has_an_account(
    customers: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
) -> None:
    """Every customer should own at least one account."""

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
        if account["customer_id"]
        not in valid_customer_ids
    }

    assert not invalid_customer_ids


def test_customer_domain_values(
    customers: list[dict[str, Any]],
) -> None:
    """Customer fields must use accepted values."""

    valid_statuses = {
        "ACTIVE",
        "SUSPENDED",
        "CLOSED",
    }

    valid_kyc_statuses = {
        "VERIFIED",
        "PENDING",
        "REJECTED",
    }

    valid_risk_ratings = {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert all(
        customer["customer_status"]
        in valid_statuses
        for customer in customers
    )

    assert all(
        customer["kyc_status"]
        in valid_kyc_statuses
        for customer in customers
    )

    assert all(
        customer["risk_rating"]
        in valid_risk_ratings
        for customer in customers
    )


def test_account_domain_values(
    accounts: list[dict[str, Any]],
) -> None:
    """Account fields must use accepted values."""

    valid_types = {
        "CHECKING",
        "SAVINGS",
    }

    valid_tiers = {
        "STANDARD",
        "PREMIUM",
    }

    valid_statuses = {
        "ACTIVE",
        "FROZEN",
        "CLOSED",
    }

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
    """Customer updates cannot precede creation."""

    for customer in customers:
        created_at = datetime.fromisoformat(
            customer["created_at"]
        )

        updated_at = datetime.fromisoformat(
            customer["updated_at"]
        )

        assert created_at <= updated_at <= AS_OF_DATE


def test_account_date_consistency(
    accounts: list[dict[str, Any]],
) -> None:
    """Account dates must agree with status."""

    for account in accounts:
        opened_at = datetime.fromisoformat(
            account["opened_at"]
        )

        updated_at = datetime.fromisoformat(
            account["updated_at"]
        )

        closed_at_value = account["closed_at"]

        assert opened_at <= updated_at <= AS_OF_DATE

        if account["account_status"] == "CLOSED":
            assert closed_at_value

            closed_at = datetime.fromisoformat(
                closed_at_value
            )

            assert opened_at <= closed_at
            assert closed_at <= updated_at
        else:
            assert not closed_at_value


def test_every_account_has_a_card(
    accounts: list[dict[str, Any]],
    cards: list[dict[str, Any]],
) -> None:
    """Every account should have at least one card."""

    account_ids = {
        account["account_id"]
        for account in accounts
    }

    card_account_ids = {
        card["account_id"]
        for card in cards
    }

    assert account_ids == card_account_ids
    assert len(cards) >= len(accounts)


def test_card_primary_keys_are_unique(
    cards: list[dict[str, Any]],
) -> None:
    """Card IDs must be populated and unique."""

    card_ids = [
        card["card_id"]
        for card in cards
    ]

    assert all(card_ids)
    assert len(card_ids) == len(set(card_ids))


def test_card_account_relationship(
    accounts: list[dict[str, Any]],
    cards: list[dict[str, Any]],
) -> None:
    """Every card must reference a valid account."""

    valid_account_ids = {
        account["account_id"]
        for account in accounts
    }

    invalid_account_ids = {
        card["account_id"]
        for card in cards
        if card["account_id"]
        not in valid_account_ids
    }

    assert not invalid_account_ids


def test_card_domain_values(
    cards: list[dict[str, Any]],
) -> None:
    """Card fields must use accepted values."""

    valid_card_types = {
        "PHYSICAL",
        "VIRTUAL",
    }

    valid_networks = {
        "VISA",
        "MASTERCARD",
    }

    valid_statuses = {
        "ACTIVE",
        "BLOCKED",
        "EXPIRED",
        "CANCELLED",
    }

    valid_daily_limits = {
        "500",
        "1000",
        "2500",
        "5000",
    }

    assert all(
        card["card_type"] in valid_card_types
        for card in cards
    )

    assert all(
        card["card_network"] in valid_networks
        for card in cards
    )

    assert all(
        card["card_status"] in valid_statuses
        for card in cards
    )

    assert all(
        card["daily_limit"] in valid_daily_limits
        for card in cards
    )

    assert all(
        len(card["last_four"]) == 4
        and card["last_four"].isdigit()
        for card in cards
    )


def test_sensitive_card_fields_are_excluded(
    cards: list[dict[str, Any]],
) -> None:
    """Full payment credentials must not be generated."""

    forbidden_columns = {
        "card_number",
        "full_card_number",
        "cvv",
        "cvc",
        "security_code",
        "pin",
    }

    actual_columns = set(cards[0].keys())

    assert forbidden_columns.isdisjoint(
        actual_columns
    )


def test_card_date_consistency(
    accounts: list[dict[str, Any]],
    cards: list[dict[str, Any]],
) -> None:
    """Card dates and statuses must agree with accounts."""

    accounts_by_id = {
        account["account_id"]: account
        for account in accounts
    }

    for card in cards:
        account = accounts_by_id[
            card["account_id"]
        ]

        account_opened_at = datetime.fromisoformat(
            account["opened_at"]
        )

        issued_at = datetime.fromisoformat(
            card["issued_at"]
        )

        expires_at = datetime.fromisoformat(
            card["expires_at"]
        )

        updated_at = datetime.fromisoformat(
            card["updated_at"]
        )

        assert account_opened_at <= issued_at
        assert issued_at <= AS_OF_DATE
        assert expires_at > issued_at
        assert issued_at <= updated_at <= AS_OF_DATE

        if account["closed_at"]:
            account_closed_at = datetime.fromisoformat(
                account["closed_at"]
            )

            assert issued_at <= account_closed_at

        if account["account_status"] == "CLOSED":
            assert card["card_status"] == "CANCELLED"
        elif expires_at <= AS_OF_DATE:
            assert card["card_status"] == "EXPIRED"


def test_merchant_row_count(
    merchants: list[dict[str, Any]],
) -> None:
    """The generator should produce 500 merchants."""

    assert len(merchants) == 500


def test_merchant_primary_keys_are_unique(
    merchants: list[dict[str, Any]],
) -> None:
    """Merchant IDs must be populated and unique."""

    merchant_ids = [
        merchant["merchant_id"]
        for merchant in merchants
    ]

    assert all(merchant_ids)

    assert len(merchant_ids) == len(
        set(merchant_ids)
    )


def test_merchant_domain_values(
    merchants: list[dict[str, Any]],
) -> None:
    """Merchant fields must use accepted values."""

    valid_risk_levels = {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    for merchant in merchants:
        merchant_category_code = (
            merchant["merchant_category_code"]
        )

        assert merchant_category_code in (
            VALID_MERCHANT_CATEGORIES
        )

        assert (
            merchant["merchant_category"]
            == VALID_MERCHANT_CATEGORIES[
                merchant_category_code
            ]
        )

        assert merchant["country"] == "US"

        assert merchant["online_flag"] in {
            "True",
            "False",
        }

        assert (
            merchant["risk_level"]
            in valid_risk_levels
        )


def test_merchant_timestamp_order(
    merchants: list[dict[str, Any]],
) -> None:
    """Merchant updates cannot precede creation."""

    for merchant in merchants:
        created_at = datetime.fromisoformat(
            merchant["created_at"]
        )

        updated_at = datetime.fromisoformat(
            merchant["updated_at"]
        )

        assert created_at <= updated_at <= AS_OF_DATE