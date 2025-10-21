import unittest

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "this is a paragraph", props={"href": "https://www.google.com", "target": "_blank"})
        node2 = HTMLNode("p", "this is a paragraph", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node, node2)
    
    def test_print(self):
        node = HTMLNode("p", "this is a paragraph", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.__repr__(), 'HTMLNode(p, this is a paragraph, None,  href="https://www.google.com" target="_blank")')

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "hello world")
        self.assertEqual(node.to_html(), "<p>hello world</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "hello google", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">hello google</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", children=[child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(node.to_html(), '<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>')

    def test_no_children_error(self):
        try:
            node = ParentNode("p", [])
            node.to_html()
        except Exception as ex:
            self.assertEqual(str(ex), "ParentNode must have children")
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

if __name__ == "__main__":
    unittest.main()
