import git
from distutils.util import convert_path
from distutils import dir_util
import logging

# Get branch name, version number, and tag
repo = git.Repo('.')
branch_name = repo.active_branch.name

ns = {}
ver_path = convert_path('ontolopy/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)
version = ns['__version__']

tagged = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)

# Check that we have a correctly tagged release on the main branch.
if not tagged:
    logging.error("This branch is not tagged.")
if tagged.name != version:
    logging.error(f"Tag name ({tagged.name}) and version ({version}) do not match.")
if branch_name != "main":
    logging.error(f"We only deploy docs of releases to the main branch. You're on branch: {branch_name}")

# Copy already built files into gh-pages version
branch_names = [x.name for x in repo.branches]
if 'gh-pages' not in branch_names:
    logging.error("No branch named gh-pages!")

try:
    repo.git.checkout('gh-pages')
    repo.git.checkout('doc/build/html/', 'main')
    dir_util.copy_tree("doc/build/html/", f"versions/{version}/")
except:
    print("failed")

