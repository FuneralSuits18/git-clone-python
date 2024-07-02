# Git Implementation in Python

A Python script that implements basic Git functionalities such as:

- Initializing a repository
- Reading blobs
- Creating blobs
- Listing trees
- Adding files to staging area
- Writing tree objects
- Creating commits

This project was completed with the help of [CodeCrafters](https://app.codecrafters.io/catalog).

## Usage
### Initialize a Git repository:
`python main.py init`  

### Read a blob object:
`python main.py cat-file -p <blob_sha>`

### Create a blob object:
`python main.py hash-object [-w] <file>`

### List entries in a tree object:
`python main.py ls-tree [--name-only] <tree_sha>`

### Add files to staging area:
`python main.py add <file>...`

### Write a tree object:
`python main.py write-tree`

### Create a commit using a tree object:
`python main.py commit-tree <tree_sha> [-p <parent_commit_sha>] -m <message>`

Replace `<arguments>` with actual values as needed.