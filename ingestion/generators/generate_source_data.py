"""Generate synthetic source data for the fintech analytics platform."""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from faker import Faker


SEED = 42
NUMBER_OF_CUSTOMERS = 5_000
AS_OF_DATE = datetime(2026, 8, 31, 23, 59, 59)

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
    return start + timedelta(seconds=random.randint(0, total_seconds))


def serialize_value(value: Any) -> Any:
    """Convert dates and datetimes into CSV-friendly ISO strings."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def write_csv(records: list[dict[str, Any]], file_name: str) -> None:
    """Write a collection of records to the generated data directory."""

    if not records:
        raise ValueError(f"No records were generated for {file_name}")

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIRECTORY / file_name

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
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

    print(f"Created {output_path} with {len(records):,} rows")


def generate_customers() -> list[dict[str, Any]]:
    """Generate synthetic customer records."""

    customers: list[dict[str, Any]] = []

    for customer_number in range(1, NUMBER_OF_CUSTOMERS + 1):
        customer_id = f"CUST{customer_number:06d}"

        created_at = random_datetime(
            datetime(2022, 1, 1),
            datetime(2026, 6, 30, 23, 59, 59),
        )

        updated_at = random_datetime(created_at, AS_OF_DATE)

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
            "email": f"{customer_id.lower()}@example.com",
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


def determine_account_status(customer_status: str) -> str:
    """Generate an account status consistent with the customer status."""

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
            account_id = f"ACC{account_number:08d}"

            opened_at = random_datetime(
                customer["created_at"],
                AS_OF_DATE,
            )

            account_status = determine_account_status(
                str(customer["customer_status"])
            )

            closed_at = None

            if account_status == "CLOSED":
                closed_at = random_datetime(opened_at, AS_OF_DATE)

            update_start = closed_at if closed_at else opened_at
            updated_at = random_datetime(update_start, AS_OF_DATE)

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
                "overdraft_enabled": random.choice([True, False]),
                "created_at": opened_at,
                "updated_at": updated_at,
            }

            accounts.append(account)
            account_number += 1

    return accounts


def main() -> None:
    """Generate and save all currently implemented source datasets."""

    customers = generate_customers()
    accounts = generate_accounts(customers)

    write_csv(customers, "customers.csv")
    write_csv(accounts, "accounts.csv")

    print("Synthetic source data generation completed successfully.")


if __name__ == "__main__":
    main()