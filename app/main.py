import sys
import os
import zlib
import hashlib


def read_blob():
    if sys.argv[2] == "-p":
        blob_sha = sys.argv[3]
        with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as file:
            blob = zlib.decompress(file.read())
            header, content = blob.split(b"\0", maxsplit=1)
            print(content.decode("utf-8"), end="")


def create_blob():
    with open(sys.argv[3], "r") as file:
        content = file.read()
        header = f"blob {len(content)}"
        hash_value = hashlib.sha1(bytes(f"{header}\0{content}", "utf-8")).hexdigest()
        print(hash_value.strip("\n"), end="")
        if sys.argv[2] == "-w":
            if not os.path.isdir(f".git/objects/{hash_value[:2]}"):
                os.mkdir(f".git/objects/{hash_value[:2]}")
            with open(f".git/objects/{hash_value[:2]}/{hash_value[2:]}", "wb") as blob:
                blob.write(zlib.compress(bytes(f"{header}\0{content}", "utf-8")))

def read_tree():
    tree_sha = sys.argv[3]
    with open(f".git/objects/{tree_sha[:2]}/{tree_sha[2:]}", "rb") as file:
        tree = zlib.decompress(file.read())
        header, next_content = tree.split(b"\x00", maxsplit=1)
        while next_content:
            mode, after_mode = next_content.split(b" ", maxsplit=1)
            name, after_name = after_mode.split(b"\x00", maxsplit=1)
            sha = after_name[:20]
            next_content = after_name[20:]
            mode_name = "blob"
            if mode == b"100644":       # regular file
                mode = "100644"
            elif mode == b"100755":     # executable file
                mode = "100755"
            elif mode == b"120000":     # symbolic link
                mode = "120000"
            elif mode == b"040000":     # directory
                mode = "040000"
                mode_name = "tree"
            else:                       # gitlink / submodule (repos nested in other repos)
                mode = "160000"
                mode_name = "submodule"
            if sys.argv[2] == "--name-only":        # only this flag is implemented
                print(name.decode("utf-8"))
            else:
                print(f"{mode} {mode_name} {sha.hex()}    {name.decode("utf-8")}")




def main():
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        read_blob()
    elif command == "hash-object":
        create_blob()
    elif command == "ls-tree":
        read_tree()
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
