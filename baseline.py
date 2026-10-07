"""A dumb keyword baseline. If Jev can't beat this, you don't need AI."""
KEYWORDS = {
    "food": ["swiggy", "zomato", "restaurant", "cafe", "starbucks", "mcdonald", "pizza", "dominos"],
    "groceries": ["bigbasket", "blinkit", "zepto", "dmart", "supermarket", "grocery", "reliance fresh"],
    "transport": ["uber", "ola", "petrol", "fuel", "metro", "parking", "toll", "shell"],
    "bills": ["electricity", "airtel", "jio", "broadband", "rent", "insurance", "water bill"],
    "shopping": ["amazon", "flipkart", "myntra", "zara", "ikea", "croma"],
    "entertainment": ["netflix", "spotify", "bookmyshow", "pvr", "steam", "hotstar"],
    "health": ["pharmacy", "apollo", "clinic", "hospital", "gym", "cult.fit", "lab"],
    "travel": ["irctc", "makemytrip", "indigo", "airbnb", "booking.com", "hotel"],
}


def baseline_categorize(description: str) -> str:
    d = description.lower()
    for category, words in KEYWORDS.items():
        if any(w in d for w in words):
            return category
    return "other"
