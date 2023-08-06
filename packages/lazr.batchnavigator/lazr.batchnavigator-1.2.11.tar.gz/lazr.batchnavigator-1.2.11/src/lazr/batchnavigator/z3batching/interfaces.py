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
"""Batching Support

$Id$
"""
from zope.interface import Attribute
from zope.interface.common.mapping import IItemMapping

class IBatch(IItemMapping):
    """A Batch represents a sub-list of the full enumeration.

    The Batch constructor takes a list (or any list-like object) of elements,
    a starting index and the size of the batch. From this information all
    other values are calculated.
    """

    def __len__():
        """Return the length of the batch. This might be different than the
        passed in batch size, since we could be at the end of the list and
        there are not enough elements left to fill the batch completely."""

    def __iter__():
        """Creates an iterator for the contents of the batch (not the entire
        list)."""

    def __getitem__(index):
        """Return the element at the given offset."""

    def __contains__(key):
        """Checks whether the key (in our case an index) exists."""

    def nextBatch():
        """Return the next batch. If there is no next batch, return None."""

    def prevBatch():
        """Return the previous batch. If there is no previous batch, return
        None."""

    def first():
        """Return the first element of the batch."""

    def last():
        """Return the last element of the batch."""

    def total():
        """Return the length of the list (not the batch)."""

    def startNumber():
        """Give the start **number** of the batch, which is 1 more than the
        start index passed in."""

    def endNumber():
        """Give the end **number** of the batch, which is 1 more than the
        final index."""

    sliced_list = Attribute(
        "A sliced list as returned by IRangeFactory.sliced_list.")

    trueSize = Attribute("The actual size of this batch.")

    has_previous_batch = Attribute(
        "True, if this batch has a predecessor, else False.")

    has_next_batch = Attribute(
        "True, if this batch has a successor, else False.")
