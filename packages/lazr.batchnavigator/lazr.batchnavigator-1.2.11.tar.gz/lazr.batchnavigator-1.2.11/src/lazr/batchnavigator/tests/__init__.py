# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.batchnavigator
#
# lazr.batchnavigator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.batchnavigator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.batchnavigator. If not, see <http://www.gnu.org/licenses/>.
"The lazr.batchnavigator tests."

import unittest

from lazr.batchnavigator.tests import (
    test_docs,
    )

def test_suite():
    # Discovery would be nice, but needs python2.7 for use with subunit &
    # testrepository.
    result = unittest.TestSuite()
    result.addTests(test_docs.additional_tests())
    modules = ['batchnavigator', 'z3batching']
    result.addTests(unittest.TestLoader().loadTestsFromNames([
        'lazr.batchnavigator.tests.test_' + name for name in modules]))
    return result
