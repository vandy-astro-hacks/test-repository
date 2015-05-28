# Christina was here 

# Testing Updating...

# test-repository
just a blank repository for testing cloning/pushing/pulling

### setting up git
* make sure git is installed on your system
* create a user account and request to be added to the organization
* see this page for setting up git to connect to your account: https://help.github.com/articles/set-up-git/

### cloning a repository to your local machine
* copy the link found to the right under HTTPS clone URL
* in a terminal in the parent directory issue `git clone <copied-URL>`
* this will create a new directory with the name of the repository (test-repository in this case)

### updating your local version to match the repository
* cd into the repository directory (test-repository in this case)
* issue `git pull`

### editing an existing file
* make sure your local version is up-to-date
* edit any file using an editor of your choice
* `git status` to see what files you have changed since last pulling
* `git commit -a` will commit all your changes locally and will ask for you to provide a message describing your changes.  Note that this won't send anything to the server yet.
* Note that there are more advanced options if you don't want to commit all of your local changes
* `git push` will send your commit to the repository so that others can get your changes via `git pull`

### creating a new file
* make sure your local version is up-to-date
* create and edit a new file
* `git add <file>` to start tracking your new file
* `git commit -a` to commit locally
* `git push` to send your commit to the repository

### undo local changes
* to undo all of your local changes and revert everything to as it was last time you pulled, use `git reset --hard HEAD`
* to discard local changes for a specific file, use `git checkout HEAD <file>`

### other commands
* helpful cheat sheet: http://www.git-tower.com/blog/git-cheat-sheet/

### Meagan made edits
* look at the helpful edits Meagan made
