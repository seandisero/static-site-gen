import unittest 

from textnode import BlockType, TextNode, TextType
from core import extract_title, extract_markdown_images, split_nodes_image, text_to_textnodes, markdown_to_blocks, block_to_block_type

class TestCore(unittest.TestCase):

    def test_extract_markdown_title(self):
        text = "# Hello"
        match = extract_title(text)
        self.assertEqual(match, "Hello")
        try:
            text = "## Hello"
            match = extract_title(text)
        except Exception as e:
            self.assertEqual(e.args[0], "malformed title")


    def test_extract_markdown_images(self):
        text = "This is text with a link ![to boot dev](https://www.boot.dev) and ![to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
        [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
            ),
        ],
        new_nodes,
    )

    def test_together(self):
        in_text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        out_list = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        nodes = text_to_textnodes(in_text)
        self.assertEqual(nodes, out_list)

    def test_markdown_to_blocks(self):
        md = """
            This is **bolded** paragraph

            This is another paragraph with _italic_ text and `code` here
            This is the same paragraph on a new line

            - This is a list
            - with items
        """
        blocks = markdown_to_blocks(md)
        print(blocks)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_get_block_type_paragraph(self):
        block = "this is a paragraph"
        type = block_to_block_type(block)
        self.assertEqual(type, BlockType.PARAGRAPH)

    def test_get_block_type_heading(self):
        block = "## this is a heading"
        type = block_to_block_type(block)
        self.assertEqual(type, BlockType.HEADING)

    def test_get_block_type_code(self):
        block = "``` this is code ```"
        type = block_to_block_type(block)
        self.assertEqual(type, BlockType.CODE)

    def test_get_block_type_quote(self):
        block = "> this is a quote"
        type = block_to_block_type(block)
        self.assertEqual(type, BlockType.QUOTE)
        
    def test_get_block_type_orderedlist(self):
        block = "1. this is an ordered list"
        type = block_to_block_type(block)
        self.assertEqual(type, BlockType.ORDERED_LIST)

if __name__ == "__main__":
    unittest.main()

