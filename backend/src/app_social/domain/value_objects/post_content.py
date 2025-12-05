from dataclasses import dataclass

@dataclass
class PostContent:
    title: str
    text: str
    images: tuple
    tags: tuple