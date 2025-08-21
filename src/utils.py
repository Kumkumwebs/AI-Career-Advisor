import json
import re
from typing import List, Set

def load_skills(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_skills(text: str, taxonomy: List[str]) -> List[str]:
    text_l = text.lower()
    found = []
    for sk in taxonomy:
        # simple contains match; can be improved with tokenization/lemmatization
        if sk in text_l:
            found.append(sk)
    # deduplicate while preserving order
    seen: Set[str] = set()
    unique = []
    for s in found:
        if s not in seen:
            unique.append(s); seen.add(s)
    return unique
