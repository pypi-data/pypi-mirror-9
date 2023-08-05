#!/usr/bin/python
import os
import sys
import traceback
from StringIO import StringIO

sys.path.insert(0, os.path.pardir)
import rrdmodel

test_dir = 'tmp'

def assertEqual(a, b):
    if a != b:
        raise AssertionError('{} != {}'.format(a,b))

def setup():
    test_file = os.path.join(test_dir, 'traffic.rrd')
    if os.path.exists(test_dir):
        if os.path.exists(test_file):
            os.unlink(test_file)
    else:
        os.mkdir(test_dir)

    global m, start_time, num_seconds
    m = rrdmodel.RRDModel(test_dir)
    start_time = 1e9
    num_seconds = 3*86400
    for t in range(0, num_seconds, 30):
        m.update((start_time + t)*1000, (t, 2*t))

def cleanup():
    if os.path.exists(test_file):
        os.unlink(test_file)
    os.rmdir(test_dir)

def test_fetch_1m():
    results = m.fetch(start_time, start_time + num_seconds, 1)
    assertEqual(len(results), 60)

def test_fetch_10m():
    results = m.fetch(start_time, start_time + num_seconds, 10)
    assertEqual(len(results), 144)

setup()

tests = (
    test_fetch_1m,
    test_fetch_10m,
)

error_msgs = StringIO()
num_tests = 0
num_fails = 0
num_errors = 0
for test_func in tests:
    try:
        test_func()
    except Exception as e:
        error_msgs.write('='*70 + '\n' + traceback.format_exc() + '\n')
        if isinstance(e, AssertionError):
            num_fails += 1
            sys.stderr.write('F')
        else:
            num_errors += 1
            sys.stderr.write('E')
    else:
        sys.stderr.write('.')
    num_tests += 1
    sys.stderr.flush()

#cleanup()

sys.stderr.write('\n')
sys.stderr.write(error_msgs.getvalue())
sys.stderr.write('-'*70 + '\n')

sys.stderr.write('Ran {} tests\n\n'.format(num_tests))
if num_errors > 0 or num_fails > 0:
    msgs = []
    if num_errors > 0:
        msgs.append('errors=' + str(num_errors))
    if num_fails > 0:
        msgs.append('fails=' + str(num_fails))
    sys.stderr.write('FAILED ({})\n'.format(' '.join(msgs)))
    sys.exit(1)
else:
    sys.stderr.write('OK\n')
    sys.exit(0)
