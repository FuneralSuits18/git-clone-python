import sys
from init import create_init
from objects import read_blob, create_blob, list_tree, write_tree, create_commit_tree
from add import add


def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [options] [args]")
        sys.exit(1)
    
    command = sys.argv[1]

    if command == "init":
        create_init()
    elif command == "cat-file":
        if len(sys.argv) != 4:
            print("Usage: main.py cat-file <type> <object>")
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
            print("Usage: main.py hash-object [-w] <file>")
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
            print("Usage: main.py ls-tree [--name-only] <tree>")
            sys.exit(1)
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: main.py add <file>...")
            sys.exit(1)
        add(sys.argv[2:])
    elif command == "write-tree":
        sha = write_tree()
        print(sha)
    elif command == "commit-tree":
        if len(sys.argv) < 6:
            print("Usage: main.py commit-tree <tree_sha> [-p] [<commit_sha>] -m <message>")
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
