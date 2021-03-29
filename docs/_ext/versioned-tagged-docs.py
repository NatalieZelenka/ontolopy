import git
from github import Github
from distutils.util import convert_path
import logging
import os
import shutil
import re


def copy_to_version(app, exception):
    """
    We keep versioned docs in two situations:
     - A new PR into dev from a feature branch (in versions/dev)
     - A new release on main (in versions/{versions})
    :param app:
    :param exception:
    :return:
    """

    # Get branch name, version number, and tag
    git_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(app.outdir))))
    repo = git.Repo(git_root)

    try:
        # This works if you're working locally, and you're on a branch rather than on a PR or release tag commit.
        branch_name = repo.active_branch.name
    except:
        commit = repo.commit()
        branch_name = repo.git.branch('--contains', commit.hexsha).strip('* ')
        logging.warning(f'Branch name: {branch_name}')

        gh = Github()
        gh_repo = gh.get_repo("NatalieThurlby/Ontolopy")

        pr_reg = re.findall(r'pull/(\d+)/', branch_name)
        release_reg = re.findall(r'(\d+\.\d+\.\d+?-\w+)', branch_name)

        # PR
        if len(pr_reg) != 0:
            assert(len(pr_reg) == 1)
            number = int(pr_reg[0])
            pr = gh_repo.get_pull(number)
            from_ = pr.head.label.split(':')[1]
            to_ = pr.base.label.split(':')[1]

            logging.warning(f'Detected detached HEAD state: PR from {from_} to {to_}.')
            branch_name = to_  # only want to keep where we're going to, e.g. feature_branch -> dev, version = "dev"
        # Release
        elif len(release_reg) != 0:
            assert(len(release_reg)) == 1
            release_id = release_reg[0]
            release = gh_repo.get_release(release_id)
            logging.warning(
                f'Detected detached HEAD state: due to release {release_id} on branch {release.target_commitish}')
            if release.prerelease:
                logging.warning(f"We don't keep versioned docs for pre-releases.")
            elif release.target_commitish == 'main':
                branch_name = release.target_commitish
            else:
                logging.error(f'Releases should only happen on branch "main", not branch {release.target_commitish}.')

    ns = {}
    ver_path = convert_path(os.path.join(git_root, 'ontolopy/version.py'))
    with open(ver_path) as ver_file:
        exec(ver_file.read(), ns)
    version = ns['__version__']

    tagged = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
    if not tagged:
        tag_name = None
    else:
        tag_name = tagged.name

    # Check that we have a correctly tagged release on the main branch.
    if branch_name not in ["main", "dev"]:
        logging.warning(f"On branch {branch_name}. Not saving versioned docs.")
        return None
    if branch_name == 'main' and not tagged:
        logging.warning("On branch main, but it is not tagged. Not saving versioned docs.")
        return None
    elif branch_name == 'main' and tagged and (tag_name != version):
        logging.error(f"Tag name ({tag_name}) and version ({version}) do not match.")

    # Copy built files to version dir
    logging.info(f"Copying built files to version directory for branch {branch_name}, tag {tag_name}.")
    if branch_name == 'main':
        version_dir = os.path.join(app.outdir, f'versions/{version}/')
    elif branch_name == 'dev':
        version_dir = os.path.join(app.outdir, f'versions/{branch_name}/')

    if not os.path.exists(version_dir):
        shutil.copytree(app.outdir, version_dir, ignore=shutil.ignore_patterns('versions'))
    else:
        os.system(f'rm -r {version_dir}')
        shutil.copytree(app.outdir, version_dir, ignore=shutil.ignore_patterns('versions'))

    # TODO: build json for dropdown (#9)


def setup(app):
    app.connect('build-finished', copy_to_version)

