import os
import zlib
import hashlib
import time


def read_blob(blob_sha, flag=None):
    """Reads the content of a Git object.

    Usage: git.py cat-file -p <blob_sha>
    """
    try:
        if flag == "-p":
            with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", "rb") as f:
                blob = zlib.decompress(f.read())
            header, content = blob.split(b"\0", maxsplit=1)
            print(content.decode("utf-8"), end="")
    except FileNotFoundError:
        print(f"Error: blob not found.")
        sys.exit(1)


def create_blob(path, write=False, print_blob=True):
    '''Returns the SHA-1 hash of a file's content. Optionally writes blobs.

    Usage: git.py hash-object [-w] <file>
    '''
    try:
        with open(path, "r") as f:
            content = f.read()
        header = f"blob {len(content)}"
        hash_value_content = f"{header}\0{content}".encode()
        hash_value = hashlib.sha1(hash_value_content).hexdigest()

        if write:
            if not os.path.isdir(f".git/objects/{hash_value[:2]}"):
                os.mkdir(f".git/objects/{hash_value[:2]}")
            with open(f".git/objects/{hash_value[:2]}/{hash_value[2:]}", "wb") as blob:
                blob.write(zlib.compress(bytes(f"{header}\0{content}", "utf-8")))
        if print_blob:
            print(hash_value.strip("\n"), end="")
        return hash_value
    except FileNotFoundError:
        print(f"Error: file not found.")
        sys.exit(1)


def list_tree(tree_sha, name_only=False):
    '''Lists the entries of a Git tree.

    Usage: git.py ls-tree [--name-only] <tree>
    '''
    try:
        with open(f".git/objects/{tree_sha[:2]}/{tree_sha[2:]}", "rb") as f:
            tree = zlib.decompress(f.read())
        header, next_content = tree.split(b"\0", maxsplit=1)
        while next_content:
            mode, after_mode = next_content.split(b" ", maxsplit=1)
            name, after_name = after_mode.split(b"\0", maxsplit=1)
            sha = after_name[:20]
            next_content = after_name[20:]
            mode_name = "blob"
            if mode == b"100644":       # regular file
                mode = "100644"
            else:                       # directory
                mode = "040000"
                mode_name = "tree"
            if name_only:
                print(name.decode("utf-8"))
            else:
                print(f"{mode} {mode_name} {sha.hex()}    {name.decode("utf-8")}")
    except FileNotFoundError:
        print(f"Error: Tree object not found.")
        sys.exit(1)


def write_tree(path="./"):
    if os.path.isfile(path):
        return create_blob(path, write=True, print_blob=False)

    def sort_key(x):
        if os.path.isfile(f"{path}/{x}"):
            return x
        else:
            return f"{x}/"

    directories = sorted(os.listdir(path), key=sort_key)
    tree_obj_content = b""
    for directory in directories:
        if directory == ".git":
            continue
        full_path = f"{path}/{directory}"
        if os.path.isfile(full_path):       # only regular files and directories implemented
            mode = "100644"
        else:
            mode = "40000"
        header = f"{mode} {directory}\0".encode()
        sha = write_tree(full_path)
        tree_obj_content += header + bytes.fromhex(sha)

    tree_header = f"tree {len(tree_obj_content)}\0".encode()
    tree_obj_content = tree_header + tree_obj_content
    tree_sha = hashlib.sha1(bytes(tree_obj_content)).hexdigest()
    os.makedirs(f".git/objects/{tree_sha[:2]}", exist_ok=True)
    with open(f".git/objects/{tree_sha[:2]}/{tree_sha[2:]}", "wb") as f:
        f.write(zlib.compress(tree_obj_content))
    return tree_sha


def create_commit_tree(tree_sha, message, parent_sha=None):
    date_seconds = int(time.time())
    date_timezone = time.strftime("%z")

    author_name = "Chilli Powder"
    author_email = "chillipowder@spice.com"
    author_info = f"{author_name} <{author_email}> {date_seconds} {date_timezone}"

    writable_content = f"tree {tree_sha}\n"
    if parent_sha:
        writable_content += f"parent {parent_sha}\n"
    writable_content += f"author {author_info}\ncommitter {author_info}\n\n{message}\n"
    writable_content = writable_content.encode()

    header = f"commit {len(writable_content)}\0".encode()
    data = header + writable_content
    hash_value = hashlib.sha1(data).hexdigest()

    dir = f".git/objects/{hash_value[:2]}/"
    os.makedirs(dir, exist_ok=True)
    path = f"{dir}/{hash_value[2:]}"
    with open(path, "wb") as f:
        f.write(zlib.compress(data))

    return hash_value