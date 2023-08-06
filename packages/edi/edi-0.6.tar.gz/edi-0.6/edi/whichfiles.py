import os, re, sys, subprocess

def list_directory_files_recursively(directory):
    """Get a list of all files in a subdirectory, recursively."""
    filelist = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filelist.append(os.path.join(root, filename))
    return filelist
      
def uncommitted():
    """List of uncommitted files in the repository."""
    filenames = []
    for line in subprocess.check_output(["git", "status", "-s"]).split("\n"):
        if line != "":
            filenames.append(line[3:])
    
    filenames_and_directories_that_exist = [filename for filename in filenames if os.path.exists(filename)]
    
    # Expand directories
    filenames = []
    for filename_or_directory in filenames_and_directories_that_exist:
        if os.path.isdir(filename_or_directory):
            for subdirectory_filename in list_directory_files_recursively(filename_or_directory):
                filenames.append(subdirectory_filename)
        else:
            filenames.append(filename_or_directory)
    
    filenames_sorted = sorted(filenames, key=os.path.getctime, reverse=True)
    return filenames_sorted

def lastedited(howmany=10):
    """List of files most recently modified by the current user."""
    try:
        your_email = subprocess.check_output(["git", "config", "user.email"]).replace("\n", "")
    except:
        sys.stderr.write("I don't know who you are. Use 'git config user.email' to specify your email address.\n")
        sys.exit(1)


    # List of which files changed (figure out which of those the current user changed).
    my_commits = False
    my_filename_lines = []
    
    for line in subprocess.check_output(["git", "whatchanged", "--pretty=format:\"%ae\"", "-n", "512",]).split("\n"):
        if re.compile(r"\"(.*?)\@(.*?)\"").match(line) is not None:
            my_commits = (line == "\"{0}\"".format(your_email))
        elif line == "":
            pass
        else:
            if my_commits == True:
                my_filename_lines.append(line)
    
    last_changed_files = uncommitted()
    
    # Append the list of files which the user changed and committed to the list of uncommitted files.
    for filename_line in my_filename_lines:
        filename = filename_line[39:]
        if filename not in last_changed_files and os.path.exists(filename):
            last_changed_files.append(filename)

    # Order by reverse modification date.
    last_changed_files = sorted(last_changed_files, key=os.path.getctime, reverse=True)
    return last_changed_files[:howmany]

def f7(seq):
    """Remove duplicates from a list while preserving order.
    - Stolen from: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order.
    - Yes, an ordered dict would be cleaner, but this is apparently a bit faster and not that ugly a hack."""
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def keyword(keywords):
    """List of files matching the keyword list specified."""
    git_ls_files_that_exist = [x for x in subprocess.check_output(["git", "ls-files"]).split("\n") if os.path.exists(x)]
    git_ls_filelist = sorted(git_ls_files_that_exist, key=os.path.getctime, reverse=True) 
    filelist = uncommitted() + git_ls_filelist
    matches = []

    for filename in filelist:
        match = True
        for keyword in keywords:
            if keyword.lower() not in filename.lower():
                match = False
        if match:
            matches.append(filename)

    matches = f7(matches)
    return matches
