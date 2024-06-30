import sys
import os
import zlib
import hashlib


def init():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")


# read blob
def cat_file():
    if sys.argv[2] == "-p":
        blob_sha = sys.argv[3]
        with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as file:
            blob = zlib.decompress(file.read())
            header, content = blob.split(b"\0", maxsplit=1)
            print(content.decode("utf-8"), end="")


# create blob
def hash_object():
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

# read tree
def ls_tree():
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


def add():
    index_file = ".git/index"
    files_to_add = sys.argv[2:]     # List of files passed as arguments
    index_entries = []

    if os.path.exists(index_file):
        with open(index_file, "rb") as f:
            index_entries = f.read().splitlines()

    for file_path in files_to_add:
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read()
            header = f"blob {len(content)}"
            blob_data = bytes(f"{header}\0{content}", "utf-8")
            blob_sha = hashlib.sha1(blob_data).hexdigest()

            if not os.path.isdir(f".git/objects/{blob_sha[:2]}"):
                os.mkdir(f".git/objects/{blob_sha[:2]}")
            with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "wb") as blob:
                blob.write(zlib.compress(blob_data))

            index_entries.append(f"{blob_sha} {file_path}")

    with open(index_file, "w") as f:
        f.write("\n".join(index_entries))

    print(f"Added {len(files_to_add)} files to the index")


def main():
    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "cat-file":
        cat_file()
    elif command == "hash-object":
        hash_object()
    elif command == "ls-tree":
        ls_tree()
    elif command == "add":
        add()
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
