# Copyright 2004-2009 Canonical Ltd.  All rights reserved.
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

from zope.interface import Interface, Attribute

__metaclass__ = type


class InvalidBatchSizeError(AssertionError):
    """Received a batch parameter that was invalid (e.g. exceeds our configured max size)."""


class IRangeFactory(Interface):
    """A helper used to construct better backend queries for batches.

    IRangeFactory instances are paired with a result object that the
    BatchNavigator was constructed with. Generally they will be curried
    as part of determining what backend query to run for the thing being
    batched.
    """

    def getEndpointMemos(batch):
        """Converts a batch to a pair of (lower, upper) endpoint memos.

        :return: A tuple of bytestrings suitable for inclusion in URLs.
        """

    def getSlice(size, endpoint_memo='', forwards=True):
        """Returns a slice of the results starting after endpoint_memo.

        Note that endpoint_memo should be a simple string and is untrusted.

        :param size: The maximum number of entries to return in the slice.
        :param endpoint_memo: An endpoint memo as returned by getEndpointMemos.
            If None or '', the edge of the results is used.
        :param forwards: If True, slice forwards from endpoint_memo. Otherwise
            slice backwards from endpoint_memo (e.g. ascending indices in the
            result will indicate earlier items in the results collection).
        :return: An object honouring the tuple protocol, just like 'results' in
            the IBatchNavigatorFactory constructor call. If forwards was not
            True, the order will be reversed vs the 'results' object, otherwise
            it is identical. The object should be fully materialized from any
            backing store and have no more than size elements in it.
        """

    def getSliceByIndex(start, end):
        """Return a slice of the results.

        :param start: The index of the first element contained in the
            result.
        :param end: The index of the first element not contained in the
            result.
        """

    rough_length = Attribute(
        """The total length of the result set.

        The value does not have to be accurate; it should only be
        used for informational purposes.
        """)


class IBatchNavigator(Interface):
    """A batch navigator for a specified set of results."""

    batch = Attribute("The IBatch for which navigation links are provided.")

    heading = Attribute(
        "The heading describing the kind of objects in the batch.")

    def setHeadings(singular, plural):
        """Set the heading for singular and plural results."""

    def prevBatchURL():
        """Return a URL to the previous chunk of results."""

    def nextBatchURL():
        """Return a URL to the next chunk of results."""


class IBatchNavigatorFactory(Interface):
    def __call__(results, request, start=0, size=None, callback=None,
                 transient_parameters=None, force_start=False,
                 range_factory=None):
        """Constructs an `IBatchNavigator` instance.

        :param results: is an iterable of results.

        :param request: Expected to confirm to
            zope.publisher.interfaces.IRequest.
            The following variables are pulled out of the request to control
            the batch navigator:
              - memo: A record of the underlying storage index pointer for the
                position of the batch.
              - direction: Indicates whether the memo is at the start or end of
                the batch.
              - start: Cosmetic - used to calculate the apparent location (but
                note that due to the concurrent nature of repeated visits to
                batches that the true offset may differ - however the
                collection won't skip or show items twice. For compatibility
                with saved URLs, if memo and direction are both missing then
                start is used to do list slicing into the collection.
              - batch: Controls the amount of items we are showing per batch.
                It will only appear if it's different from the default value
                set when the batch is created.

        :param size: is the default batch size, to fall back to if the
            request does not specify one.  If no size can be determined
            from arguments or request, the launchpad.default_batch_size
            config option is used.

        :param callback: is called, if defined, at the end of object
            construction with the defined batch as determined by the
            start and request parameters.

        :param transient_parameters: optional sequence of parameter
            names that should not be passed on in links generated by
            the batch navigator.  Use this for parameters that had
            meaning when this page was requested, but should not be kept
            around for other page requests in the batch.

        :param force_start: if True, the given `start` argument has
            precedence over the start value in the request, if any.

        :param range_factory: An IRangeFactory paired with results, or None.
            If None, a default IRangeFactory is constructed which simply adapts
            results.

        :raises InvalidBatchSizeError: if the requested batch size is higher
            than the maximum allowed.
        """
