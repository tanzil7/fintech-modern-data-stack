"""Generate synthetic source data for the fintech analytics platform."""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from faker import Faker


SEED = 42
NUMBER_OF_CUSTOMERS = 5_000
NUMBER_OF_MERCHANTS = 500
AS_OF_DATE = datetime(2026, 8, 31, 23, 59, 59)

MERCHANT_CATEGORIES = [
    ("5411", "GROCERY"),
    ("5812", "RESTAURANTS"),
    ("5912", "DRUG_STORES"),
    ("5541", "SERVICE_STATIONS"),
    ("5732", "ELECTRONICS"),
    ("5311", "DEPARTMENT_STORES"),
    ("5999", "MISCELLANEOUS_RETAIL"),
    ("4111", "LOCAL_TRANSIT"),
    ("4814", "TELECOMMUNICATIONS"),
    ("7011", "HOTELS"),
    ("4511", "AIRLINES"),
    ("4899", "DIGITAL_SERVICES"),
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "generated"

fake = Faker("en_US")
Faker.seed(SEED)
random.seed(SEED)


def random_datetime(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between two boundaries."""

    if start >= end:
        return start

    total_seconds = int((end - start).total_seconds())

    return start + timedelta(
        seconds=random.randint(0, total_seconds)
    )


def serialize_value(value: Any) -> Any:
    """Convert dates and datetimes into CSV-friendly ISO strings."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def write_csv(
    records: list[dict[str, Any]],
    file_name: str,
) -> None:
    """Write records to the generated data directory."""

    if not records:
        raise ValueError(
            f"No records were generated for {file_name}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = OUTPUT_DIRECTORY / file_name

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(records[0].keys()),
        )

        writer.writeheader()

        for record in records:
            writer.writerow(
                {
                    key: serialize_value(value)
                    for key, value in record.items()
                }
            )

    print(
        f"Created {output_path} with {len(records):,} rows"
    )


def generate_customers() -> list[dict[str, Any]]:
    """Generate synthetic customer records."""

    customers: list[dict[str, Any]] = []

    for customer_number in range(
        1,
        NUMBER_OF_CUSTOMERS + 1,
    ):
        customer_id = f"CUST{customer_number:06d}"

        created_at = random_datetime(
            datetime(2022, 1, 1),
            datetime(2026, 6, 30, 23, 59, 59),
        )

        updated_at = random_datetime(
            created_at,
            AS_OF_DATE,
        )

        customer_status = random.choices(
            ["ACTIVE", "SUSPENDED", "CLOSED"],
            weights=[92, 3, 5],
            k=1,
        )[0]

        kyc_status = random.choices(
            ["VERIFIED", "PENDING", "REJECTED"],
            weights=[94, 4, 2],
            k=1,
        )[0]

        risk_rating = random.choices(
            ["LOW", "MEDIUM", "HIGH"],
            weights=[75, 20, 5],
            k=1,
        )[0]

        customer = {
            "customer_id": customer_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": (
                f"{customer_id.lower()}@example.com"
            ),
            "date_of_birth": fake.date_of_birth(
                minimum_age=18,
                maximum_age=80,
            ),
            "phone_number": fake.phone_number(),
            "street_address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postal_code": fake.postcode(),
            "customer_status": customer_status,
            "kyc_status": kyc_status,
            "risk_rating": risk_rating,
            "created_at": created_at,
            "updated_at": updated_at,
        }

        customers.append(customer)

    return customers


def determine_account_status(
    customer_status: str,
) -> str:
    """Generate an account status consistent with customer status."""

    if customer_status == "CLOSED":
        return "CLOSED"

    if customer_status == "SUSPENDED":
        return random.choices(
            ["FROZEN", "ACTIVE"],
            weights=[75, 25],
            k=1,
        )[0]

    return random.choices(
        ["ACTIVE", "FROZEN", "CLOSED"],
        weights=[95, 3, 2],
        k=1,
    )[0]


def generate_accounts(
    customers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate one to three accounts for every customer."""

    accounts: list[dict[str, Any]] = []
    account_number = 1

    for customer in customers:
        number_of_accounts = random.choices(
            [1, 2, 3],
            weights=[70, 25, 5],
            k=1,
        )[0]

        for _ in range(number_of_accounts):
            account_id = (
                f"ACC{account_number:08d}"
            )

            opened_at = random_datetime(
                customer["created_at"],
                AS_OF_DATE,
            )

            account_status = determine_account_status(
                str(customer["customer_status"])
            )

            closed_at = None

            if account_status == "CLOSED":
                closed_at = random_datetime(
                    opened_at,
                    AS_OF_DATE,
                )

            update_start = (
                closed_at
                if closed_at
                else opened_at
            )

            updated_at = random_datetime(
                update_start,
                AS_OF_DATE,
            )

            account = {
                "account_id": account_id,
                "customer_id": customer["customer_id"],
                "account_type": random.choice(
                    ["CHECKING", "SAVINGS"]
                ),
                "account_tier": random.choices(
                    ["STANDARD", "PREMIUM"],
                    weights=[85, 15],
                    k=1,
                )[0],
                "account_status": account_status,
                "currency": "USD",
                "opened_at": opened_at,
                "closed_at": closed_at,
                "overdraft_enabled": random.choice(
                    [True, False]
                ),
                "created_at": opened_at,
                "updated_at": updated_at,
            }

            accounts.append(account)
            account_number += 1

    return accounts


def determine_card_status(
    account_status: str,
    expires_at: datetime,
) -> str:
    """Generate a card status consistent with account status."""

    if account_status == "CLOSED":
        return "CANCELLED"

    if expires_at <= AS_OF_DATE:
        return "EXPIRED"

    if account_status == "FROZEN":
        return random.choices(
            ["BLOCKED", "ACTIVE"],
            weights=[80, 20],
            k=1,
        )[0]

    return random.choices(
        ["ACTIVE", "BLOCKED", "CANCELLED"],
        weights=[94, 4, 2],
        k=1,
    )[0]


def generate_cards(
    accounts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate one or two synthetic cards per account."""

    cards: list[dict[str, Any]] = []
    card_number = 1

    for account in accounts:
        number_of_cards = random.choices(
            [1, 2],
            weights=[82, 18],
            k=1,
        )[0]

        for _ in range(number_of_cards):
            card_id = f"CARD{card_number:08d}"

            opened_at = account["opened_at"]

            latest_issue_date = (
                account["closed_at"]
                or AS_OF_DATE
            )

            issued_at = random_datetime(
                opened_at,
                latest_issue_date,
            )

            expiration_years = random.choice(
                [3, 4, 5]
            )

            expires_at = issued_at + timedelta(
                days=365 * expiration_years
            )

            card_status = determine_card_status(
                str(account["account_status"]),
                expires_at,
            )

            updated_at = random_datetime(
                issued_at,
                AS_OF_DATE,
            )

            card = {
                "card_id": card_id,
                "account_id": account["account_id"],
                "card_type": random.choices(
                    ["PHYSICAL", "VIRTUAL"],
                    weights=[70, 30],
                    k=1,
                )[0],
                "card_network": random.choice(
                    ["VISA", "MASTERCARD"]
                ),
                "card_status": card_status,
                "last_four": (
                    f"{random.randint(0, 9999):04d}"
                ),
                "issued_at": issued_at,
                "expires_at": expires_at,
                "daily_limit": random.choice(
                    [500, 1_000, 2_500, 5_000]
                ),
                "created_at": issued_at,
                "updated_at": updated_at,
            }

            cards.append(card)
            card_number += 1

    return cards


def generate_merchants() -> list[dict[str, Any]]:
    """Generate synthetic merchant records."""

    merchants: list[dict[str, Any]] = []

    for merchant_number in range(
        1,
        NUMBER_OF_MERCHANTS + 1,
    ):
        merchant_id = (
            f"MER{merchant_number:05d}"
        )

        (
            merchant_category_code,
            merchant_category,
        ) = random.choice(MERCHANT_CATEGORIES)

        created_at = random_datetime(
            datetime(2021, 1, 1),
            datetime(2026, 6, 30, 23, 59, 59),
        )

        updated_at = random_datetime(
            created_at,
            AS_OF_DATE,
        )

        merchant = {
            "merchant_id": merchant_id,
            "merchant_name": fake.company(),
            "merchant_category_code": (
                merchant_category_code
            ),
            "merchant_category": merchant_category,
            "city": fake.city(),
            "state": fake.state_abbr(),
            "country": "US",
            "online_flag": random.choices(
                [True, False],
                weights=[35, 65],
                k=1,
            )[0],
            "risk_level": random.choices(
                ["LOW", "MEDIUM", "HIGH"],
                weights=[80, 17, 3],
                k=1,
            )[0],
            "created_at": created_at,
            "updated_at": updated_at,
        }

        merchants.append(merchant)

    return merchants


def main() -> None:
    """Generate and save all implemented source datasets."""

    customers = generate_customers()
    accounts = generate_accounts(customers)
    cards = generate_cards(accounts)
    merchants = generate_merchants()

    write_csv(
        customers,
        "customers.csv",
    )

    write_csv(
        accounts,
        "accounts.csv",
    )

    write_csv(
        cards,
        "cards.csv",
    )

    write_csv(
        merchants,
        "merchants.csv",
    )

    print(
        "Synthetic source data generation "
        "completed successfully."
    )


if __name__ == "__main__":
    main()