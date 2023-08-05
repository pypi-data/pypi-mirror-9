from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging

from lib2to3.main import warn, StdoutRefactoringTool
from lib2to3 import refactor

from .fixes import lib2to3_fix_names
from . import __version__


def main():
    """Main program."""
    parser = argparse.ArgumentParser(prog='python-modernize')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-d', '--doctests', action='store_true',
                        help='fix up doctests')
    parser.add_argument('-f', '--fix', action='append', default=[],
                        help='each FIX specifies a transformation; '
                             'default: all')
    parser.add_argument('-j', '--processes', action='store', default=1,
                        type=int, help='Run 2to3 concurrently')
    parser.add_argument('-x', '--nofix', action='append', default=[],
                        help='prevent a fixer from being run')
    parser.add_argument('-l', '--list-fixes', action='store_true',
                        help='list available transformations')
    parser.add_argument('-p', '--print-function', action='store_true',
                        help='modify the grammar so that print() is a '
                             'function')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='more verbose logging')
    parser.add_argument('--no-diffs', action='store_true',
                        help="don't show diffs of the refactoring")
    parser.add_argument('-w', '--write', action='store_true',
                        help='write back modified files')
    parser.add_argument('-n', '--nobackups',
                        action='store_true', default=False,
                        help="don't write backups for modified files.")
    parser.add_argument('--future-unicode',
                        action='store_true', default=False,
                        help='use unicode_strings __future__ feature '
                             '(only useful for Python 2.6+)')
    parser.add_argument('files', nargs='*',
                        help="files to fix or '-' for standard in")

    fixer_pkg = 'libmodernize.fixes'
    avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
    avail_fixes.update(lib2to3_fix_names)

    refactor_stdin = False
    flags = {}
    args = parser.parse_args()

    if args.processes < 1:
        import multiprocessing
        args.processes = multiprocessing.cpu_count()

    if not args.write and args.no_diffs:
        warn(
            "not writing files and not printing diffs; that's not very useful")

    if not args.write and args.nobackups:
        parser.error("Can't use -n without -w")

    if args.list_fixes:
        print('Available transformations for the -f/--fix option:')
        for fixname in sorted(avail_fixes):
            print(fixname)

    if not args.files:
        return 0

    if '-' in args.files:
        refactor_stdin = True
        if len(args.files) > 1:
            parser.error('Cannot mix stdin and regular files')
        if args.write:
            parser.error("Can't write to stdin")

    if args.print_function:
        flags['print_function'] = True

    if args.verbose == 0:
        level = logging.ERROR
    elif args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(format='%(name)s: %(message)s', level=level)

    unwanted_fixes = set(args.nofix)

    if not args.future_unicode:
        unwanted_fixes.add('libmodernize.fixes.fix_unicode_future')

    if args.doctests:
        unwanted_fixes.add('libmodernize.fixes.fix_print')
        unwanted_fixes.add('libmodernize.fixes.fix_absolute_import_future')
    else:
        # Use fix_absolute_import_future instead.
        unwanted_fixes.add('lib2to3.fixes.fix_import')

    explicit = set()
    if args.fix:
        all_present = False
        for fix in args.fix:
            if fix == 'all':
                all_present = True
            else:
                explicit.add(fix)
        requested = avail_fixes.union(explicit) if all_present else explicit
    else:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    rt = StdoutRefactoringTool(sorted(fixer_names), flags, sorted(explicit),
                               args.nobackups, not args.no_diffs)

    if not rt.errors:
        if refactor_stdin:
            rt.refactor_stdin()
        else:
            try:
                rt.refactor(args.files, args.write, args.doctests,
                            args.processes)
            except refactor.MultiprocessingUnsupported:
                assert args.processes > 1
                parser.error("Sorry, -j isn't supported on this platform")
        rt.summarize()

    return int(bool(rt.errors))
