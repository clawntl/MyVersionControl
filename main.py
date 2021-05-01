import hashlib, os, configparser
from math import ceil

"""
TODO:
.gitignore
folders

"""

directory = r""

def iterationProgressBar(iteration, total, decimal_places=1, length=50, fill ="█", prefix = "", suffix = "", printEnd ="\r"):
    #Progress bar for the console
    
    #Work out the percentage complete
    percentage = f"{(100 * (iteration/float(total))):.{str(decimal_places)}f}"
    #Work out how much of the far should be filled
    filled = int(length * iteration // total)
    
    bar = (fill * filled) + ('-' * (length - filled))
    
    print(f'\r{prefix} |{bar}| {percentage}% {suffix}', end=printEnd)
    
    #Print a new line once finished
    if iteration == total: 
        print()

def rel_path(relative_path):
    global directory
    return os.path.join(directory, relative_path)

def find_files(_dir):
    # Add all files in dir an add to list
    items = []
    for entry in os.scandir(_dir):
        if entry.is_file():      #Only add if files
            items.append(entry)
            #print(entry.path)
            
    return items

def copy_file(file_1, file_2, BUFFER_SIZE=65536, progressBar=True):
    file_size = os.path.getsize(file_1)
    iters = ceil(file_size/BUFFER_SIZE) + 1
    
    with open(file_1, "rb") as f1, open(file_2, "wb") as f2:
        idx = 1 
        iterationProgressBar(0, iters, prefix = 'Progress:', suffix = 'Complete', length = 50) if progressBar else None
        while True:
            iterationProgressBar(idx, iters, prefix = 'Progress:', suffix = 'Complete', length = 50) if progressBar else None
            data = f1.read(BUFFER_SIZE)
            if not data:
                break
            f2.write(data)
            idx += 1

def delete_files(path):
    for i in find_files(path):
        os.remove(os.path.join(path, i.name))

def init():
    version_path = rel_path(f".versions\\revisions\\")
    if not os.path.isdir(version_path):
        os.makedirs(version_path)
        return ">Initialised Successfully"
    else:
        return ">Error: Already initialised"
    
def backup(BUFFER_SIZE=65536):
    global directory
      
    #Get the path to store the version and create if doesn't exist
   
    version_path = rel_path(f".versions\\checkout_backup\\")
    if os.path.isdir(version_path):
        delete_files(version_path)
    else:
        os.makedirs(version_path)
    
    #Get all items in working dir
    items = find_files(directory)
    
    #Hash each items in working dir
    for item in items:
        #Generate hash using a buffer to save memory
        sha1 = hashlib.sha1()
        with open(rel_path(item), "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)
    
        # Copy the file and store it with the filename in format "hash filename .txt"
        copy_file(rel_path(item), (version_path + f"{sha1.hexdigest()} {item.name} .txt"), progressBar=False)
    
def commit(BUFFER_SIZE=65536):
    global directory
    
    #Count the current number of revisions
    version_number = len([name for name in os.scandir(rel_path(f".versions\\revisions")) if name.is_dir()])
    
    #Get the path to store the version and create if doesn't exist
    
    version_path = rel_path(f".versions\\revisions\\{version_number+1}\\")
    if not os.path.isdir(version_path):
        os.makedirs(version_path)
    
    #Get all items in working dir
    items = find_files(directory)
    
    #Hash each items in working dir
    for item in items:
        #Generate hash using a buffer to save memory
        sha1 = hashlib.sha1()
        with open(rel_path(item), "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)
    
        # Copy the file and store it with the filename in format "hash filename .txt"
        copy_file(rel_path(item), (version_path + f"{sha1.hexdigest()} {item.name} .txt"))
    
    return f">Committed Successfully as version {version_number+1}"
                    
def restore(BUFFER_SIZE=65536):
    global directory
    
    version_path = rel_path(f".versions\\checkout_backup\\")
    if not os.path.isdir(version_path):
        return ">Error: No Backup Exists"
    
    #Get all items in working dir
    items = find_files(directory)
    working_directory_files = []

    #Hash each items in working dir
    for item in items:
        sha1 = hashlib.sha1()
        with open(rel_path(item), "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)
        working_directory_files.append({"hash": sha1.hexdigest(), "filename": item.name})

    #Get all items from version
    version_items = find_files(version_path)

    #Get the version files into dictionaries for easier comparison
    version_files = []
    for version_item in version_items:
        name_split = version_item.name.split()
        version_files.append({"hash": name_split[0], "filename": name_split[1]})
    
    
    #Update any files if not changed or create if they don't exist in the working dir
    for i in version_files:
        if i not in working_directory_files:
            copy_file(os.path.join(version_path, f"{i['hash']} {i['filename']} .txt"), rel_path(i["filename"]))
    
    #Delete any files from working dir that are not present in the version
    for j in working_directory_files:
        if j not in version_files:
            os.remove(rel_path(j["filename"]))
        
    
    delete_files(rel_path(f".versions\\checkout_backup\\"))
    os.rmdir(rel_path(f".versions\\checkout_backup\\"))
    return ">Restored successfully"

def checkout(version_number, BUFFER_SIZE=65536, back_up=True):
    global directory
    
    #Get path of version to checkout
    version_path = rel_path(f".versions\\revisions\\{version_number}\\")
    if not os.path.isdir(version_path):
        return ">Error: Version Doesn't Exists"
    
    #Create a backup of the working dir first
    if back_up:
        backup()
    
    #Get all items in working dir
    items = find_files(directory)
    working_directory_files = []

    #Hash each items in working dir
    for item in items:
        sha1 = hashlib.sha1()
        with open(rel_path(item), "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha1.update(data)
        working_directory_files.append({"hash": sha1.hexdigest(), "filename": item.name})

    #Get all items from version
    version_items = find_files(version_path)

    #Get the version files into dictionaries for easier comparison
    version_files = []
    for version_item in version_items:
        name_split = version_item.name.split()
        #Have to account for file names with spaces
        name_split = [
            name_split[0],
            " ".join(name_split[1:-1]),
            name_split[-1]
        ]
        version_files.append({"hash": name_split[0], "filename": name_split[1]})
    
    
    #Update any files if not changed or create if they don't exist in the working dir
    for i in version_files:
        if i not in working_directory_files:
            copy_file(os.path.join(version_path, f"{i['hash']} {i['filename']} .txt"), rel_path(i["filename"]))
    
    #Delete any files from working dir that are not present in the version
    for j in working_directory_files:
        if j not in version_files:
            os.remove(rel_path(j["filename"]))
        
    return ">Checked-out successfully"
    
def main():
    global directory

    #Config system to store the project dir in a ini file
    config = configparser.ConfigParser()
    if not os.path.isfile("config.ini"):
        config["Settings"] = {"directory": input("Please enter the project directory >")}
        with open("config.ini", "w") as configfile:
            config.write(configfile)
    else:
        config.read("config.ini")
    directory = config["Settings"]["directory"]
    
    #Initialise if needed
    if not os.path.isdir(rel_path(".versions")):
        init()
    
    #Command line interface
    while True:
        cmd = input(">").split()
 
        if cmd[0] == "commit":
            print(commit())
            
        elif cmd[0] == "checkout":
            if "-nb" in cmd[2:] or "--nobackup" in cmd[2:]:
                print(checkout(int(cmd[1]), back_up=False))
            else:
                print(checkout(int(cmd[1])))
            
        elif cmd[0] == "restore":
            print(restore())
            
        elif cmd[0] == "exit":
            break

        elif cmd[0] == "help":
            data = [
                ["\nCommands:"],
                ["commit", "Saves a version"],
                ["checkout <version> [options]", "Overrides the working directory with <version>"],
                ["restore", "Undoes previous checkout"],
                ["exit", "Close program"],
                ["\nCheckout Options:"],
                ["-nb, --nobackup", "Doesn't create a backup (useful for saving space)"]
            ]
            #Formatting
            col_width = max(len(word) for row in data for word in row) - 18
            for row in data:
                print("".join(word.ljust(col_width) for word in row))
                

if __name__ == "__main__":
    main()