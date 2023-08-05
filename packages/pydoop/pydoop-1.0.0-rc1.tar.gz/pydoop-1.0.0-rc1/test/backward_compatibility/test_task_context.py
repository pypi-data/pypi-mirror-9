# BEGIN_COPYRIGHT
# 
# Copyright 2009-2015 CRS4.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# 
# END_COPYRIGHT

import unittest
import pydoop
from pydoop.pipes import InputSplit


example_input_splits = [
    # ('\x002hdfs://localhost:8020/user/kikkomep/WordCountInput\x00\x00\x00\x00\x00\x01G4\x00\x00\x00\x00\x00\x01G5',
    # "hdfs://localhost:8020/user/kikkomep/WordCountInput",
    # 1,2
    # )
    ('/hdfs://localhost:9000/user/zag/in-dir/FGCS-1.ps\x00\x00\x00\x00\x00\x08h(\x00\x00\x00\x00\x00\x08h\x05',
    'hdfs://localhost:9000/user/zag/in-dir/FGCS-1.ps',
    550952, 550917),
    ('/hdfs://localhost:9000/user/zag/in-dir/FGCS-1.ps\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08h(',
    'hdfs://localhost:9000/user/zag/in-dir/FGCS-1.ps',
    0, 550952),
    ('1hdfs://localhost:9000/user/zag/in-dir/images_list\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$',
    'hdfs://localhost:9000/user/zag/in-dir/images_list',
    0, 36)
]
if not pydoop.hadoop_version_info().has_variable_isplit_encoding():
    example_input_splits = [("\x00" + raw_split, fn, o, l)
                            for (raw_split, fn, o, l) in example_input_splits]


class taskcontext_tc(unittest.TestCase):
    def test_input_split(self):
        for s in example_input_splits:
            i = InputSplit(s[0])
            self.assertEqual(i.filename, s[1])
            self.assertEqual(i.offset, s[2])
            self.assertEqual(i.length, s[3])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(taskcontext_tc('test_input_split'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run((suite()))
