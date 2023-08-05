"""dodo file. test + management stuff"""

import glob
import os

import pytest
from doitpy.pyflakes import Pyflakes
from doitpy.coverage import Config, Coverage, PythonPackage
from doitpy import docs
from doitpy.package import Package


from doit.tools import create_folder

DOIT_CONFIG = {
    'minversion': '0.24.0',
    'default_tasks': ['pyflakes', 'ut'],
#    'backend': 'sqlite3',
    }

CODE_FILES = glob.glob("doit/*.py")
TEST_FILES = glob.glob("tests/test_*.py")
TESTING_FILES = glob.glob("tests/*.py")
PY_FILES = CODE_FILES + TESTING_FILES


def task_pyflakes():
    flaker = Pyflakes()
    yield flaker('dodo.py')
    yield flaker.tasks('doit/*.py')
    yield flaker.tasks('tests/*.py')

def run_test(test):
    return not bool(pytest.main(test))
    #return not bool(pytest.main("-v " + test))
def task_ut():
    """run unit-tests"""
    for test in TEST_FILES:
        yield {'name': test,
               'actions': [(run_test, (test,))],
               'file_dep': PY_FILES,
               'verbosity': 0}


def task_coverage():
    """show coverage for all modules including tests"""
    cov = Coverage([PythonPackage('doit', 'tests')],
                   config=Config(branch=False, parallel=True,
                          omit=['tests/myecho.py', 'tests/sample_process.py'],)
                   )
    yield cov.all()
    yield cov.src()
    yield cov.by_module()



############################ website


DOC_ROOT = 'doc/'
DOC_BUILD_PATH = DOC_ROOT + '_build/html/'

def task_epydoc():
    """# generate API docs"""
    target_path = DOC_BUILD_PATH + 'api/'
    return {'actions':[(create_folder, [target_path]),
                       ("epydoc --config %sepydoc.config " % DOC_ROOT +
                        "-o %(targets)s")],
            'file_dep': CODE_FILES,
            'targets': [target_path]}


def task_docs():
    doc_files = glob.glob('doc/*.rst') + ['README.rst', 'CONTRIBUTING.md']
    yield docs.spell(doc_files, 'doc/dictionary.txt')
    sphinx_opts = "-A include_analytics=1 -A include_gittip=1"
    yield docs.sphinx(DOC_ROOT, DOC_BUILD_PATH, sphinx_opts=sphinx_opts,
                      task_dep=['spell'])


def task_website():
    """dodo file create website html files"""
    return {'actions': None,
            'task_dep': ['epydoc', 'sphinx'],
            }

def task_website_update():
    """update website on SITE_PATH
    website is hosted on github-pages
    this task just copy the generated content to SITE_PATH,
    need to commit/push to deploy site.
    """
    SITE_PATH = '../doit-website'
    SITE_URL = 'pydoit.org'
    return {
        'actions': [
            "rsync -avP %s %s" % (DOC_BUILD_PATH, SITE_PATH),
            "echo %s > %s" % (SITE_URL, os.path.join(SITE_PATH, 'CNAME')),
            "touch %s" % os.path.join(SITE_PATH, '.nojekyll'),
            ],
        'task_dep': ['website'],
        }



def task_package():
    """create/upload package to pypi"""
    pkg = Package()
    yield pkg.revision_git()
    yield pkg.manifest_git()
    yield pkg.sdist()
    yield pkg.sdist_upload()



# doit -f ../doit-recipes/deps/deps.py -d . --reporter=executed-only
