import re, os

from textnode import TextType, TextNode, BlockType
from htmlnode import HTMLNode, ParentNode, text_node_to_html_node  

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md = ""
    template = ""
    with open(from_path, "r") as f:
        md = f.read()
    with open(template_path, "r") as f:
        template = f.read()
    
    node = markdown_to_html_node(md)
    html = node.to_html()

    title = extract_title(md)
    template = template.replace("{{title}}", title)
    template = template.replace("{{content}}", html)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template)
    to_file.close()


def extract_title(markdown: str):
    line_list = markdown.split("\n")
    if len(line_list) < 1: raise Exception("no title")
    if line_list[0][0] != "#": raise Exception("no title")
    if line_list[0][1] == "#": raise Exception("malformed title")
    return line_list[0][1:].strip()

def extract_markdown_images(text):
    matches = re.findall(r'!\[(.+?)\]\((.+?)\)', text)
    return matches

def extract_markdown_link(text):
    matches = re.findall(r'(?<!!)\[(.+?)\]\((.+?)\)', text) # (?<!!)specifies that ! cann not prefex the text -> not supported in all browsers
    return matches

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    text_blocks = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            text_blocks.append(node)
            continue
        new_nodes = []
        sections = node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid text in nodes delimiter")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                new_nodes.append(TextNode(sections[i], text_type))
        text_blocks.extend(new_nodes)
    return text_blocks


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        text = node.text
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        nodes = []
        image_text = extract_markdown_images(text)
        for i in image_text:
            text = text.replace(f"![{i[0]}]({i[1]})", "*")
        text_split = text.split("*")
        j, k = 0, 0
        for i in range(len(image_text)+len(text_split)):
            if i % 2 == 0:
                if text_split[j] == "":
                    j += 1
                    continue
                nodes.append(TextNode(text_split[j], TextType.TEXT))
                j += 1
            elif i % 2 == 1:
                nodes.append(TextNode(image_text[k][0], TextType.IMAGE, image_text[k][1]))
                k+=1
        new_nodes.extend(nodes)
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        text = node.text
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        nodes = []
        image_text = extract_markdown_link(text)
        for i in image_text:
            text = text.replace(f"[{i[0]}]({i[1]})", "*")
        text_split = text.split("*")
        j, k = 0, 0
        for i in range(len(image_text)+len(text_split)):
            if i % 2 == 0:
                if text_split[j] == "":
                    j += 1
                    continue
                nodes.append(TextNode(text_split[j], TextType.TEXT))
                j += 1
            elif i % 2 == 1:
                nodes.append(TextNode(image_text[k][0], TextType.LINK, image_text[k][1]))
                k+=1
        new_nodes.extend(nodes)
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
 

def markdown_to_blocks(document):
    blocks = document.split("\n\n")
    clean_blocks = []
    for i in range(len(blocks)):
        stripped = '\n'.join([i.strip() for i in blocks[i].split("\n") if i.strip() != ''])
        clean_blocks.append(stripped)
    return clean_blocks

def starts_with_digit_dot(text):
    was_digit = False
    for i in range(len(text)):
        if text[i].isdigit():
            was_digit = True
        if text[i] == '.' and was_digit:
            return True
        if text[i] == ' ':
            return False
    return False

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")

# this should reuturn an html node of the proper type
# and I should implement specific functions for the creation of teach type 
# of html node. I need to stop thinking in an oop manner and start thinking 
# functionaly, and this will be a lot easier. Don't be lazy and just do the work.
def block_to_block_type(block):
    if block.startswith("#"):
        return BlockType.HEADING
    elif block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    elif block.startswith(">"):
        return BlockType.QUOTE
    elif block.startswith("-"):
        return BlockType.UNORDERED_LIST
    elif starts_with_digit_dot(block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def children_to_html(items, html_list):
    if isinstance(items, list):
        for i in items:
            html_list.append(children_to_html(i, html_list))
    else: 
        html_node = text_node_to_html_node(items)
        return html_node


#
# def text_to_children(text, tag):
#     t = None
#     if tag == "ul" or tag == "ol":
#         t = "li"
#     split = text.split("\n")
#     children = []
#     for s in split:
#         node = HTMLNode(t)
#         html_list = []
#         children_to_html(text_to_textnodes(s), html_list)
#         node.children = html_list
#         children.append(node)
#     return children 

# I need to think more simply and step by step.
# markdown to blocks -> for each block -> block to html node append as children to list
# -> return a parent div node with all the children html nodes.
def generate_html(document):
    blocks = markdown_to_blocks(document)
    for b in blocks:
        block_type = block_to_block_type(b)
        html_node = HTMLNode(block_type, None, None, None)
        children = []
        if block_type == BlockType.HEADING:
            children = text_to_children(b)#, None)
        if block_type == BlockType.UNORDERED_LIST:
            children = text_to_children(b)#, "ul")
        html_node.children = children
        print(html_node)


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("invalid code block")
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

mkdown = """
# this is my header

- this 
- is **a** 
- list

1. this 
2. is _a_ 
3. ordered
4. list

> wow a quote

lets put in some _random_ text because **I** can.

```import this```
""" 


print(generate_html(mkdown))


