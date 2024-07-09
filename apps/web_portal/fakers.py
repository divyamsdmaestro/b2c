# flake8: noqa
"""
This file is used for populating and using dummy data until
development of actual features are completed.
"""

import random

from faker import Faker

faker = Faker()


def get_subscription_plan(
    title,
    price,
    sub_title="Exclusive GST",
    tags=[],
    super_title=None,
    discount_price=None,
):
    return {
        "super_title": super_title,
        "title": title,
        "currency": "INR",
        "currency_symbol": "$",
        "price": price,
        "discount_price": discount_price,
        "sub_title": sub_title,
        "tags": tags,
        "benefits": [
            {"display": faker.name(), "available": random.choice([True, False])},
            {"display": faker.name(), "available": random.choice([True, False])},
            {"display": faker.name(), "available": random.choice([True, False])},
            {"display": faker.name(), "available": random.choice([True, False])},
            {"display": faker.name(), "available": random.choice([True, False])},
        ],
    }


SUBSCRIPTION_PLANS = {
    "monthly": {
        "plans": [
            get_subscription_plan(title="Free", price=0, sub_title="No Charges"),
            get_subscription_plan(title="Individual", price=999, tags=["popular"]),
            get_subscription_plan(
                title="Enterprise", price=9999, super_title="with labs"
            ),
        ]
    },
    "yearly": {
        "plans": [
            get_subscription_plan(title="Free", price=0, sub_title="No Charges"),
            get_subscription_plan(
                title="Individual", price=999, tags=["popular"], discount_price=899
            ),
            get_subscription_plan(
                title="Enterprise",
                price=9999,
                super_title="with labs",
                discount_price=8999,
            ),
        ],
        "discount_percentage": 5,
    },
}

PROFILE_IMAGE_URL = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
VIDEO_URL = "https://www.youtube.com/watch?v=tOwjEOt1zYU"
CATEGORY_IMAGE_URL = "https://www.shutterstock.com/image-photo/category-word-written-on-wood-260nw-1336568840.jpg"

# TODO: REMOVE THIS FILE COMPLETELY ONCE ACTUAL DATA ARE POPULATED & USED
