# utils/helpers.py
import requests


def categorize_task(title, description):
    content = (title + " " + description).lower()

    categories = {
        "Work": ["assignment", "project", "work", "submit", "client", "report", "deadline", "meeting"],
        "Health": ["gym", "run", "walk", "doctor", "appointment", "medicine", "exercise", "yoga"],
        "Personal": ["birthday", "party", "call", "meet", "hangout", "dinner", "friends", "family"],
        "Finance": ["pay", "bill", "bank", "salary", "invoice", "transfer", "loan", "rent"],
        "Errands": ["groceries", "shopping", "market", "buy", "order", "cleaning", "repair"]
    }

    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category

    return "Other"


