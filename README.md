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
* `git add -p <file>` to add a single file to your next commit or `git add .` to add all changes (this does not actually send anything to the server, but just "stages" them)
* `git commit -a` commit all "staged" changes
