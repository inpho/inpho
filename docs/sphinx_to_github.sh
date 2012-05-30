# This file is documenting the process of transfering inpho and
# inphosite sphinx documentation into github pages.

# ATTENTION: This file is not intended to run on the command line.
# The first section shows first-time setup and the second section
# is updating documentation when necessary.

# Beginning in the master branch in workingdir.
cd docs
rm -rf _build/html
cd ..

# Next (back in workingdir), check if .gitignore has _build. If not:
echo "_build" >> .gitignore
git add .gitignore
git commit -m 'ignoring _build'

# Back in workingdir/docs
cd docs
mkdir -p _build/html

# clone the entire repo into this new directory (project is either 
# inpho or inphosite).
git clone git@github.com:inpho/project.git _build/html

# move into that directory and set it to track gh-pages
cd _build/html
git symbolic-ref HEAD refs/heads/gh-pages
rm .git/index
git clean -fdx

# back in docs/ run 'make html' to generate documentation, which will
# fill _build/html, but not overwrite the .git directory
cd ../..
make html

# go back into _build/html and add the .html files to the gh-pages 
# repo. Also make .nojekyll:
cd _build/html
touch .nojekyll
git add .
git commit -m 'first docs to gh-pages'
git push origin gh-pages

# [optional] cleanup duplicate master repo on master branch (in _build/html)
git checkout master
rm .git/index
git clean -fdx

###------------------[DONE SETTING UP GH-PAGES]-------------------###

# All set up now! whenever it is necessary to make changes to the
# documentation, it can be done like this (start in /docs):

make html
cd _build/html
git commit -a -m 'updated documentation'
git push origin gh-pages
