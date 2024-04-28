from dataclasses import dataclass
from typing import List

@dataclass
class Profile:
    name: str
    relation: str
    pictures: str  # List of picture URLs or filenames
