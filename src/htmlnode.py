from textnode import TextNode, TextType


class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props: dict | None=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if self.props is not None:
            return " " + " ".join([f'{i.strip('\"')}="{j}"' for i, j in self.props.items()])
        return ""

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props_to_html()})"

    def __eq__(self, other) -> bool:
        return self.tag == other.tag \
        and self.value == other.value \
        and self.children == other.children \
        and self.props == other.props

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props: dict | None = None) -> None:
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props: dict | None = None) -> None:
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if self.children is None or len(self.children) == 0:
            raise ValueError("ParentNode must have children")
        for child in self.children:
            if child.value is None and isinstance(child, LeafNode):
                raise ValueError("Children must have values")
        return f'<{self.tag}>{"".join([i.to_html() for i in self.children])}</{self.tag}>'

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text, props={"href":text_node.url})
        case TextType.IMAGE:
            return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node.text})
    return LeafNode(None, None)
