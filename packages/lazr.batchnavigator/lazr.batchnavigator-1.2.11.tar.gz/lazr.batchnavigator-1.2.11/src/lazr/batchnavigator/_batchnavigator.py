# Copyright 2004-2010 Canonical Ltd.  All rights reserved.
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

__metaclass__ = type

import urllib
import cgi

from zope.interface import implements, classProvides
from zope.interface.common.sequence import IFiniteSequence
from zope.cachedescriptors.property import Lazy

from lazr.batchnavigator.z3batching.batch import _Batch
from lazr.batchnavigator.interfaces import (
    IBatchNavigator,
    IBatchNavigatorFactory,
    IRangeFactory,
    InvalidBatchSizeError,
    )

__all__ = [
    'BatchNavigator',
    'ListRangeFactory',
    ]

class BatchNavigator:

    # subclasses can override
    _batch_factory = _Batch

    implements(IBatchNavigator)
    classProvides(IBatchNavigatorFactory)

    start_variable_name = 'start'
    batch_variable_name = 'batch'
    memo_variable_name = 'memo'
    direction_variable_name = 'direction'
    # Set to e.g. 'active' to make the variable names become 'active_start',
    # 'active_batch' etc.
    variable_name_prefix = ''

    # The size the batch navigator was constructed with
    default_size = None
    # The size used if no specific size was supplied to the constructor.
    default_batch_size = 50
    max_batch_size = 300

    # We want subclasses to be able to hide the 'Last' link from
    # users.  They may want to do this for really large result sets;
    # for example, batches with over a hundred thousand items.
    show_last_link = True

    # The default heading describing the kind of objects in the batch.
    # Sub-classes can override this to be more specific.
    default_singular_heading = 'result'
    default_plural_heading = 'results'

    transient_parameters = None

    @Lazy
    def query_string_parameters(self):
        query_string = self.request.get('QUERY_STRING', '')

        # Just in case QUERY_STRING is in the environment explicitly as
        # None (Some tests seem to do this, but not sure if it can ever
        # happen outside of tests.)
        if query_string is None:
            query_string = ''
        return cgi.parse_qs(query_string, keep_blank_values=True)

    def __init__(self, results, request, start=0, size=None, callback=None,
                 transient_parameters=None, force_start=False,
                 range_factory=None):
        "See `IBatchNavigatorFactory.__call__`"
        self.request = request
        self._update_variable_names()
        local = (self.batch_variable_name, self.start_variable_name,
            self.memo_variable_name, self.direction_variable_name)
        self.transient_parameters = set(local)
        if transient_parameters is not None:
            self.transient_parameters.update(transient_parameters)

        # For backwards compatibility (as in the past a work-around has been
        # to include the url batch params in hidden fields within posted
        # forms), if the request is a POST request, and either the 'start'
        # or 'batch' params are included then revert to the default behaviour
        # of using the request (which automatically gets the params from the
        # request.form dict).
        if request.method == 'POST' and (
            self.start_variable_name in request.form or
            self.batch_variable_name in request.form):
            batch_params_source = request
        else:
            # We grab the request variables directly from the requests
            # query_string_parameters so that they will be recognized
            # even during post operations.
            batch_params_source = dict(
                (k, v[0]) for k, v
                in self.query_string_parameters.items() if k in local)

        # In this code we ignore invalid request variables since it
        # probably means the user finger-fumbled it in the request. We
        # could raise UnexpectedFormData, but is there a good reason?
        def param_var(name):
            return batch_params_source.get(name, None)
        # -- start
        request_start = param_var(self.start_variable_name)
        if force_start or request_start is None:
            self.start = start
        else:
            try:
                self.start = int(request_start)
            except (ValueError, TypeError):
                self.start = start
        # -- size
        size = self.determineSize(size, batch_params_source)
        # -- direction
        direction = param_var(self.direction_variable_name)
        if direction == 'backwards':
            direction = False
        else:
            direction = None
        # -- memo
        memo = param_var(self.memo_variable_name)
        if direction is not None and memo is None:
            # Walking backwards from the end - the only case where we generate
            # a url with no memo but a direction (and the only case where we
            # need it: from the start with no memo is equivalent to a simple
            # list slice anyway).
            memo = ''

        if range_factory is None:
            range_factory = ListRangeFactory(results)
        self.batch = self._batch_factory(results, range_factory,
            start=self.start, size=size, range_forwards=direction,
            range_memo=memo)
        if callback is not None:
            callback(self, self.batch)
        self.setHeadings(
            self.default_singular_heading, self.default_plural_heading)

    def determineSize(self, size, batch_params_source):
        """Determine the default and user requested batch sizes.

        This function should assign the default size for the batch to
        self.default_size. The base class implementation uses the size passed
        to the constructor, but other implementations may choose to clamp it or
        force a particular default size.

        :param size: Size passed to the constructor.
        :param batch_params_source: User parameters dict.
        :return: The size to be used for this batch.
        """
        self.default_size = size
        request_size = self._getRequestedSize(batch_params_source)
        if request_size is not None:
            size = request_size
        if size is None:
            size = self.default_batch_size
        return size

    def _getRequestedSize(self, batch_params_source):
        """Figure out what batch size the user requested, if any.

        Sizes that are not positive numbers are ignored.

        :return: An acceptable batch size requested by the user, or
            None.
        :raise: `InvalidBatchSizeError` if the requested size exceeds
            `max_batch_size`.
        """
        size_string = batch_params_source.get(self.batch_variable_name, None)
        if size_string is None:
            return None

        try:
            request_size = int(size_string)
        except (ValueError, TypeError):
            return None

        if request_size <= 0:
            return None

        if request_size > self.max_batch_size:
            raise InvalidBatchSizeError(
                'Maximum for "%s" parameter is %d.' %
                (self.batch_variable_name,
                 self.max_batch_size))

        return request_size

    @property
    def heading(self):
        """See `IBatchNavigator`"""
        if self.batch.total() == 1:
            return self._singular_heading
        return self._plural_heading

    def setHeadings(self, singular, plural):
        """See `IBatchNavigator`"""
        self._singular_heading = singular
        self._plural_heading = plural

    def getCleanQueryParams(self, params=None):
        """Removes batch nav params if present and returns a sequence
        of key-values pairs.

        If ``params`` is None, uses the current query_string_params.
        """
        if params is None:
            params = []
            for k, v in self.query_string_parameters.items():
                params.extend((k, item) for item in v)
        else:
            try:
                params = params.items()
            except AttributeError:
                pass

        # We need the doseq=True because some url params are for multi-value
        # fields.
        return [
            (key, value) for (key, value) in sorted(params)
            if key not in self.transient_parameters]

    def getCleanQueryString(self, params=None):
        """Removes batch nav params if present and returns a query
        string.

        If ``params`` is None, uses the current query_string_params.
        """
        # We need the doseq=True because some url params are for multi-value
        # fields.
        return urllib.urlencode(self.getCleanQueryParams(params), doseq=True)

    def generateBatchURL(self, batch, backwards=False):
        url = ""
        if batch is None:
            return url

        params = self.getCleanQueryParams()

        size = batch.size
        if size != self.default_size:
            # The current batch size should only be part of the URL if it's
            # different from the default batch size.
            params.append((self.batch_variable_name, size))

        if backwards:
            params.append((self.direction_variable_name, "backwards"))

        if batch.range_memo:
            params.append((self.memo_variable_name, batch.range_memo))

        start = batch.startNumber() - 1
        if start:
            params.append((self.start_variable_name, start))

        base_url = str(self.request.URL)
        return "%s?%s" % (base_url, urllib.urlencode(params))

    def firstBatchURL(self):
        batch = self.batch.firstBatch()
        if not self.batch.has_previous_batch:
            # We are already on the first batch.
            batch = None
        return self.generateBatchURL(batch)

    def prevBatchURL(self):
        return self.generateBatchURL(self.batch.prevBatch(), backwards=True)

    def nextBatchURL(self):
        return self.generateBatchURL(self.batch.nextBatch())

    def lastBatchURL(self):
        batch = self.batch.lastBatch()
        if not self.batch.has_next_batch:
            # We are already on the last batch.
            batch = None
        return self.generateBatchURL(batch, backwards=True)

    def currentBatch(self):
        return self.batch

    def _update_variable_names(self):
        """Update self.x_variable_name with self.variable_name_prefix.

        This gives the concrete instance the same prefix for all variables.
        """
        prefix = self.variable_name_prefix or ''
        if prefix:
            prefix += '_'
        for varname in ('start', 'batch', 'memo', 'direction'):
            attrname = varname + '_variable_name'
            setattr(self, attrname, prefix + getattr(self, attrname))


class ListRangeFactory:
    """Implements an IRangeFactory for lists (and list-like objects).

    This uses the slice protocol index as its memos: 'up to and not including
    low', 'from this point and up'.
    """

    implements(IRangeFactory)

    def __init__(self, results):
        self.results = results

    def getEndpointMemos(self, batch):
        """See `IRangeFactory`

        Most implementations will want to use batch.sliced_list to retrieve
        database keys.
        """
        end_idx = batch.trueSize + batch.start
        return (str(batch.start), str(end_idx))

    def getSlice(self, size, endpoint_memo=None, forwards=True):
        """See `IRangeFactory`"""
        if not size:
            return []
        if not forwards:
            size = -size
        if endpoint_memo:
            try:
                offset = int(endpoint_memo)
            except ValueError:
                raise InvalidBatchSizeError('not an int')
            offset_plus_size = offset + size
            if offset_plus_size < 1:
                offset_plus_size = 0
        else:
            offset = None
            offset_plus_size = size
        if forwards:
            return list(self.results[offset:offset_plus_size])
        else:
            if offset is None:
                # SQL mapped result sets will blow up on [-N:None] slices, so
                # get the total size and create absolute references.
                # This is only used for the 'Last' link in a collection, and
                # any nontrivial collection shouldn't be using ListRangeFactory
                # unless indexing is cheap (which implies counting is cheap).
                # If this becomes an issue, a shared length cache can be built
                # with _Batch, but because other implementations of
                # IRangeFactory would need to honour that protocol, it should
                # be avoided unless needed.
                if getattr(self.results, '__len__', None) is None:
                    self.results = IFiniteSequence(self.results)
                total_length = len(self.results)
                offset = total_length
                # Storm raises an exception for a negative initial offset.
                offset_plus_size = max(offset + offset_plus_size, 0)
            if offset_plus_size == offset:
                # Save a query if the slice is empty.
                # offset cannot be None so we don't have to deal with the
                # effect of None parameters as slice boundaries.
                return []
            else:
                result = list(self.results[offset_plus_size:offset])
                result.reverse()
                return result

    def getSliceByIndex(self, start, end):
        """See `IRangeFactory`"""
        if self.results is not None:
            return list(self.results[start:end])
        else:
            return []

    @Lazy
    def rough_length(self):
        """See `IRangeFactory`"""
        results = self.results
        # LBYL: we don't want to mask exceptions that len might raise, and we
        # don't have chained exceptions yet.
        if getattr(results, '__len__', None) is None:
            results = IFiniteSequence(results)
        return len(results)
