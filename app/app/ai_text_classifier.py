import re

BUYER_PATTERNS = [
    r"\blooking for\b",
    r"\bwant to buy\b",
    r"\bneed (a|an)\b",
    r"\bseeking\b",
    r"\bin search of\b"
]

SELLER_PATTERNS = [
    r"\bfor sale\b",
    r"\bselling\b",
    r"\bfsbo\b",
    r"\basking\b",
    r"\bprice\b"
]

def classify_post(text: str) -> str:
    t = text.lower()

    for p in BUYER_PATTERNS:
        if re.search(p, t):
            return "buyer"

    for p in SELLER_PATTERNS:
        if re.search(p, t):
            return "seller"

    return "ignore"
