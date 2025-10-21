from textnode import TextNode
import os
import shutil

from core import generate_page

dir_path_public = "./public"
dir_path_content = "./content"
template_path = "./template.html"

def copy_to_public(dest, p):
    if os.path.isdir(p):
        print(f"path exists for {dest}: {os.path.exists(dest)}")
        if not os.path.exists(dest+"/"):
            print(f"making dir {p}")
            os.mkdir(dest+"/")
        for name in os.listdir(p):
            copy_to_public(f"{dest}/{name}", f"{p}/{name}")
    if os.path.isfile(p):
        # print(f"trying to copy from {p} to {os.path.dirname(dest)}/")
        shutil.copy(p, os.path.dirname(dest) + "/")

def copy_static():
    current_dir = os.getcwd()
    if os.path.exists(dir_path_public):
        shutil.rmtree(dir_path_public)
    os.mkdir(dir_path_public)
    static_dir = current_dir + "/" + "static"
    if os.path.exists(static_dir):
        for path in os.listdir(static_dir):
            copy_to_public(f"{dir_path_public}/{path}", f"{static_dir}/{path}")

def main():
    copy_static()

    generate_page(
        os.path.join(dir_path_content, "index.md"),
        template_path, 
        os.path.join(dir_path_public, "index.html"),
    )

if __name__ == "__main__":
    main()

