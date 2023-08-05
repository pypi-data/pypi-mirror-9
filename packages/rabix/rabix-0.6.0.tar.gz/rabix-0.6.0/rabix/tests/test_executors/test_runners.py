import logging
import six

from nose.tools import nottest, assert_equal

from os.path import abspath, join
from rabix.common.ref_resolver import from_url
from rabix.main import init_context, fix_types

logging.basicConfig(level=logging.DEBUG)


@nottest
def assert_execution(job, outputs):
    result = job.run()
    assert_equal(result, outputs)


def test_workflow():
    path = abspath(join(__file__, '../../test_runtime/wf_tests.yaml'))

    context = init_context()
    doc = from_url(path)
    tests = doc['tests']
    for test_name, test in six.iteritems(tests):
        features = test.get('requiresFeatures', [])
        if 'map' not in features:
            fix_types(test['job']['app'])
            yield assert_execution, context.from_dict(test['job']), test['outputs']
