import os

from fabric.api import env, local
from fabric.utils import warn, puts


def find_files(path, suffixes=None, exclude_dirs=None):
    if not os.path.exists(path):
        return []

    exclude_dirs = exclude_dirs or []
    found_files = []

    def include_file(filename, suffixes):
        return any([filename.endswith('.' + suffix) for suffix in suffixes])

    for root, dirs, files in os.walk(path):
        for exclude_dir in set(dirs) & set(exclude_dirs):
            dirs.remove(exclude_dir)
        found_files.extend([os.path.join(root, file) for file in files
                           if include_file(file, suffixes)])
    return found_files


def abs_path(relative_path, base_dir=env['cwd']):
    """
    Make relative paths absolute to the project directory.
    """
    return os.path.abspath(os.path.join(base_dir, relative_path))


def jslint_file(filename):
    JSLINT_CMD = (
        'node %s'
        ' --predef=jQuery,Modernizr,STATIC_URL,FileReader,plupload'
        ' --browser'
        ' --unparam'
        ' --regexp'
        ' --vars'
        ' --maxlen=120'
        ' --indent=4' % abs_path('tools/jslint-wrapper.js'))
    local('%s "%s"' % (JSLINT_CMD, filename))


def tag_matches_package_version(tag, application_version):

    if str(tag[1:]) != str(application_version):
        # using [1:] because of the tag form eg. v1.2.3
        warn("Package version (%s) does not match tag (%s)" % (application_version, tag))
        return False
    else:
        puts("Package version (%s) matches tag (%s)" % (application_version, tag))
        return True
