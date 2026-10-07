"""Core logic: send one transaction to Jev, get back a category + confidence."""
from typesafe_sdk import Choice, Noul, TypeSafeClient

# Reads TYPESAFE_API_KEY from your environment.
# Pin the model version so your confidence thresholds don't shift under you.
client = TypeSafeClient(model="jev-1.13.0")

CATEGORIES = {
    "food": "Meals and items eaten or drunk on the spot: restaurant, cafe, street food, canteen or mess, food delivery, single-serve snacks, ice cream, juice, chaas, a single can or glass of a soft drink",
    "groceries": "Items bought to take home: vegetables, milk, bread, eggs, sauces, pickles, and packaged snacks, biscuits, chips, chocolates and multipack or large bottled drinks; quick-commerce grocery orders",
    "transport": "Cabs and autos (Uber, Ola, Rapido), fuel, metro, bus, parking, tolls, local train tickets and passes within a city",
    "bills": "Electricity, water, phone recharge, internet, rent, insurance",
    "shopping": "Physical products that are not food or medicine: clothes, electronics, stationery, toiletries, merchandise",
    "entertainment": "Movies, streaming, games, events, sports turfs, fun subscriptions",
    "health": "Doctors, pharmacy and medicines, gym, medical tests",
    "travel": "Flights, intercity train or bus tickets, hotels, trip bookings",
    "other": "Services and fees with no category above: haircut, tailoring, laundry, repairs and servicing, photocopy or printing, contest or exam fees, cash withdrawals, money sent to people",
}

CONFIDENCE_THRESHOLD = 0.6  # below this -> "needs_review". Tune it on your labeled data.


def categorize(description: str, amount: float | None = None) -> dict:
    state = {"transaction_description": description}
    if amount is not None:
        state["amount"] = amount

    response = client.system_one(
        state=state,
        questions={
            "category": Choice(
                instructions="Which spending category does this transaction belong to?",
                criteria=CATEGORIES,
            ),
            "recurring": Noul(
                instructions="This looks like a recurring payment such as a subscription or monthly bill"
            ),
        },
    )

    cat = response.answers["category"]
    return {
        "category": cat.choice,
        "confidence": cat.confidence,
        "probabilities": cat.probabilities,
        "recurring": response.answers["recurring"].noul,
        # Confidence gating: don't guess when Jev isn't sure.
        "final_category": cat.choice if cat.confidence >= CONFIDENCE_THRESHOLD else "needs_review",
    }


if __name__ == "__main__":
    # Quick smoke test: run `python categorizer.py`
    for desc in ["SWIGGY ORDER 4521", "NETFLIX.COM", "SHELL PETROL PUMP"]:
        print(desc, "->", categorize(desc))
