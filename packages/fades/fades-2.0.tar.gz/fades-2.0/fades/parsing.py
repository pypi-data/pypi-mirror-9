# Copyright 2014, 2015 Facundo Batista, Nicolás Demarchi
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://github.com/PyAr/fades

"""Script parsing to get needed dependencies."""

import logging

from pkg_resources import parse_requirements

from fades import REPO_PYPI

logger = logging.getLogger(__name__)


def _parse_content(fh):
    """Parse the content of a script to find marked dependencies."""
    content = iter(fh)
    deps = {}

    for line in content:
        # quickly discard most of the lines
        if 'fades' not in line:
            continue

        # discard other string with 'fades' that isn't a comment
        if '#' not in line:
            continue

        # assure that it's a well commented line and no other stuff
        line = line.strip()
        import_part, fades_part = line.rsplit("#", 1)

        # discard other comments in the same line that aren't for fades
        if "fades" not in fades_part:
            import_part, fades_part = import_part.rsplit("#", 1)

        fades_part = fades_part.strip()
        if not fades_part.startswith("fades."):
            continue

        if not import_part:
            # the fades comment was done at the beginning of the line,
            # which means that the import info is in the next one
            import_part = next(content).strip()

        # get module
        import_tokens = import_part.split()
        if import_tokens[0] == 'import':
            module_path = import_tokens[1]
        elif import_tokens[0] == 'from' and import_tokens[2] == 'import':
            module_path = import_tokens[1]
        else:
            logger.warning("Not understood import info: %s", import_tokens)
            continue
        module = module_path.split(".")[0]
        # To match the "safe" name that pkg_resources creates:
        module = module.replace('_', '-')

        # get the fades info
        if fades_part.startswith("fades.pypi"):
            repo = REPO_PYPI
            marked = fades_part[10:].strip()  # Only works with fades.pypi
            if not marked:
                # nothing after the pypi token
                requirement = module
            elif marked[0] in "<>=!":
                # the rest is just the version
                requirement = module + ' ' + marked
            else:
                # the rest involves not only a version, but also the project name
                requirement = marked
        else:
            logger.warning("Not understood fades info: %r", fades_part)
            continue

        # record the dependency
        dependency = list(parse_requirements(requirement))[0]
        deps.setdefault(repo, []).append(dependency)

    return deps


def parse_file(filepath):
    """Parse a file and return its marked dependencies."""
    with open(filepath, 'rt', encoding='utf8') as fh:
        return _parse_content(fh)
