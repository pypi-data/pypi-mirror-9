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
# Some parts Copyright 2005 Canonical Ltd.
#
##############################################################################
"""
Zope-derived Batching Support

*Do not use this. It is now an internal implementation detail.*
The intent is to get rid of this in favor of moving to extending z3c.batching.
"""


from zope.interface import implements
from zope.interface.common.sequence import IFiniteSequence
from interfaces import IBatch

from zope.cachedescriptors.property import Lazy

# The base batch size, which can be overridden by users of _Batch such
# as BatchNavigator. In Launchpad, we override it via a config option.
BATCH_SIZE = 50

class _PartialBatch:
    """A helper batch implementation.

    _Batch.sliced_list() below needs to retrieve a second chunk of
    data when a call of range_factory.getSlice() for a backwards batch
    returns less elements than requested because the start of the result
    set is reached.

    In this case, another (forwards) batch must be retrieved. _Batch
    must not assume that the memo value used to retrieve the first, too
    small, result set can be used to retrieve the additional data. (The
    class RangeFactoryWithValueBasedEndpointMemos in
    tests/test_z3batching.py is an example where this assumption fails.)

    Instead, _Batch.sliced_list() must retrieve the endpoint memos for
    the partial data and use them to retrieve the missing part of the
    result set. Since
      - IRangeFactory.getEndpointMemos(batch) is free to use any
        property of IBatch,
      - a call like self.range_factory.getEndpointMemos(self) in
       _Batch.sliced_list() leads to infinite recursions if the
       range factory wants to access sliced_list,

    we use this helper class for the getEndpointMemos() call in
    _Batch.sliced_list().
    """
    implements(IBatch)

    def __init__(self, sliced_list):
        self.start = 0
        self.trueSize = len(sliced_list)
        self.sliced_list = sliced_list
        self.size = len(sliced_list)

    def __len__(self):
        """See `IBatch`."""
        return len(self.sliced_list)

    def __iter__(self):
        """See `IBatch`."""
        return iter(self.sliced_list)

    def __getitem__(self, index):
        """See `IBatch`."""
        return self.sliced_list[index]

    def __contains__(self, key):
        """See `IBatch`."""
        return 0 <= key < len(self.sliced_list)

    def nextBatch(self):
        """See `IBatch`."""
        raise NotImplementedError

    def prevBatch(self):
        """See `IBatch`."""
        raise NotImplementedError

    def first(self):
        """See `IBatch`."""
        return self.sliced_list[0]

    def last(self):
        """See `IBatch`."""
        return self.sliced_list[-1]

    def total(self):
        """See `IBatch`."""
        return len(self.sliced_list)

    def startNumber(self):
        """See `IBatch`."""
        return 1

    def endNumber(self):
        """See `IBatch`."""
        return len(self.sliced_list) + 1

    # The values do not matter at all. Just make verifyObject() happy.
    has_previous_batch = None
    has_next_batch = None


class _Batch(object):
    implements(IBatch)

    def _get_length(self, results):
        # If this batch's contents is smaller than the batch size, it is the
        # last batch and we can deduce the underlying data's size.
        if (self._sliced_list is not None
                and len(self._sliced_list) <= self.size):
            return self.start + len(self._sliced_list)
        return self.range_factory.rough_length

    @property
    def listlength(self):
        if self._listlength is None:
            self._listlength = self._get_length(self.list)
        return self._listlength

    @Lazy
    def trueSize(self):
        """Return the actual size of this batch."""
        length = len(self.sliced_list)
        if length >= self.size:
            # This batch is full (and there might be another batch
            # afterwards). Return .size
            return self.size
        else:
            # This batch is not full. Return its (user-visible)
            # length.
            return length

    def __init__(self, results, range_factory, start=0, size=None,
        range_forwards=None, range_memo=None, _listlength=None):
        """Create a _Batch.

        :param start: Cosmetic indicator of the start of the batch. Has *no*
            effect on returned data.
        :param range_factory: A factory used to construct efficient views of
            the results.
        :param range_forwards: True if the range memo is at or before the start
            of the batch.
        :param range_memo: An endpoint memo from the range factory describing
            how to get a slice from the factory which will have offset 0
            contain the first element of the batch (or the list, if not
            range_forwards). '' for the extreme edge of the range, None to
            have the start parameter take precedence and cause actual
            slicing of results.
        """
        if results is None:
            results = []
        self.list = results

        if _listlength is not None:
            self._listlength = _listlength
        else:
            self._listlength = None
        self._sliced_list = None

        if size is None:
            size = BATCH_SIZE
        self.size = size

        self.start = start
        self.end = start + size
        self.range_factory = range_factory
        self.range_memo = range_memo
        if range_forwards is None:
            range_forwards = True
        self.range_forwards = range_forwards
        self.is_first_batch = False

    def __len__(self):
        assert self.trueSize >= 0, ('The number of items in a batch should '
            'never be negative.')
        return self.trueSize

    def __getitem__(self, key):
        if key >= self.trueSize:
            raise IndexError, 'batch index out of range'
        # When self.start is negative (IOW, when we are batching over an
        # empty list) we need to raise IndexError here; otherwise, the
        # attempt to slice below will, on objects which don't implement
        # __len__, raise a mysterious exception directly from python.
        if self.start < 0:
            raise IndexError, 'batch is empty'
        # We delegate to self.sliced_list because:
        # - usually folk will be walking the batch and sliced_list optimises
        #   that.
        # - if they aren't, the overhead of duplicating one batch of results in
        #   memory is small
        return self.sliced_list[key]

    @Lazy
    def sliced_list(self):
        # We use Lazy here to avoid self.__iter__ giving us new objects every
        # time; in certain cases (such as when database access is necessary)
        # this can be expensive.
        #
        if self.range_memo is None:
            # Legacyy mode - use the slice protocol on results.
            sliced = self.range_factory.getSliceByIndex(self.start, self.end+1)
        else:
            # The range factory gives us a partition on results starting from
            # the previous actual result.
            if self.range_memo is '' and not self.range_forwards:
                # As a special case, when getting the last batch (range_memo
                # None, range_forwards False) we calculate the number of items
                # we would expect from the size of the collection. This is done
                # because that is what the older code did when range_factory
                # was added.
                size = self.listlength % self.size
                if not size:
                    size = self.size
            else:
                # We get one more item than we need, so that we can detect
                # cases where the underlying list ends on a batch boundary
                # without having to check the total size of the list (an
                # expensive operation).
                size = self.size + 1
            sliced = self.range_factory.getSlice(size, self.range_memo,
                self.range_forwards)
            if not self.range_forwards:
                sliced.reverse()
                if self.range_memo is not '' and len(sliced) <= size:
                    if len(sliced) == size:
                        # sliced is meant to have an extra element *after* the
                        # content for end-of-collection-detection, but the
                        # partitioner has just walked backwards, so shuffle things
                        # around to suit. If we didn't get as much data as we asked
                        # for we are at the beginning of the collection and all
                        # elements are needed.
                        sliced = sliced[1:] + sliced[:1]
                    else:
                        # If we got fewer than expected walking backwards, the
                        # range memo may have constrained us. So we need to get
                        # some more results:
                        needed = size - len(sliced)
                        partial = _PartialBatch(sliced)
                        extra_memo = (
                            self.range_factory.getEndpointMemos(partial))
                        extra = self.range_factory.getSlice(needed,
                            extra_memo[1], forwards=True)
                        sliced = sliced + extra
                        self.is_first_batch = True
        # This is the first time we get an inkling of (approximately)
        # how many items are in the list. This is the appropriate time
        # to handle edge cases.
        self._sliced_list = sliced
        return sliced

    def __iter__(self):
        sliced = self.sliced_list
        if len(sliced) > self.size:
            # The slice contains more than a full batch, indicating
            # that there is another batch beyond this one. But we
            # don't actually want to return the item from the next
            # batch.
            sliced = sliced[:-1]
        else:
            # The slice contains a full batch or less, indicating that
            # there is no batch beyond this one. In this case we want
            # to return the full slice.
            pass
        return iter(sliced)

    def first(self):
        return self[0]

    def last(self):
        return self[self.trueSize-1]

    def __contains__(self, item):
        return item in self.__iter__()

    @property
    def has_next_batch(self):
        """See `IBatch`."""
        # self.sliced_list tries to return one more object than the
        # batch size. If it returns the batch size, or fewer, then
        # this batch encompasses the end of the list, for forward
        # batching.
        # In the case of backward batching, an empty memo value
        # indicates that this is the last batch.
        if self.range_forwards:
            return len(self.sliced_list) > self.size
        else:
            return self.range_memo != ''

    def nextBatch(self):
        if not self.has_next_batch:
            return None

        start = self.start + self.size
        memos = self.range_factory.getEndpointMemos(self)
        return _Batch(self.list, self.range_factory, start, self.size,
            range_memo=memos[1], range_forwards=True,
            _listlength=self._listlength)

    @property
    def has_previous_batch(self):
        """See `IBatch`."""
        if self.range_memo is None:
            # If no range memo is specified, sliced_list() falls back
            # to slicing by index. This happens for old URLs, for example.
            return self.start > 0
        if self.range_forwards:
            # For forward batching, we are at the first batch if the memo
            # value is empty.
            return self.range_memo != ''
        else:
            # For backwards batching, we can rely on the flag set in
            # sliced_list. sliced_list is a @Lazy property, so make
            # sure that it has been evaluated.
            self.sliced_list
            return not self.is_first_batch

    def prevBatch(self):
        if not self.has_previous_batch:
            return None

        # The only case in which we should /not/ offer a previous batch
        # is when we are already at position zero, which also happens
        # when the list is empty.
        if self.start <= 0 and self.range_memo is None:
            return None
        start = self.start - self.size
        if start < 0:
            # This situation happens, for instance, when you have a
            # 20-item batch and you manually set your start to 15;
            # in this case, hopping back one batch would be starting at
            # -5, which doesn't really make sense.
            start = 0
        memos = self.range_factory.getEndpointMemos(self)
        return _Batch(self.list, self.range_factory, start, self.size,
            range_memo=memos[0], range_forwards=False,
            _listlength=self._listlength)

    def firstBatch(self):
        return _Batch(self.list, self.range_factory, 0, size=self.size,
            range_memo='', range_forwards=True, _listlength=self._listlength)

    def lastBatch(self):
        # Return the last possible batch for this dataset, at the
        # correct offset.
        last_index = self.listlength - 1
        last_batch_start = last_index - (last_index % self.size)
        if last_batch_start < 0:
            last_batch_start = 0
        return _Batch(self.list, self.range_factory, last_batch_start,
            size=self.size, range_memo='', range_forwards=False,
            _listlength=self._listlength)

    def total(self):
        return self.listlength

    def startNumber(self):
        return self.start+1

    def endNumber(self):
        # If this batch is completely empty, it makes no sense to ask for an
        # "endNumber" so return None.
        if not len(self.sliced_list):
            return None
        return self.start + min(self.size, len(self.sliced_list))
