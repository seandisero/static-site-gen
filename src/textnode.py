from enum import Enum


class TextType(Enum):
    TEXT = ""
    BOLD = "**"
    ITALIC = "_"
    CODE = "`"
    LINK = "["
    IMAGE = "!"

class BlockType(Enum):
    PARAGRAPH = "p"
    HEADING = "h"
    CODE = "code"
    QUOTE = "blockquote"
    UNORDERED_LIST = "ul"
    ORDERED_LIST = "ol"


class TextNode():
    def __init__(self, text, text_type, url = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, value) -> bool:
        return self.text == value.text \
        and self.text_type == value.text_type \
        and self.url == value.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"


