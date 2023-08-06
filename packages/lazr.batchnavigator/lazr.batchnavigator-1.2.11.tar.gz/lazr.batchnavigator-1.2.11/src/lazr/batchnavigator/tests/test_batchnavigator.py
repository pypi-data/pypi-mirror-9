# Copyright 2011 Canonical Ltd.  All rights reserved.
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

"""Unit tests for lazr.batchnavigator.BatchNavigator."""

import testtools
from testtools.matchers import Equals
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from lazr.batchnavigator import BatchNavigator, ListRangeFactory
from lazr.batchnavigator.interfaces import (
    IRangeFactory,
    InvalidBatchSizeError,
    )
from lazr.batchnavigator.z3batching.batch import _Batch
from lazr.batchnavigator.tests.test_z3batching import RecordingFactory

SERVER_URL = 'http://www.example.com/foo'


def query_string(start=None, batch=None, memo=None, direction=None):
    query_string_args = {}
    params = locals()
    def maybe(arg):
        if params[arg] is not None:
            query_string_args[arg] = params[arg]
    maybe('batch')
    maybe('direction')
    maybe('start')
    maybe('memo')
    query_string = "&".join(["%s=%s" % item for item
        in sorted(query_string_args.items())])
    return query_string


def query_url(start=None, batch=None, memo=None, direction=None):
    return SERVER_URL + '?' + query_string(start=start, batch=batch,
        memo=memo,direction=direction)


def batchnav_request(start=None, batch=None, memo=None, direction=None):
    return TestRequest(SERVER_URL=SERVER_URL,
        method='GET', environ={'QUERY_STRING': query_string(start=start,
        batch=batch, memo=memo,direction=direction)})


def sample_batchnav(start=None, batch=None, memo=None, direction=None):
    collection = range(1, 11)
    request = batchnav_request(start=start, batch=batch, memo=memo,
        direction=direction)
    range_factory = RecordingFactory(collection)
    return BatchNavigator(collection, request, range_factory=range_factory)


class PickyListLikeCollection:
    """Collection that really hates slices with negative start values.

    Some database-backed collections, e.g. Postgres via Storm, throw
    exceptions if a slice is used that starts with a negative value.  When
    batch navigator is going backwards it is easy to pass such a slice.  This
    collection is used to ensure it is noticed if that happens.
    """
    def __init__(self, collection):
        self._collection = collection
    def __iter__(self):
        return iter(self._collection)
    def __getitem__(self, index):
        if (isinstance(index, slice) and
            index.start is not None and index.start < 0):
            raise RuntimeError
        return self._collection.__getitem__(index)
    def __len__(self):
        return self._collection.__len__()


def empty_batchnav(start=None, batch=None, memo=None, direction=None):
    collection = PickyListLikeCollection([])
    request = batchnav_request(start=start, batch=batch, memo=memo,
        direction=direction)
    range_factory = RecordingFactory(collection)
    return BatchNavigator(collection, request, range_factory=range_factory)


class EqualsQuery(Equals):

    def __init__(self, start=None, batch=None, direction=None, memo=None):
        Equals.__init__(self, query_url(start=start, batch=batch,
            direction=direction, memo=memo))


class TestBatchFactory(testtools.TestCase):

    def test_accepts_range_factory(self):
        # A BatchNavigator can be instantiated with a RangeFactory.
        results = [1, 2, 3, 4]
        range_factory = ListRangeFactory(results)
        request = batchnav_request()
        batchnav = BatchNavigator(
            results, request, range_factory=range_factory)
        self.assertEqual(batchnav.batch.range_factory, range_factory)

    def test_without_memo_direction_gets_non_factory_batch(self):
        # memo and direction were added after the core was developed; for
        # compatability with bookmarks when they are missing the old behaviour
        # is invoked even when an explicit range factory is supplied
        batchnav = sample_batchnav(start=3, batch=3)
        self.assertEqual(range(4,7), list(batchnav.currentBatch()))
        self.assertEqual([], batchnav.batch.range_factory.calls)

    def test_without_memo_with_backwards_direction_gets_reverse_batch(self):
        # When direction is specified backwards without memo the batch seeks
        # backwards rather than doing a big list protocol slice.
        batchnav = sample_batchnav(start=3, batch=3, direction='backwards')
        self.assertEqual(range(10,11), list(batchnav.currentBatch()))
        self.assertEqual([('getSlice', 1, '', False)],
            batchnav.batch.range_factory.calls)

    def test_memo_used_for_middle_batch_forwards(self):
        # If we have a memo for a batch, it is used.
        batchnav = sample_batchnav(start=3, batch=3, memo='3')
        self.assertEqual(range(4,7), list(batchnav.currentBatch()))
        self.assertEqual([('getSlice', 4, '3', True)],
            batchnav.batch.range_factory.calls)

    def test_memo_used_for_middle_batch_backwards(self):
        # If we have a memo for a batch, it is used.
        batchnav = sample_batchnav(start=3, batch=3, memo='6',
            direction='backwards')
        self.assertEqual(range(4,7), list(batchnav.currentBatch()))
        self.assertEqual([('getSlice', 4, '6', False)],
            batchnav.batch.range_factory.calls)

    def test_lastBatchURL_sets_direction(self):
        batchnav = sample_batchnav(batch=3)
        self.assertThat(batchnav.lastBatchURL(),
            EqualsQuery(start=9, batch=3, direction='backwards'))

    def test_lastBatchURL_not_empty_for_bogus_start_value(self):
        # lastBatchURL() is correct even when the start parameter
        # is bogus: memo says that the batch begins at offset
        # 6, while start points to the last element of the
        # of the batch.
        batchnav = sample_batchnav(start=9, batch=3, memo="6")
        self.assertThat(batchnav.lastBatchURL(),
            EqualsQuery(start=9, batch=3, direction='backwards'))

    def test_firstBatchURL_is_trivial(self):
        batchnav = sample_batchnav(start=3, batch=3, memo='3')
        self.assertThat(batchnav.firstBatchURL(), EqualsQuery(batch=3))

    def test_firstBatchURL_does_not_depend_on_start_parameter(self):
        # nextBatchURL() is correct even when start has the (incorrect)
        # value 0. Start = 0 implies that we are at the first batch.
        # But this value may be wrong (see _Batch.__init__()), and
        # firstBatchURL() does not rely on it.
        batchnav = sample_batchnav(start=0, batch=3, memo='3')
        self.assertThat(batchnav.firstBatchURL(), EqualsQuery(batch=3))

    def test_nextBatchURL_has_memo(self):
        batchnav = sample_batchnav(start=3, batch=3, memo='3')
        self.assertThat(batchnav.nextBatchURL(),
            EqualsQuery(start=6, batch=3, memo='6'))

    def test_prevBatchURL_has_memo_direction(self):
        batchnav = sample_batchnav(start=6, batch=3, memo='6')
        self.assertThat(batchnav.prevBatchURL(),
            EqualsQuery(start=3, batch=3, memo='6', direction='backwards'))

    def test_variable_prefix_affects_all_params(self):
        # subclassing and setting variable_name_prefix causes all the variable
        # names to be adjusted.
        collection = range(1, 11)
        request = TestRequest(SERVER_URL=SERVER_URL,
            method='GET', environ={
            'QUERY_STRING': "prefix_start=6&prefix_batch=3&prefix_memo=6"})
        range_factory = RecordingFactory(collection)
        class PrefixBatchNavigator(BatchNavigator):
            variable_name_prefix = 'prefix'
        batchnav = PrefixBatchNavigator(collection, request,
                range_factory=range_factory)
        self.assertThat(batchnav.prevBatchURL(),
            Equals(SERVER_URL + '?prefix_batch=3&prefix_direction=backwards'
                '&prefix_memo=6&prefix_start=3'))

    def test_range_factory_producing_url_unsafe_memos(self):
        # Memo values containing characters with special meaning in URLs
        # are properly escaped by generateBatchURL().
        class WeirdRangeFactory(ListRangeFactory):
            def getEndpointMemos(self, batch):
                return ('start&/1', 'end&/2')

        collection = range(1, 11)
        request = TestRequest(
            SERVER_URL=SERVER_URL, method='GET',
            environ={'QUERY_STRING': "start=6&batch=3&memo=6"})
        range_factory = WeirdRangeFactory(collection)
        batchnav = BatchNavigator(
            collection, request, range_factory=range_factory)
        self.assertThat(
            batchnav.nextBatchURL(),
            Equals(SERVER_URL + '?batch=3&memo=end%26%2F2&start=9'))

    def test_empty_collection(self):
        batchnav = empty_batchnav(
            start=2, batch=2)
        self.assertEqual([], list(batchnav.currentBatch()))

    def test_empty_collection_backwards(self):
        batchnav = empty_batchnav(
            start=2, batch=2, direction='backwards')
        self.assertEqual([], list(batchnav.currentBatch()))


class TestListRangeFactory(testtools.TestCase):

    def test_valid_object(self):
        verifyObject(IRangeFactory, ListRangeFactory([]))

    def test_getEndpointMemos_empty(self):
        batch = _Batch([], ListRangeFactory([]))
        self.assertEqual(('0', '0'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_one_item(self):
        results = [0, 1, 2]
        batch = _Batch(results, ListRangeFactory(results), start=1, size=1)
        self.assertEqual(('1', '2'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_two_items(self):
        results = [0, 1, 2, 3]
        batch = _Batch(results, ListRangeFactory(results), start=1, size=2)
        self.assertEqual(('1', '3'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_three_items(self):
        results = [0, 1, 2, 3, 4]
        batch = _Batch(results, ListRangeFactory(results), start=1, size=3)
        self.assertEqual(('1', '4'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_start_border(self):
        results = [0, 1]
        batch = _Batch(results, ListRangeFactory(results), size=1)
        self.assertEqual(('0', '1'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_end_border(self):
        results = [0, 1]
        batch = _Batch(results, ListRangeFactory(results), start=1, size=1)
        self.assertEqual(('1', '2'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getEndpointMemos_last_batch_end_border(self):
        results = [0, 1, 2, 3]
        batch = _Batch(results, ListRangeFactory(results), start=4, size=1)
        self.assertEqual(('4', '4'),
            batch.range_factory.getEndpointMemos(batch))

    def test_getslice_bad_memo(self):
        self.assertRaises(InvalidBatchSizeError,
            ListRangeFactory([]).getSlice, 3, 'foo')

    def test_getslice_next_end(self):
        # at the end, crickets...
        results = [0, 1, 2, 3, 4, 5]
        _slice = ListRangeFactory(results).getSlice(3, '6')
        self.assertEqual([], _slice)

    def test_getslice_before_start(self):
        # at the end, crickets...
        results = [0, 1, 2, 3, 4, 5]
        _slice = list(ListRangeFactory(results).getSlice(3, '0', forwards=False))
        self.assertEqual([], _slice)

    def test_getslice_empty_slice(self):
        class fakeResults(object):
            def __getitem__(self, item):
                raise Exception('Thou shalt not slice.')
        results = fakeResults()
        ListRangeFactory(results).getSlice(3, '0', forwards=False) # No exception

    def test_getslice_before_end(self):
        results = [0, 1, 2, 3, 4, 5]
        _slice = list(ListRangeFactory(results).getSlice(3, '6', forwards=False))
        self.assertEqual([5, 4, 3], _slice)

    def test_getslice_next(self):
        # The slice returned starts where indicated but continues on.
        results = [0, 1, 2, 3, 4, 5]
        _slice = ListRangeFactory(results).getSlice(3, '3')
        self.assertEqual([3, 4, 5], _slice)

    def test_getslice_before_middle(self):
        # Going backwards does not include the anchor (because going forwards
        # includes it)
        results = [0, 1, 2, 3, 4, 5]
        _slice = list(ListRangeFactory(results).getSlice(3, '3', forwards=False))
        self.assertEqual([2, 1, 0], _slice)

    def test_getSliceByIndex(self):
        # getSliceByIndex returns the slice of the result limited by
        # the indices start, end.
        results = [0, 1, 2, 3, 4, 5]
        _slice = ListRangeFactory(results).getSliceByIndex(2, 5)
        self.assertEqual([2, 3, 4], _slice)

    def test_getSliceByIndex__no_result_set(self):
        # If no result set is present, getSliceByIndex() returns an
        # empty list.
        _slice = ListRangeFactory(None).getSliceByIndex(2, 5)
        self.assertEqual([], _slice)

    def test_picky_collection_ok(self):
        p = PickyListLikeCollection(range(5))
        self.assertEqual(range(5)[0:2], p[0:2])

    def test_picky_collection_bad(self):
        p = PickyListLikeCollection([])
        # It would be nice to demonstrate p[-10:2] but it cannot be done
        # directly since assertRaises needs individual parameters.  The
        # following is the equivalent.
        self.assertRaises(RuntimeError,
                          p.__getitem__, slice(-10, 2, None))

    def test_getSlice_empty_result_set_forwards(self):
        results = PickyListLikeCollection([])
        _slice = ListRangeFactory(results).getSlice(5, forwards=True)
        self.assertEqual([], _slice)

    def test_getSlice_empty_result_set_backwards(self):
        results = PickyListLikeCollection([])
        _slice = ListRangeFactory(results).getSlice(5, forwards=False)
        self.assertEqual([], _slice)

    def test_getSliceByIndex_empty_result_set(self):
        results = PickyListLikeCollection([])
        self.assertRaises(
            RuntimeError,
            ListRangeFactory(results).getSliceByIndex, -1, 1)

    def test_rough_length(self):
        # ListRangeFactory.rough_length returns the length of the
        # result set.
        factory = ListRangeFactory(range(4))
        self.assertEqual(4, factory.rough_length)
