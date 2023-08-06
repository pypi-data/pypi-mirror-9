#!/usr/bin/env python2
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import copy
import os
import subprocess
import sys

from subunit import run as subunit_run
from testtools import run as testtools_run


def parse_args():
    parser = argparse.ArgumentParser(
        description='Tool to run openstack tests')
    parser.add_argument('--blacklist_file', '-b',
                        help='Path to a blacklist file, this file contains a'
                             ' separate regex exclude on each newline')
    parser.add_argument('--regex', '-r',
                        help='A normal testr selection regex. If a blacklist '
                             'file is specified, the regex will be appended '
                             'to the end of the generated regex from that '
                             'file')
    parser.add_argument('--pretty', '-p', dest='pretty', action='store_true',
                        help='Print pretty output from subunit-trace. This is '
                             'mutually exclusive with --subunit')
    parser.add_argument('--no-pretty', dest='pretty', action='store_false',
                        help='Disable the pretty output with subunit-trace')
    parser.add_argument('--subunit', '-s', action='store_true',
                        help='output the raw subunit v2 from the test run '
                             'this is mutuall exclusive with --pretty')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all the tests which will be run.')
    parser.add_argument('--no-discover', '-n', metavar='TEST_ID',
                        help="Takes in a single test to bypasses test "
                             "discover and just excute the test specified")
    parser.add_argument('--slowest', dest='slowest', action='store_true',
                        help="after the test run print the slowest tests")
    parser.add_argument('--no-slowest', dest='slowest', action='store_false',
                        help="after the test run don't print the slowest "
                             "tests")
    parser.add_argument('--pdb', metavar='TEST_ID',
                        help='Run a single test that has pdb traces added')
    parser.add_argument('--parallel', dest='parallel', action='store_true',
                        help='Run tests in parallel (this is the default)')
    parser.add_argument('--serial', dest='parallel', action='store_false',
                        help='Run tests serially')
    parser.add_argument('--concurrency', '-c', type=int, metavar='WORKERS',
                        help='The number of workers to use when running in '
                             'parallel. By default this is the number of cpus')
    parser.add_argument('--until-failure', action='store_true',
                        help='Run the tests in a loop until a failure is '
                             'encountered. Running with subunit or pretty'
                             'output enable will force the loop to run tests'
                             'serially')
    parser.set_defaults(pretty=True, slowest=True, parallel=True)
    opts = parser.parse_args()
    return opts


def construct_regex(blacklist_file, regex):
    if not blacklist_file:
        exclude_regex = ''
    else:
        black_file = open(blacklist_file, 'r')
        exclude_regex = ''
        for line in black_file:
            regex = line.strip()
            exclude_regex = '|'.join([regex, exclude_regex])
        if exclude_regex:
            exclude_regex = "'(?!.*" + exclude_regex + ")"
    if regex:
        exclude_regex += regex
    return exclude_regex


def call_testr(regex, subunit, pretty, list_tests, slowest, parallel, concur,
               until_failure):
    if parallel:
        cmd = ['testr', 'run', '--parallel']
        if concur:
            cmd.append('--concurrency=%s' % concur)
    else:
        cmd = ['testr', 'run']
    if list_tests:
        cmd = ['testr', 'list-tests']
    elif (subunit or pretty) and not until_failure:
        cmd.append('--subunit')
    elif not (subunit or pretty) and until_failure:
        cmd.append('--until-failure')
    cmd.append(regex)
    env = copy.deepcopy(os.environ)
    # This workaround is necessary because of lp bug 1411804 it's super hacky
    # and makes tons of unfounded assumptions, but it works for the most part
    if (subunit or pretty) and until_failure:
        proc = subprocess.Popen(['testr', 'list-tests', regex], env=env,
                                stdout=subprocess.PIPE)
        out = proc.communicate()[0]
        raw_test_list = out.split('\n')
        bad = False
        test_list = []
        exclude_list = ['CAPTURE', 'TEST_TIMEOUT', 'PYTHON',
                        'subunit.run discover']
        for line in raw_test_list:
            for exclude in exclude_list:
                if exclude in line:
                    bad = True
                    break
                elif not line:
                    bad = True
                    break
            if not bad:
                test_list.append(line)
            bad = False
        count = 0
        failed = False
        if not test_list:
            print("No tests to run")
            exit(1)
        # If pretty or subunit output is desired manually loop forever over
        # test individually and generate the desired output in a linear series
        # this avoids 1411804 while retaining most of the desired behavior
        while True:
            for test in test_list:
                if pretty:
                    cmd = ['python', '-m', 'subunit.run', test]
                    ps = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
                    proc = subprocess.Popen(['subunit-trace',
                                             '--no-failure-debug', '-f',
                                             '--no-summary'], env=env,
                                            stdin=ps.stdout)
                    ps.stdout.close()
                    proc.communicate()
                    if proc.returncode > 0:
                        failed = True
                        break
                else:
                    try:
                        subunit_run.main([sys.argv[0], test], sys.stdout)
                    except SystemExit as e:
                        if e > 0:
                            print("Ran %s tests without failure" % count)
                            exit(1)
                        else:
                            raise
                count = count + 1
            if failed:
                print("Ran %s tests without failure" % count)
                exit(0)
    # If not until-failure special case call testr like normal
    elif pretty and not list_tests:
        ps = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
        proc = subprocess.Popen(['subunit-trace', '--no-failure-debug', '-f'],
                                env=env, stdin=ps.stdout)
        ps.stdout.close()
    else:
        proc = subprocess.Popen(cmd, env=env)
    proc.communicate()
    return_code = proc.returncode
    if slowest and not list_tests:
        print("\nSlowest Tests:\n")
        slow_proc = subprocess.Popen(['testr', 'slowest'], env=env)
        slow_proc.communicate()
    return return_code


def call_subunit_run(test_id, pretty, subunit):
    if pretty:
        env = copy.deepcopy(os.environ)
        cmd = ['python', '-m', 'subunit.run', test_id]
        ps = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
        proc = subprocess.Popen(['subunit-trace', '--no-failure-debug', '-f'],
                                env=env, stdin=ps.stdout)
        ps.stdout.close()
        proc.communicate()
        return proc.returncode
    elif subunit:
        subunit_run.main([sys.argv[0], test_id], sys.stdout)
    else:
        testtools_run.main([sys.argv[0], test_id], sys.stdout)


def call_testtools_run(test_id):
    testtools_run.main([sys.argv[0], test_id], sys.stdout)


def main():
    opts = parse_args()
    if opts.pretty and opts.subunit:
        msg = ('Subunit output and pretty output cannot be specified at the '
               'same time')
        print(msg)
        exit(2)
    if opts.list and opts.no_discover:
        msg = ('you can not list tests when you are bypassing discovery to '
               'run a single test')
        print(msg)
        exit(3)
    if not opts.parallel and opts.concurrency:
        msg = "You can't specify a concurrency to use when running serially"
        print(msg)
        exit(4)
    if (opts.pdb or opts.no_discover) and opts.until_failure:
        msg = "You can not use until_failure mode with pdb or no-discover"
        print(msg)
        exit(5)
    exclude_regex = construct_regex(opts.blacklist_file, opts.regex)
    if not os.path.isdir('.testrepository'):
        subprocess.call(['testr', 'init'])
    if not opts.no_discover and not opts.pdb:
        exit(call_testr(exclude_regex, opts.subunit, opts.pretty, opts.list,
                        opts.slowest, opts.parallel, opts.concurrency,
                        opts.until_failure))
    elif opts.pdb:
        exit(call_testtools_run(opts.pdb))
    else:
        exit(call_subunit_run(opts.no_discover, opts.pretty, opts.subunit))

if __name__ == '__main__':
    main()
