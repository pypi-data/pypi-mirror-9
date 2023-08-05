# BEGIN_COPYRIGHT
#
# Copyright 2009-2015 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# END_COPYRIGHT

import unittest
import os

from pydoop.mapreduce.string_utils import quote_string, unquote_string
from pydoop.mapreduce.string_utils import create_digest
from pydoop.utils.serialize import deserialize
from pydoop.mapreduce.binary_streams import BinaryDownStreamFilter

_CURRENT_DIR = os.path.dirname(__file__)
JOB_TOKEN = os.path.join(_CURRENT_DIR, 'data/jobToken')
MAP_JAVA_DOWNLINK_DATA = os.path.join(
    _CURRENT_DIR, 'data/mapper_downlink.data'
)


class TestUtils(unittest.TestCase):

    def test_quote(self):
        for x in ['dfskjfdjsalk', 'sdkfj\ta\t\n', 'dfssd\t\n', '\adsfsdfa\t\n',
                  'dsjfkjewrwerwerwe8239489238492\n \t dfasd \\',
                  'jdsfkj\\hsdjhfjh\\\t\n']:
            self.assertEqual(x, unquote_string(quote_string(x)))

    def test_digest(self):
        with open(JOB_TOKEN) as f:
            f.read(4)  # magic
            deserialize(int, f)  # prot
            deserialize(int, f)  # n
            deserialize(str, f)  # label
            deserialize(str, f)  # job
            passwd = deserialize(str, f)
        with open(MAP_JAVA_DOWNLINK_DATA) as istream:
            cmd_stream = BinaryDownStreamFilter(istream)
            cmd, args = cmd_stream.next()
        self.assertEqual(cmd, 'authenticationReq')
        xdigest = '5bMR7RdwmkLvK582eYWEK8X6jDA='
        xchallenge = '1593317824749889452062285518813742155'
        digest, challenge = args
        self.assertEqual(digest, xdigest)
        self.assertEqual(challenge, xchallenge)
        self.assertEqual(digest, create_digest(passwd, challenge))


def suite():
    suite_ = unittest.TestSuite()
    suite_.addTest(TestUtils('test_quote'))
    suite_.addTest(TestUtils('test_digest'))
    return suite_


if __name__ == '__main__':
    _RUNNER = unittest.TextTestRunner(verbosity=2)
    _RUNNER.run((suite()))
