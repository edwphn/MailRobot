"""
Sort and group data into dictionary. Returns dict.

Functions:
- prepare_overdue
- prepare_frfeed
"""
from decimal import Decimal


def prepare_overdue(raw) -> dict:
    """
    Sort and group data into dictionary. Structure:

    currency: {
        email: {
            'total_amount': 289.8,
            'invoices': ['230102789', '230102790']
        }
    }

    After data could be unpacked and send as arguments, e.g.:
    `send_mail(currency, email, inv_data['amount'], inv_data['invoices'])`

    Returning dictionary.
    """

    dataset: dict = {}

    for db_id, invoice, currency, amount, email in raw:
        invoice = invoice + '.pdf'
        email = email.strip().lower()
        amount = Decimal(amount)

        if currency not in dataset:
            dataset[currency] = {}

        if email not in dataset.get(currency, []):
            dataset[currency][email] = {'total_amount': Decimal(0), 'invoices': []}

        dataset[currency][email]['total_amount'] += amount
        dataset[currency][email]['invoices'].append(invoice)

    return dataset


def prepare_frfeed(raw) -> dict:
    """
    Sort and group data into dictionary. Structure:

    email_1: [
        (orderno, invoce, amount, parcels, carrier, tracking),
        (orderno, invoce, amount, parcels, carrier, tracking),
        ...
    ]

    After data could be unpacked and send as arguments, e.g.:
    `data2html(orderno, invoce, amount, parcels, carrier, tracking)`

    Returning dictionary.
    """

    dataset: dict = {}

    for db_id, invoice, currency, orderno, amount, email, parcels, carrier, tracking in raw:
        invoice = invoice + '.pdf'
        amount = f'{Decimal(amount)} {currency}'
        email = email.strip().lower()
        parcels = str(int(parcels))
        tracking = tracking.replace(',', ', ')

        details: tuple = (orderno, invoice, amount, parcels, carrier, tracking)

        if email not in dataset:
            dataset[email] = []

        dataset[email].append(details)

    return dataset
