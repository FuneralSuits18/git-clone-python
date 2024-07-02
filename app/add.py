import os

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
    index_entries = []
    try:
        if os.path.exists(index_file):
            with open(index_file, "rb") as f:
                index_entries = f.read().splitlines()

        for file_path in files:
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