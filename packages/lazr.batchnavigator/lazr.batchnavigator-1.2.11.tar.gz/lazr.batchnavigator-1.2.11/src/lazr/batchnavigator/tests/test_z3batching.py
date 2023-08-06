##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Batch tests.
"""
import operator
import unittest

from zope.interface.verify import verifyObject, verifyClass

from lazr.batchnavigator.z3batching.batch import (
    _Batch,
    BATCH_SIZE,
    _PartialBatch,
    )
from lazr.batchnavigator.z3batching.interfaces import IBatch
from lazr.batchnavigator import ListRangeFactory


class ListWithExplosiveLen(list):
    """A list subclass that doesn't like its len() being called."""
    def __len__(self):
        raise RuntimeError


class ListAllergicToNegativeIndexes(list):
    """A list subclass that doesn't like negative indexes."""
    def __getitem__(self, index):
        if index < 0:
            raise RuntimeError('Negative indexes are not allowed.')


class ListWithIncorrectLength(list):
    """A list subclass returning a too small length value.

    The goal of configurable range factories is to avoid SQL queries
    involving very expensive counting of result rows.

    One way to avoid a SELECT COUNT(*) FROM ... is to use the number
    of results reported by EXPLAIN SELECT ... FROM ...

    These results are not necessarily precise, hence class _Batch
    must not rely on the length reported by a sequence. This class
    can be used in tests to ensure that result sets with bad length
    information are processed properly.
    """
    def __init__(self, length, data=[]):
        super(ListWithIncorrectLength, self).__init__(data)
        self._length = length

    def __len__(self):
        return self._length

    def __getslice__(self, start, end):
        return super(ListWithIncorrectLength, self).__getslice__(start, end)


class RangeFactoryWithValueBasedEndpointMemos:
    """A RangeFactory which uses data values from a batch as endpoint memos.
    """
    def __init__(self, results):
        self.results = results

    def getEndpointMemos(self, batch):
        """See `IRangeFactory`."""
        return batch[0], batch[-1]

    getEndpointMemosFromSlice = getEndpointMemos

    def getSlice(self, size, endpoint_memo='', forwards=True):
        """See `IRangeFactory`."""
        if size == 0:
            return []
        if endpoint_memo == '':
            if forwards:
                return self.results[:size]
            else:
                sliced = self.results[-size:]
                sliced.reverse()
                return sliced

        if forwards:
            index = 0
            while (index < len(self.results) and
                   endpoint_memo >= self.results[index]):
                index += 1
            return self.results[index:index+size]
        else:
            index = len(self.results) - 1
            while (index >= 0 and endpoint_memo < self.results[index]):
                index -= 1
            if index < 0:
                return []
            start_index = max(0, index - size)
            sliced = self.results[start_index:index]
            sliced.reverse()
            return sliced

    def getSliceByIndex(self, start, end):
        """See `IRangeFactory`."""
        return self.results[start:end]

    @property
    def rough_length(self):
        """See `IRangeFactory`."""
        return len(self.results)


class RangeFactoryRecordingResultLengthCalls:
    """A RangeFactory surrogate which records each access to rough_length."""

    def __init__(self):
        self.rough_length_accesses = 0

    @property
    def rough_length(self):
        self.rough_length_accesses += 1
        return 42


class TestingInfrastructureTest(unittest.TestCase):
    def test_ListWithExplosiveLen(self):
        # For some of the tests we want to be sure len() of the underlying
        # collection is never called, so we've created a subclass of list that
        # raises an exception if asked for its length.
        self.assertRaises(RuntimeError, len, ListWithExplosiveLen([1,2,3]))

    def test_ListAllergicToNegativeIndexes(self):
        # Some of the tests want to show that the underlying collection is
        # never accessed with a negative index, so we have a subclass of list
        # that raises an exception if accessed in that way.
        self.assertRaises(
            RuntimeError,
            operator.getitem, ListAllergicToNegativeIndexes([1,2,3]), -1)

    def test_ListWithIncorrectLength(self):
        # Calling len(ListWithIncorrectLength) returns a bogus value.
        self.assertEqual(0, len(ListWithIncorrectLength(0, [1,])))
        self.assertEqual(2, len(ListWithIncorrectLength(2, [1,])))
        # Slicing works for positive indexes, even if len() returns a too
        # small value.
        weird_list = ListWithIncorrectLength(2, [0, 1, 2, 3])
        self.assertEqual([2, 3], weird_list[2:4])
        # But it returns odd data with negative indexes. (This does not
        # matter much because even ListRangeFactory does not use
        # negative indexes.)
        self.assertEqual([0], weird_list[-3:-1])
        # Slicing with positive indexes works for a too large len() value.
        weird_list = ListWithIncorrectLength(6, [0, 1, 2, 3])
        self.assertEqual([2, 3], weird_list[2:4])
        # Slicing with negative indexes returns wrong results,
        self.assertEqual([], weird_list[-2:-1])
        self.assertEqual([3], weird_list[-3:-2])

    def test_RangeFactoryWithValueBased_getEndpointMemos(self):
        data = [str(value) for value in range(10)]
        self.assertEqual(
            ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], data)
        factory = RangeFactoryWithValueBasedEndpointMemos(data)
        # The endpoint memo values are the values of the first and last
        # elelemnt of a batch.
        batch = data[:3]
        self.assertEqual(('0', '2'), factory.getEndpointMemos(batch))
        batch = data[4:8]
        self.assertEqual(('4', '7'), factory.getEndpointMemos(batch))
        # getSlice() called with an empty memo value returns the
        # first elements if forwards is True...
        self.assertEqual(
            ['0', '1', '2'],
            factory.getSlice(size=3, endpoint_memo='', forwards=True))
        # ...and the last elements if forwards is False.
        self.assertEqual(
            ['9', '8', '7'],
            factory.getSlice(size=3, endpoint_memo='', forwards=False))
        # A forwards slice starts with a value larger than the
        # given memo value.
        self.assertEqual(
            ['6', '7'],
            factory.getSlice(size=2, endpoint_memo='5', forwards=True))
        # A backwards slice starts with a value smaller than the
        # given memo value.
        self.assertEqual(
            ['4', '3'],
            factory.getSlice(size=2, endpoint_memo='5', forwards=False))
        # A slice is smaller than requested if the end of the results
        # is reached.
        self.assertEqual(
            ['8', '9'],
            factory.getSlice(size=3, endpoint_memo='7', forwards=True))
        self.assertEqual(
            [], factory.getSlice(size=3, endpoint_memo='A', forwards=True))
        self.assertEqual(
            [], factory.getSlice(size=3, endpoint_memo=' ', forwards=False))


class RecordingFactory(ListRangeFactory):
    def __init__(self, results):
        ListRangeFactory.__init__(self, results)
        self.calls = []

    def getEndpointMemos(self, batch):
        self.calls.append('getEndpointMemos')
        return ListRangeFactory.getEndpointMemos(self, batch)

    def getSlice(self, size, memo, forwards):
        self.calls.append(('getSlice', size, memo, forwards))
        return ListRangeFactory.getSlice(self, size, memo, forwards)


class BatchTest(unittest.TestCase):

    def getData(self):
        return ['one', 'two', 'three', 'four', 'five', 'six',
                'seven', 'eight', 'nine', 'ten']

    def test_Interface(self):
        self.failUnless(IBatch.providedBy(self.getBatch()))

    def getBatch(self, start=0, size=None, range_forwards=None,
                 range_memo=None):
        return _Batch(self.getData(), ListRangeFactory(self.getData()), start,
            size, range_forwards, range_memo)

    def getRecordingBatch(self, start=0, size=None, memo=None, forwards=True):
        range_factory = RecordingFactory(self.getData())
        batch = _Batch(range_factory.results, range_factory, start=start,
            size=size, range_forwards=forwards, range_memo=memo)
        return batch

    def test_constructor(self):
        self.getBatch(9, 3)
        # A start that's larger than the length should still construct a
        # working (but empty) batch.
        self.getBatch(99, 3)
        # If no size is provided a default is used.
        _Batch(self.getData(), ListRangeFactory(self.getData()))

    def test_default_batch_size(self):
        # If we don't specify a batch size, a default one is chosen for us.
        batch = _Batch(self.getData(), ListRangeFactory(self.getData()))
        self.assertEqual(batch.size, BATCH_SIZE)

    def test__len__(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(len(batch), 3)

        batch = self.getBatch(9, 3)
        self.assertEqual(len(batch), 1)

        batch = self.getBatch(99, 3)
        self.assertEqual(len(batch), 0)

        # If the entire set of contents fits into a single batch, the result
        # of len() is correct.
        batch = self.getBatch(size=999)
        self.assertEqual(len(batch), 10)

        # If the entire set of contents fits into a single batch, and we've
        # iterated over the items, the result of len() is correct.
        batch = self.getBatch(size=999)
        list(batch)
        self.assertEqual(len(batch), 10)

    def test__getitem__(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(batch[0], 'one')
        self.assertEqual(batch[1], 'two')
        self.assertEqual(batch[2], 'three')
        batch = self.getBatch(3, 3)
        self.assertEqual(batch[0], 'four')
        self.assertEqual(batch[1], 'five')
        self.assertEqual(batch[2], 'six')
        batch = self.getBatch(9, 3)
        self.assertRaises(IndexError, batch.__getitem__, 3)

        # If the batch is "off the end" and we've materialized the underlying
        # list (by iterating over the batch) we will get an IndexError if we
        # pass in a negative item index.
        batch = self.getBatch(99, 3)
        list(iter(batch))
        self.assertRaises(IndexError, batch.__getitem__, -1)

    def test__iter__(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(list(iter(batch)), ['one', 'two', 'three'])
        batch = self.getBatch(9, 3)
        self.assertEqual(list(iter(batch)), ['ten'])
        batch = self.getBatch(99, 3)
        self.assertEqual(list(iter(batch)), [])

    def test__getitem__does_not_use_negative_indices(self):
        # Some collections don't implement __len__, so slicing them doesn't
        # work, therefore we want to be sure negative slices are not passed
        # through to the underlying collection.
        data = ListAllergicToNegativeIndexes(self.getData())
        batch = _Batch(data, ListRangeFactory(data), 99, 3)
        list(iter(batch))
        self.assertRaises(IndexError, batch.__getitem__, -1)

    def test__contains__(self):
        batch = self.getBatch(0, 3)
        self.assert_(batch.__contains__('one'))
        self.assert_(batch.__contains__('two'))
        self.assert_(batch.__contains__('three'))
        self.assert_(not batch.__contains__('four'))
        batch = self.getBatch(6, 3)
        self.assert_(not batch.__contains__('one'))
        self.assert_(batch.__contains__('seven'))
        self.assert_(not batch.__contains__('ten'))

    def test_last_batch_len_optimization(self):
        # If the current batch is known to be the last batch, then we can
        # calculate the total number of items without calling len() on the
        # underlying collection.
        data = ListWithExplosiveLen(self.getData())
        batch = _Batch(data, ListRangeFactory(data), 0, 20)

        # If we get the total number of items before accessing the underlying
        # data, we'll call len() on the collection object.
        self.assertRaises(RuntimeError, lambda: batch.listlength)

        # If instead we do something that materialized the slice of the
        # underlying collection that this batch represents...
        next(iter(batch))
        # ... then no exception is raised and we get the number of items.
        self.assertEqual(batch.listlength, 10)

    def test_firstBatch(self):
        """Check that the link to the first batch works.

        This first batch will be always pointing to the first available batch
        and, its main difference with the 'prev' and 'next' batches is, that
        will not be None ever.
        """
        # first batch when we are at the beginning of the batch.
        first = self.getBatch(0, 3).firstBatch()
        self.assertEqual(list(iter(first)), ['one', 'two', 'three'])
        # first batch when we are in the second set of items of the batch.
        first = self.getBatch(3, 3).firstBatch()
        self.assertEqual(list(iter(first)), ['one', 'two', 'three'])
        # first batch when we are in the third set of items of the batch.
        first = self.getBatch(6, 3).firstBatch()
        self.assertEqual(list(iter(first)), ['one', 'two', 'three'])
        # first batch when we are at the end of the batch.
        first = self.getBatch(9, 3).firstBatch()
        self.assertEqual(list(iter(first)), ['one', 'two', 'three'])
        # first batch when we get a request for an out of range item.
        first = self.getBatch(99, 3).firstBatch()
        self.assertEqual(list(iter(first)), ['one', 'two', 'three'])

    def test_nextBatch(self):
        next = self.getBatch(0, 3).nextBatch()
        self.assertEqual(list(iter(next)), ['four', 'five', 'six'])
        nextnext = next.nextBatch()
        self.assertEqual(list(iter(nextnext)), ['seven', 'eight', 'nine'])
        next = self.getBatch(9, 3).nextBatch()
        self.assertEqual(next, None)
        next = self.getBatch(99, 3).nextBatch()
        self.assertEqual(next, None)

    def test_nextBatch__backwards_batching(self):
        # The "first backwards" batch has no next batch.
        batch = self.getBatch(9, 3, range_forwards=False, range_memo='')
        self.assertTrue(batch.nextBatch() is None)
        # previous batches of this batch have a batch.
        batch = batch.prevBatch()
        self.assertFalse(batch.nextBatch() is None)

    def test_prevBatch(self):
        prev = self.getBatch(9, 3).prevBatch()
        self.assertEqual(list(iter(prev)), ['seven', 'eight', 'nine'])
        prevprev = prev.prevBatch()
        self.assertEqual(list(iter(prevprev)), ['four', 'five', 'six'])
        prev = self.getBatch(0, 3).prevBatch()
        self.assertEqual(prev, None)
        prev = self.getBatch(2, 3).prevBatch()
        self.assertEqual(list(iter(prev)), ['one', 'two', 'three'])

        # If we create a batch that's out of range, and don't get its
        # length or any of its data, its previous batch will also be
        # out of range.
        out_of_range = self.getBatch(99, 3)
        out_of_range_2 = out_of_range.prevBatch()
        self.assertEqual(out_of_range_2.start, 96)

    def test_lastBatch(self):
        """Check that the link to the last batch works.

        This last batch will be always pointing to the last available batch
        and, its main difference with the 'prev' and 'next' batches is, that
        will not be None ever.
        """
        # last batch when we are at the beginning of the batch.
        last = self.getBatch(0, 3).lastBatch()
        self.assertEqual(list(iter(last)), ['ten'])
        # last batch when we are in the second set of items of the batch.
        last = self.getBatch(3, 3).lastBatch()
        self.assertEqual(list(iter(last)), ['ten'])
        # last batch when we are in the third set of items of the batch.
        last = self.getBatch(6, 3).lastBatch()
        self.assertEqual(list(iter(last)), ['ten'])
        # last batch when we are at the end of the batch.
        last = self.getBatch(9, 3).lastBatch()
        self.assertEqual(list(iter(last)), ['ten'])
        # last batch when we get a request for an out of range item.
        last = self.getBatch(99, 3).lastBatch()
        self.assertEqual(list(iter(last)), ['ten'])

        # We are going to test now the same, but when we get a request of 5
        # items per batch because we had a bug in the way we calculate the
        # last batch set that was only happening when we were using a batch
        # size that is multiple of the item list length.

        # last batch when we are at the beginning of the batch.
        last = self.getBatch(0, 5).lastBatch()
        self.assertEqual(
            list(iter(last)), ['six', 'seven', 'eight', 'nine', 'ten'])
        # last batch when we are in the second set of items of the batch.
        last = self.getBatch(5, 5).lastBatch()
        self.assertEqual(
            list(iter(last)), ['six', 'seven', 'eight', 'nine', 'ten'])
        # last batch when we get a request for an out of range item.
        last = self.getBatch(99, 5).lastBatch()
        self.assertEqual(
            list(iter(last)), ['six', 'seven', 'eight', 'nine', 'ten'])

    def test_batchRoundTrip(self):
        batch = self.getBatch(0, 3).nextBatch()
        self.assertEqual(list(iter(batch.nextBatch().prevBatch())),
                         list(iter(batch)))

    def test_first_last(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(batch.first(), 'one')
        self.assertEqual(batch.last(), 'three')
        batch = self.getBatch(9, 3)
        self.assertEqual(batch.first(), 'ten')
        self.assertEqual(batch.last(), 'ten')
        batch = self.getBatch(99, 3)
        self.assertRaises(IndexError, batch.first)
        self.assertRaises(IndexError, batch.last)

    def test_total(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(batch.total(), 10)
        batch = self.getBatch(6, 3)
        self.assertEqual(batch.total(), 10)
        batch = self.getBatch(99, 3)
        self.assertEqual(batch.total(), 10)

    def test_trueSize_of_full_batch(self):
        # The .trueSize property reports how many items are in the batch.
        batch = self.getBatch(0, 3)
        self.assertEqual(batch.trueSize, 3)

    def test_trueSize_of_last_batch(self):
        # If the current batch contains fewer than a full batch, .trueSize
        # reports how many items are in the batch.
        batch = self.getBatch(9, 3)
        self.assertEqual(batch.trueSize, 1)

    def test_optimized_trueSize_of_full_batch(self):
        # If the unerlying items in the batch have been materialized, there is
        # a code path that avoids calling len() on the underlying collection.
        data = ListWithExplosiveLen(self.getData())
        batch = _Batch(data, ListRangeFactory(data), 0, 3)
        next(iter(batch)) # Materialize the items.
        self.assertEqual(batch.trueSize, 3)

    def test_optimized_trueSize_of_last_batch(self):
        # If the current batch contains fewer than a full batch, .trueSize
        # reports how many items are in the batch.
        data = ListWithExplosiveLen(self.getData())
        batch = _Batch(data, ListRangeFactory(data), 9, 3)
        next(iter(batch)) # Materialize the items.
        self.assertEqual(batch.trueSize, 1)

    def test_startNumber(self):
        batch = self.getBatch(0, 3)
        self.assertEqual(batch.startNumber(), 1)
        batch = self.getBatch(9, 3)
        self.assertEqual(batch.startNumber(), 10)
        batch = self.getBatch(99, 3)
        self.assertEqual(batch.startNumber(), 100)

    def test_endNumber(self):
        # If a batch of size 3 starts at index 0, the human-friendly numbering
        # of the last item should be 3.
        batch = self.getBatch(0, 3)
        self.assertEqual(batch.endNumber(), 3)
        # If a batch of size 3 starts at index 9 and has just 1 item in it
        # (because there are 10 items total), the human-friendly numbering
        # of the last item should be 10.
        batch = self.getBatch(9, 3)
        self.assertEqual(batch.endNumber(), 10)
        # If the batch start exceeds the number number of items, then the
        # endNumber will be None to indicate that it makes no sense to ask.
        batch = self.getBatch(99, 3)
        self.assertEqual(batch.endNumber(), None)

    def test_sliced_list_uses_range_factory(self):
        batch = self.getRecordingBatch(memo='', forwards=False)
        list(batch)
        self.assertEqual([('getSlice', 10, '', False)], batch.range_factory.calls)

    def test_firstBatch_generates_memo_None(self):
        batch = self.getRecordingBatch(start=3, size=3, memo='3')
        first = batch.firstBatch()
        self.assertEqual('', first.range_memo)
        self.assertEqual(True, first.range_forwards)
        self.assertEqual(0, first.start)
        self.assertEqual(3, first.size)
        self.assertEqual(['one', 'two', 'three'], list(first))

    def test_lastBatch_generates_memo_None_backwards(self):
        batch = self.getRecordingBatch(start=3, size=3, memo='3')
        last = batch.lastBatch()
        self.assertEqual('', last.range_memo)
        self.assertEqual(False, last.range_forwards)
        # len() is known, and size() is known, so the last batch starts at
        # len-size
        self.assertEqual(9, last.start)
        self.assertEqual(3, last.size)
        self.assertEqual(['ten'], list(last))

    def test_nextBatch_generates_upper_memo(self):
        batch = self.getRecordingBatch(start=3, size=3, memo='3')
        next = batch.nextBatch()
        self.assertEqual('6', next.range_memo)
        self.assertEqual(True, next.range_forwards)
        self.assertEqual(6, next.start)
        self.assertEqual(3, next.size)
        self.assertEqual(['seven', 'eight', 'nine'], list(next))

    def test_prevBatch_generates_lower_memo_backwards(self):
        batch = self.getRecordingBatch(start=6, size=3, memo='3')
        prev = batch.prevBatch()
        self.assertEqual('6', prev.range_memo)
        self.assertEqual(False, prev.range_forwards)
        # len() is known, and size() is known, so the prev batch starts at
        # len-size
        self.assertEqual(3, prev.start)
        self.assertEqual(3, prev.size)
        self.assertEqual(['four', 'five', 'six'], list(prev))

    def test_backwards_memo_inside_first_batch(self):
        # If data is retrieved backwards from the memo point and if
        # there is less data available than requested, additional
        # data stored "after the endpoint" is returned.
        batch = self.getRecordingBatch(start=0, size=5, memo=3, forwards=False)
        self.assertEqual(['one', 'two', 'three', 'four', 'five'], list(batch))

    def test_trueSize__with_bad_list_length(self):
        # Even if the len(resultset) claims to have only 2 elements,
        # batches starting at offsets 1 and 2 have two elements.
        weird_list = ListWithIncorrectLength(2, [0, 1, 2, 3])
        batch = _Batch(
            weird_list, range_factory=ListRangeFactory(weird_list),
            size=2, start=1)
        self.assertEqual(2, batch.trueSize)
        self.assertEqual([1, 2, 3], batch.sliced_list)
        batch = _Batch(
            weird_list, range_factory=ListRangeFactory(weird_list),
            size=2, start=2)
        self.assertEqual(2, batch.trueSize)
        self.assertEqual([2, 3], batch.sliced_list)

    def test_nextBatch__too_small_results_length(self):
        # Batch.nextBatch() is not None even if len(results)
        # indicates that there should not be a next batch.
        weird_list = ListWithIncorrectLength(3, [0, 1, 2, 3, 4])
        batch = _Batch(
            weird_list, range_factory=ListRangeFactory(weird_list),
            size=3)
        self.assertTrue(batch.nextBatch() is not None)

    def test_nextBatch__bad_results_length(self):
        # Even if len(results) claims that there are only 6 results,
        # batch.nextBatch() is not None
        weird_list = ListWithIncorrectLength(6, [0, 1, 2, 3, 4, 5, 6])
        batch = _Batch(
            weird_list, range_factory=ListRangeFactory(weird_list),
            size=3, range_memo='3', start=3, range_forwards=True)
        self.assertEqual([3, 4, 5, 6], batch.sliced_list)
        self.assertEqual([6], batch.nextBatch().sliced_list)

    def test_prevBatch__outdated_start_params(self):
        # The start parameter of a backwards batch may reach zero
        # even when the real begin of a result set is not yet reached.
        data = [1, 2, 3, 4, 5, 6]
        range_factory = RangeFactoryWithValueBasedEndpointMemos(data)
        # We create the first backwards.
        batch = _Batch(
            data, range_factory=range_factory, size=3, range_memo='',
            start=3, range_forwards=False)
        self.assertEqual([4, 5, 6], batch.sliced_list)
        self.assertEqual(3, batch.start)
        # The previous batch is now the first batch.
        batch = batch.prevBatch()
        self.assertEqual(0, batch.start)
        self.assertEqual(4, batch.range_memo)
        self.assertEqual([1, 2, 3, 4], batch.sliced_list)
        self.assertTrue(batch.prevBatch() is None)
        # If we now insert another value at the start of the result set,
        # and when we reload this batch with the same range parameters,
        # we get the same data slice, but also a prevBtach()
        # that is not None.
        data = [0, 1, 2, 3, 4, 5, 6]
        range_factory = RangeFactoryWithValueBasedEndpointMemos(data)
        new_batch = _Batch(
            data, range_factory=range_factory, size=3,
            range_memo=batch.range_memo, start=batch.start,
            range_forwards=False)
        # the contents of the batch is still correct. (Note that the
        # value of the last does not matter, see _Batch.sliced_list().)
        self.assertEqual([1, 2, 3, 0], new_batch.sliced_list)
        # And we get a previous batch.
        self.assertEqual([0, 1, 2, 3], new_batch.prevBatch().sliced_list)
        # Note that both new_batch and its previous batch claim to start
        # at 0.
        self.assertEqual(0, new_batch.start)
        self.assertEqual(0, new_batch.prevBatch().start)

    def test_last_backwards_batch_with_value_based_range_factory(self):
        # Another slice is added in _Batch.sliced_list() when the
        # regular slice of a backwards batch does not return the
        # number of required elements. This works for range factories
        # which are based on the values too.
        data = [str(value) for value in range(10)]
        range_factory = RangeFactoryWithValueBasedEndpointMemos(data)
        batch = _Batch(
            data, range_factory=range_factory, size=3, range_memo='1',
            start=1, range_forwards=False)
        self.assertEqual(['0', '1', '2', '3'], batch.sliced_list)

    def test_PartialBatch(self):
        # PartialBatch implements the full IBatch interface.
        from zope.interface.common.mapping import IItemMapping
        self.assertTrue(verifyClass(IBatch, _PartialBatch))
        partial = _PartialBatch(sliced_list=range(3))
        self.assertTrue(verifyObject(IBatch, partial))
        # trueSize is the length of sliced_list
        self.assertEqual(3, partial.trueSize)
        # sliced_list is passed by the contrucotr parameter sliced_list
        self.assertEqual([0, 1, 2], partial.sliced_list)
        # __len__() returns the length of the sliced list
        self.assertEqual(3, len(partial))
        # __iter__() iterates over sliced_list
        self.assertEqual([0, 1, 2], [element for element in partial])
        # __contains__() works.
        self.assertTrue(1 in partial)
        self.assertFalse(3 in partial)
        # prevBatch(), nextBatch() exost but are not implemented.
        self.assertRaises(NotImplementedError, partial.prevBatch)
        self.assertRaises(NotImplementedError, partial.nextBatch)
        # first and last are implemented.
        self.assertEqual(0, partial.first())
        self.assertEqual(2, partial.last())
        # total() return the length of sliced_list
        self.assertEqual(3, partial.total())
        # startNumber, endNumber() are implemented
        self.assertEqual(1, partial.startNumber())
        self.assertEqual(4, partial.endNumber())

    def test_has_next_batch__forwards_with_memo_not_at_end(self):
        # If a batch is not the last batch for a result set,
        # has_next_batch is True. When the parameter range_memo
        # is given, the value of start does not matter.
        batch = self.getBatch(
            start=7, size=3, range_forwards=True, range_memo="6")
        self.assertTrue(batch.has_next_batch)

    def test_has_next_batch__forwards_with_memo_at_end(self):
        # If a batch is the last batch for a result set,
        # has_next_batch is False. When the parameter range_memo
        # is given, the value of start does not matter.
        batch = self.getBatch(
            start=6, size=3, range_forwards=True, range_memo="7")
        self.assertFalse(batch.has_next_batch)

    def test_has_next_batch__forwards_without_memo_not_at_end(self):
        # If a batch is the last batch for a result set,
        # has_next_batch is False. When the parameter range_memo
        # is not given, the value of start is used.
        batch = self.getBatch(start=6, size=3)
        self.assertTrue(batch.has_next_batch)

    def test_has_next_batch__forwards_without_memo_at_end(self):
        # If a batch is the last batch for a result set,
        # has_next_batch is False. When the parameter range_memo
        # is not given, the value of start is used.
        batch = self.getBatch(start=7, size=3)
        self.assertFalse(batch.has_next_batch)

    def test_has_previous_batch__backwards_with_memo_not_at_end(self):
        # If a batch is not the first batch for a result set,
        # has_previous_batch is True. The value of start does not
        # matter.
        batch = self.getBatch(
            start=0, size=3, range_forwards=False, range_memo="4")
        self.assertTrue(batch.has_previous_batch)

    def test_has_previous_batch__backwards_with_memo_at_end(self):
        # If a batch is not the first batch for a result set,
        # has_previous_batch is False.The value of start does not
        # matter.
        batch = self.getBatch(
            start=1, size=3, range_forwards=False, range_memo="3")
        self.assertFalse(batch.has_previous_batch)

    def test_batch_gets_listlength_from_factory(self):
        # Batches get the length of the result set from the
        # range factory.
        range_factory = RangeFactoryRecordingResultLengthCalls()
        batch = _Batch(range(3), range_factory)
        listlength = batch.listlength
        self.assertEqual(42, listlength)
        self.assertEqual(1, range_factory.rough_length_accesses)
