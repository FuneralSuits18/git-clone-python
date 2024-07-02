import os
import pytest
import hashlib
import zlib
from git import create_init, create_blob, read_blob, list_tree, write_tree, create_commit_tree

def test_create_init(tmp_path):
    os.chdir(tmp_path)

    create_init()
    assert os.path.isdir(".git")
    assert os.path.isdir(".git/objects")
    assert os.path.isdir(".git/refs")
    assert os.path.isfile(".git/HEAD")

    with open(".git/HEAD", "r") as f:
        content = f.read()
    assert content in ["ref: refs/heads/main\n", "ref: refs/heads/master\n"]

def test_read_blob(tmp_path, capsys):
    os.chdir(tmp_path)
    create_init()
    capsys.readouterr()

    content = b"custard with mangoes"
    blob = b"blob " + str(len(content)).encode() + b"\0" + content
    sha = hashlib.sha1(blob).hexdigest()
    
    os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
        f.write(zlib.compress(blob))
    
    read_blob(sha, "-p")
    
    captured = capsys.readouterr()
    
    assert captured.out == "custard with mangoes"
    assert captured.err == ""

def test_create_blob(tmp_path):
    os.chdir(tmp_path)
    create_init()

    with open("test.txt", "w") as f:
        f.write("clock is ticking")
    
    sha = create_blob("test.txt", write=True, print_blob=False)

    assert len(sha) == 40
    assert os.path.isfile(f".git/objects/{sha[:2]}/{sha[2:]}")

def test_list_tree(tmp_path, capsys):
    os.chdir(tmp_path)
    create_init()

    os.mkdir("subdir")
    with open("list_tree.txt", "w") as f:
        f.write("Up up and away")
    with open("subdir/list_tree2.txt", "w") as f:
        f.write("stray cat")
    
    tree_sha = write_tree()
    list_tree(tree_sha)

    captured = capsys.readouterr()

    assert "100644 blob" in captured.out
    assert "040000 tree" in captured.out
    assert "list_tree.txt" in captured.out
    assert "subdir" in captured.out

def test_write_tree(tmp_path):
    os.chdir(tmp_path)
    create_init()

    os.mkdir("subdir")
    with open("write_tree.txt", "w") as f:
        f.write("White ballons")
    with open("subdir/write_tree2.txt", "w") as f:
        f.write("Clouds of change")
    
    tree_sha = write_tree()

    assert len(tree_sha) == 40
    assert os.path.isfile(f".git/objects/{tree_sha[:2]}/{tree_sha[2:]}")

def test_create_commit_tree(tmp_path):
    os.chdir(tmp_path)
    create_init()

    with open("commit_tree.txt", "w") as f:
        f.write("Faded depth")
    
    tree_sha = write_tree()
    commit_sha = create_commit_tree(tree_sha, "Last commit")
    
    assert len(commit_sha) == 40
    assert os.path.isfile(f".git/objects/{commit_sha[:2]}/{commit_sha[2:]}")

if __name__ == "__main__":
    pytest.main()