import sys
import os
import zlib
import hashlib
import time


def create_init():
    """Initializes a new Git repository in the current directory."""
    try:
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    except FileExistsError:
        print(".git directory already exists.")


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


def add(files):
    '''Add files to staging area.
    
    Usage: git.py add <file>...")
    
    Limitations: 
    - file modes are not handled
    - no binary file support
    - less metadata in index file and less performance than the actual git add
    - no error handling.
    '''
    index_file = ".git/index"
    files_to_add = sys.argv[2:]
    index_entries = []
    try:
        if os.path.exists(index_file):
            with open(index_file, "rb") as f:
                index_entries = f.read().splitlines()

        for file_path in files_to_add:
            if os.path.isfile(file_path):
                sha = create_blob(file_path, write=True)
                index_entries.append(f"{sha} {file_path}")
            else:
                print(f"Error: File not found: {file_path}")
                sys.exit(1)

        with open(index_file, "w") as f:
            f.write("\n".join(index_entries))
    except FileNotFoundError:
        print(f"Error: file not found.")
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


def main():
    if len(sys.argv) < 2:
        print("Usage: git.py <command> [options] [args]")
        sys.exit(1)
    
    command = sys.argv[1]

    if command == "init":
        create_init()
    elif command == "cat-file":
        if len(sys.argv) != 4:
            print("Usage: git.py cat-file <type> <object>")
            sys.exit(1)
        blob_sha = sys.argv[3]
        flag = sys.argv[2]
        read_blob(blob_sha, flag)
    elif command == "hash-object":
        if len(sys.argv) == 3:
            sha = create_blob(sys.argv[2])
        elif len(sys.argv) == 4:
            write = "-w" in sys.argv
            sha = create_blob(sys.argv[3], write)
        else:
            print("Usage: git.py hash-object [-w] <file>")
            sys.exit(1)
    elif command == "ls-tree":
        if len(sys.argv) == 3:
            tree_sha = sys.argv[2]
            list_tree(tree_sha)
        elif len(sys.argv) == 4:
            name_only = "--name-only" in sys.argv
            tree_sha = sys.argv[3]
            list_tree(tree_sha, name_only)
        else:
            print("Usage: git.py ls-tree [--name-only] <tree>")
            sys.exit(1)
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: git.py add <file>...")
            sys.exit(1)
        add(sys.argv[2:])
        add()
    elif command == "write-tree":
        sha = write_tree()
        print(sha)
    elif command == "commit-tree":
        if len(sys.argv) < 6:
            print("Usage: git.py commit-tree <tree_sha> [-p] [<commit_sha>] -m <message>")
            sys.exit(1)
        tree_sha = sys.argv[2]
        message = None
        parent_sha = None
        if sys.argv[3] == "-p":
            parent_sha = sys.argv[4]
            message = sys.argv[6]
        else:
            message = sys.argv[4]
        sha = create_commit_tree(tree_sha, message, parent_sha)
        print(sha)
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
