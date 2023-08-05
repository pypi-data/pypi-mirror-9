# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json

from pkg_resources import resource_filename


__version__ = '0.0.1-2'


def main():
    """
    Main entry point.
    """
    import jsonschema
    parser = argparse.ArgumentParser(version=__version__)
    parser.add_argument(
        '--verbose', action='store_true', default=False,
        help='Turn on verbose output.')
    parser.add_argument(
        '--header', action='store_true', default=False,
        help='Turn on header.')
    parser.add_argument(
        'playbooks', metavar='PLAYBOOKS', type=str, nargs='+',
        help='The playbook(s) to lint.')

    args = parser.parse_args()

    validation_results = {}
    all_valid = True
    # Load the playbook schema
    with open(resource_filename(
            'relent', 'schemas/playbook_schema.json'), 'r') as schema_fp:
        schema = json.load(schema_fp)
        # Do checks against playbooks
        for playbook in args.playbooks:
            try:
                with open(playbook, 'r') as pb:
                    # Schema check
                    jsonschema.validate(json.load(pb), schema)
            except jsonschema.ValidationError, e:
                all_valid = False
                validation_results[playbook] = (
                    False, e.message, list(e.schema_path), str(e))
            except ValueError, e:
                all_valid = False
                validation_results[playbook] = (
                    False, 'JSON is invalid.', str(e), str(e))

    # If all_valid is True then return back happy results
    if all_valid is True:
        if args.verbose or args.header:
            parser._print_message('Found 0 issues.\n')
        raise SystemExit(0)
    else:
        if args.verbose or args.header:
            parser._print_message('Found %s issues.\n\n' % len(
                validation_results))
        for problem_playbook in validation_results.keys():
            parser._print_message('%s: E: %s %s\n' % (
                problem_playbook,
                validation_results[problem_playbook][1],
                validation_results[problem_playbook][2]))
            if args.verbose:
                parser._print_message(
                    validation_results[problem_playbook][3] + '\n--\n')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
