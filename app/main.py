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
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
