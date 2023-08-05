# -*- test-case-name: piped.test.test_util -*-

# Copyright (c) 2010-2011, Found IT A/S and Piped Project Contributors.
# See LICENSE for details.
import datetime
import functools
import itertools
import logging
import math
import operator
import os
import random
import sys
import xmlrpclib
import copy
import json

import twisted
from twisted.internet import defer, reactor
from twisted.application import service
from twisted.python import failure, filepath, reflect

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


logger = logging.getLogger(__name__)


def chunked(iterable, chunk_size):
    """ Yield `chunk_size`-sized chunks of `iterable`.

    Example: ::

        >>> list(chunked(range(10), chunk_size=3))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    tmp = []
    i = 1
    for obj in iterable:
        tmp.append(obj)
        if not i % chunk_size:
            yield tmp
            tmp = []
        i += 1
    if tmp:
        yield tmp


def create_lambda_function(definition, **namespace):
    lambda_namespace = dict()
    for key, value in namespace.items():
        if isinstance(value, basestring):
            value = reflect.namedAny(value)
        lambda_namespace[key] = value

    # create the function by evaluating the definition
    function = eval('lambda %s'%definition, lambda_namespace)

    return function


def _get_paths(maybe_iterable, separator='.'):
    if isinstance(maybe_iterable, basestring):
        return maybe_iterable.split(separator)
    elif hasattr(maybe_iterable, '__iter__'):
        return maybe_iterable
    else:
        return [maybe_iterable]


def dict_get_path(dict_like, path_or_list, fallback=None, separator='.'):
    """ Walk *dict_like* with the path-components as keys. If items
    are not found, then attribute lookups with the keys are performed.

    If the path is not found or a non-dict-like object without the key
    as an attribute is found, *fallback* is returned.

    If *path_or_list* is a string, it is split by *separator*. If not,
    it is assumed to be an iterable that returns path keys.

    Example: ::

        >>> d = dict(a=dict(b=dict(c='d')))
        >>> dict_get_path(d, 'a.b.c')
        'd'
        >>> dict_get_path(d, 'a.b.nonexistent')
        >>> dict_get_path(d, 'a.b.nonexistent', 'fallback')
        'fallback'

        >>> class Foo:
        ...     def __init__(self, wrapped):
        ...         self.wrapped = wrapped
        ...
        >>> d = dict(a=Foo(dict(b='c')))
        >>> dict_get_path(d, 'a.wrapped.b')
        'c'
        >>> dict_get_path(d, 'a.no_such_attribute', 'fallback')
        'fallback'

    .. note ::

        This is not a performant way to look up things. It's meant to
        be flexible and make it easy to delve into graphs of
        dicts/objects, but do not use it in performance critical
        paths.

    """
    if path_or_list == '':
        return dict_like

    for key in _get_paths(path_or_list, separator):
        try:
            dict_like = dict_like[key]
        except (KeyError, TypeError, AttributeError):
            try:
                dict_like = getattr(dict_like, key)
            except AttributeError:
                return fallback
    return dict_like


def dict_set_path(dict_like, path_or_list, value, separator='.'):
    """ Walk *dict_like* with the path-components as keys. The last
    component of the path is used as a key in the last dict-like.

    Like `dict_set_path`, this will also delve into attributes. If
    part of the path does not exist, an empty dictionary is created if
    the object with the missing key provides a `setdefault`-method.

    If *path_or_list* is a string, it is split by *separator*. If not,
    it is assumed to be an iterable that returns path keys.

    Example: ::
        >>> d = dict(a=dict(b=dict(c='d')))
        >>> dict_set_path(d, 'a.b.c', 'e')
        >>> d
        {'a': {'b': {'c': 'e'}}}
        >>> dict_set_path(d, 'a', 'b')
        >>> d
        {'a': 'b'}
        >>> dict_set_path(d, 'b.c', 'd')
        >>> d
        {'a': 'b', 'b': {'c': 'd'}}
    """
    # We don't simply reuse dict_get_path here, because we want to be
    # stricter about missing path components.
    keys = _get_paths(path_or_list, separator)
    for key in keys[:-1]:
        try:
            dict_like.setdefault(key, dict()) # Failing will raise AttributeError
            dict_like = dict_like[key] # Failling will raise TypeError or KeyError
        except (KeyError, TypeError, AttributeError):
            # It's not a dict. Try to reach an attribute. If that fails, give up.
            dict_like = getattr(dict_like, key)

    key = keys[-1]
    try:
        dict_like[key] = value
    except (TypeError, ValueError, AttributeError):
        # Not a dict, so try setting an attribute. If that fails, give up.
        if hasattr(dict_like, key):
            setattr(dict_like, key, value)
        else:
            raise AttributeError('%r has no attribute "%s"' % (dict_like, key))


def dict_remove_path(dict_like, path_or_list, separator='.', ignore_missing=True):
    """ Remove the value on the specified path from its containing
    dict_like.

    The semantics for path lookups are the same as in `dict_get_path`.

    If *ignore_missing* is false, then a `KeyError` is raised if the
    path cannot be removed.
    """
    keys = _get_paths(path_or_list, separator)
    path_of_parent = keys[:-1]
    key_to_remove = keys[-1]
    parent = dict_get_path(dict_like, path_of_parent)

    try:
        if parent:
            del parent[key_to_remove]
        else:
            if not ignore_missing:
                raise KeyError('Could not remove "%s" from %r' % (path_or_list, dict_like))
    except KeyError:
        if not ignore_missing:
            raise


def dict_setdefault_path(dict_like, path_or_list, value, separator='.'):
    """ Sets the configuration key specified by *path* to *value*,
    unless a value is already defined for that path. Returns the value
    of *path* --- i.e. either *value* or the already existing value.

    Example: ::
        >>> d = dict(a=dict(b=dict(c='d')))
        >>> dict_setdefault_path(d, 'a.b.c', 'e')
        'd'
        >>> dict_setdefault_path(d, 'a.b.e', 'f')
        'f'
        >>> d
        {'a': {'b': {'c': 'd', 'e': 'f'}}}

    .. :seealso: ::

        :ref:`~piped.util.dict_set_path`
            for more on the behaviour of setting with key paths.
    """
    existing_value = dict_get_path(dict_like, path_or_list, Ellipsis, separator)
    if existing_value is Ellipsis:
        dict_set_path(dict_like, path_or_list, value, separator)
        return value
    else:
        return existing_value


def dict_iterate_paths(dict_like, separator='.'):
    """ Returns an iterator which yields a path and value tuple for each entry. """
    queue = [[key] for key in dict_like.keys()]
    while queue:
        key = queue.pop(0)
        value = dict_get_path(dict_like, key)

        yield separator.join([str(k) for k in key]), value

        if hasattr(value, 'keys') and callable(value.keys):
            new_keys = [key+[new_key] for new_key in value.keys()]
            queue.extend(new_keys)


def ensure_date(date_like):
    """ Convert *date_like* into a `datetime.date`-object.

    *date_like* is assumed to either already be a date- or a
     datetime-object, or a UNIX-timestamp.
    """
    # We check for datetime.datetime first, as a datetime is also a date.
    if isinstance(date_like, datetime.datetime):
        return date_like.date()
    elif isinstance(date_like, datetime.date):
        return date_like
    elif isinstance(date_like, (int, long)):
        return datetime.datetime.utcfromtimestamp(date_like).date()
    else:
        raise ValueError('Expected date-like object, got ' + repr(date_like))


def ensure_filepath(filepath_or_path):
    if isinstance(filepath_or_path, basestring):
        return filepath.FilePath(filepath_or_path)
    return filepath_or_path


def ensure_unicode(s, errors='strict'):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return unicode(s, 'utf8', errors)
    return unicode(s)


def expand_filepath(path):
    """ Returns the full path to a file. """
    return os.path.expandvars(os.path.expanduser(getattr(path, 'path', path)))


def flatten(list_like, recursive=True):
    """ Flattens a list-like datastructure (returning a new list). """
    retval = []
    for element in list_like:
        if isinstance(element, list):
            if recursive:
                retval += flatten(element, recursive=True)
            else:
                retval += element
        else:
            retval.append(element)
    return retval


def in_unittest():
    """ Return whether we're running under trial. """
    supported_test_runners = 'trial', 'nose'
    for test_runner in supported_test_runners:
        if test_runner in sys.argv[0]:
            return True
    return False


def interleaved(*iterables):
    """ Interleaves elements from the iterables.

    Assumes that all iterables yield the same number of elements.

    Example:

    >>> interleaved([1,3], [2,4])
    (1, 2, 3, 4)
    >>> interleaved([1,3], [2])
    (1, 2)
    """
    return reduce(operator.concat, itertools.izip(*iterables))


def merge_dicts(first, second, inline=False, replace=False, replace_primitives=False, merge_nested_dictionaries=True):
    """ Merges the two supplied dictionaries into a new one.

    @param first: First dictionary to merge.
    @param second: Second dictionary to merge.
    @param inline: If True, performs the changes inline in the first dictionary.
    @param replace: Replaces keys that already exist in first with the values from second.
    @param replace_primitives: Replace primitives (strings/ints/lists)
    @param merge_nested_dictionaries: If True, recurses when finding nested dictionaries.
    @return: A dict with the merged results. If inline is True, result == first.
    """
    # TODO: set support
    merged = first
    if not inline: merged = dict(first)
    for key, value in second.items():
        if key in merged:
            if replace: #we wanted replacing, so do it
                merged[key] = value
                continue
            elif isinstance(merged[key], dict) and merge_nested_dictionaries:
                # some special handling if dictionaries
                merged[key] = merge_dicts(merged[key], value, replace=replace, merge_nested_dictionaries=merge_nested_dictionaries, replace_primitives=replace_primitives)
            else: # merged[key] is not a dict we want to merge
                if replace_primitives:
                    merged[key] = value
                elif isinstance(value, list): # but value is a list
                    merged[key] = list(merged[key])+value
                else: # value is not a list
                    merged[key] = [merged[key]]
                    merged[key].append(value)
        else: # key didnt exist before, so just copy it
            merged[key] = value
    return merged


def resolve_sibling_import(import_pipeline_name, current_pipeline_name):
    # one dot per level up: http://www.python.org/dev/peps/pep-0328/#id9
    if import_pipeline_name.startswith('.'):
        import_prefix = current_pipeline_name.split('.')

        while import_pipeline_name.startswith('.'):
            import_prefix = import_prefix[:-1] # remove the last part of the prefix
            import_pipeline_name = import_pipeline_name[1:] # remove a dot

        import_pipeline_name = '.'.join(import_prefix+[import_pipeline_name])

    return import_pipeline_name


def safe_deepcopy(dict_like, object_describer=repr, path_of_paths='_volatile', separator='.'):
    """
    deepcopy() *dict_like*, but values of the paths found in
    *path_of_paths* (if any) are replaced with those provided by
    *object_describer*.

    The object returned by *object_describer* should also be pickleable.

    Example:

        >>> class uncopyable(object):
        ...     def __deepcopy__(self, memo):
        ...         raise copy.Error("Intentional copy error")
        ...
        >>> problem_object = uncopyable()
        >>> d = dict(foo='bar', nested=dict(unsafe=problem_object), _volatile=['nested.unsafe'])
        >>> safe_deepcopy(d) # Note how problem_object is replaced by its repr() # doctest: +ELLIPSIS
        {'foo': 'bar', '_volatile': ['nested.unsafe'], 'nested': {'unsafe': '<...uncopyable object at 0x...>'}}
        >>> d # doctest: +ELLIPSIS
        {'foo': 'bar', '_volatile': ['nested.unsafe'], 'nested': {'unsafe': <...uncopyable object at 0x...>}}
    """
    paths_to_describe = dict_get_path(dict_like, path_of_paths, [], separator)
    if not paths_to_describe:
        return copy.deepcopy(dict_like)

    # Backup all references and replace the values in the original with object descriptions.
    backups = dict()
    sentinel = object()
    for path in paths_to_describe:
        volatile_value = dict_get_path(dict_like, path, sentinel, separator)
        if volatile_value is sentinel:
            # No value at the path, so just skip.
            continue

        # Keep a reference to the original, which we throw back after the copy has been made.
        backups[path] = volatile_value
        # We assume that object_describer results in a copyable value.
        dict_set_path(dict_like, path, object_describer(volatile_value), separator)

    try:
        final_copy = copy.deepcopy(dict_like)
    finally:
        # Restore the volatile values, so dict_like is returned as-is.
        for path, volatile_value in backups.items():
            dict_set_path(dict_like, path, volatile_value, separator)

    return final_copy


def wait(nap_time, result=None):
    # Chicken and the egg: we want the returned defer to be able to cancel the delayed-call,
    # but the Deferred api only supports setting the canceller when we're creating the
    # deferred, but the delayed_call needs to know which Deferred it should callback. We
    # solve this by setting the `cancel` function directly on the Deferred after creating
    # the delayed call, before returning the Deferred.
    d = defer.Deferred()
    delayed_call = reactor.callLater(nap_time, d.callback, result)
    d.cancel = lambda: (delayed_call.cancel(), d.errback(defer.CancelledError()))
    return d

class AttributeDict(dict):
    """ Dict where attributes can also be used to get the items. Used
    for simple stubs when testing. """

    def __getattribute__(self, key):
        value = dict.get(self, key)
        if value is not None:
            return value
        return object.__getattribute__(self, key)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class OrderedDictionary(OrderedDict):

    def replace_key(self, existing_key, new_key, new_value):
        """ Deletes *existing_key* and replaces it with *new_key* and
        its *new_value*, but lets *new_key* get *existing_key*s place
        in the ordering.

        Example: ::
           >>> d = OrderedDictionary([('foo', 1), ('bar', 2)])
           >>> d.replace_key('foo', 'notfoo', 1)
           >>> d
           OrderedDictionary([('notfoo', 1), ('bar', 2)])
        """

        if not existing_key in self:
            raise KeyError(existing_key)

        set_keys = False # controls whether keys are re-set

        for key in self.keys()[:]: # get a copy, since we're modifying the dict
            if key == existing_key:
                # replace the key
                del self[existing_key]
                self[new_key] = new_value

                # re-set the rest of the keys, to preserve the ordering
                set_keys = True
                continue # in order to avoid setting the existing key we just deleted

            if set_keys:
                # we have to delete the key, then set it in order to move it to the end
                value = self[key]
                del self[key]
                self[key] = value

    def update(self, dict_or_items=None):
        """ Update from another OrderedDict or dict or sequence of
        (key, value) pairs. If provided an unordered dictionary, it is
        only accepted if the existing keys already exist.
        """
        if dict_or_items is None:
            return

        if isinstance(dict_or_items, dict) and not isinstance(dict_or_items, OrderedDict):
            if not set(self.keys()) == set(dict_or_items.keys()):
                # If we accepted just any dictionary, we'd violate the
                # Ordered-contract. However, it's often useful to just
                # provide a kw from **kw, which NetworkX often does.
                #    If a user doesn't care about ordering, he could just do
                #  for k,v in regular_dict.items(): odict[k]=v
                raise TypeError('undefined order, cannot get items from dict')
            items = dict_or_items.items()
        else:
            items = dict_or_items
        super(OrderedDictionary, self).update(items)


class PipedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, xmlrpclib.DateTime):
            obj = datetime.datetime.strptime(obj.value, '%Y%m%dT%H:%M:%S')
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        if hasattr(obj, '__json__'):
            return obj.__json__()
        if isinstance(obj, filepath.FilePath):
            # if we have the original path, use it, unless its a path that is
            # relative to our source tree because it will probably not make sense
            # without additional information about what it is relative to.
            if hasattr(obj, 'origpath') and not hasattr(obj, 'pipedpath'):
                return obj.origpath
            return obj.path
        return super(PipedJSONEncoder, self).default(obj)


class BatonJSONEncoder(PipedJSONEncoder):
    """ A custom JSON encoder that falls back to repr() if an exception is raised
    during JSON encoding. """
    def default(self, obj):
        try:
            return super(BatonJSONEncoder, self).default(obj)
        except TypeError as te:
            return repr(obj)


class PullFromQueueAndProcessWithDependency(service.Service):
    _waiting_on_queue = None
    _waiting_on_processor = None

    def __init__(self, deferred_queue, dependency_config):
        self.deferred_queue = deferred_queue
        self.dependency_config = dict(provider=dependency_config) if isinstance(dependency_config, basestring) else dependency_config

    def configure(self, runtime_environment):
        self.runtime_environment = runtime_environment
        dependency_manager = runtime_environment.dependency_manager

        self._processor_dependency = dependency_manager.add_dependency(self, self.dependency_config)

    def startService(self):
        service.Service.startService(self)

        if self._waiting_on_processor:
            # We've been started, stopped, started again, and there's
            # processing going on. The process-loop will find
            # self.running to be true, so let it continue instead of
            # having multiple processing loops.
            return

        self._process_input()

        logger.info('Starting pulling: %s using %s.'%(self.name, self.dependency_config['provider']))

    def stopService(self):
        service.Service.stopService(self)

        if self._waiting_on_queue:
            self._waiting_on_queue.cancel()

        logger.info('Stopped pulling: %s.'%self.name)

    @defer.inlineCallbacks
    def _process_input(self):
        while self.running:
            self._waiting_on_queue = self.deferred_queue.get()
            try:
                baton = yield self._waiting_on_queue
            except defer.CancelledError:
                # the deferred has been cancelled by stopService, so return
                return
            finally:
                self._waiting_on_queue = None

            try:
                self._waiting_on_processor = self._processor_dependency.wait_for_resource()
                processor = yield self._waiting_on_processor
                self._waiting_on_processor = processor(baton)
                yield self._waiting_on_processor
            except Exception as e:
                # An exception occurred while processing the baton, and we don't have anyone to inform
                # so just log the exception and continue
                logger.error('Exception raised while processing baton', exc_info=True)
            finally:
                self._waiting_on_processor = None


# we store a reference to the superclass of NonCleaningFailure here because it may change
# due to the monkey-patching performed when piped is started with the -D argument
NonCleaningFailureSuperClass = failure.Failure

class NonCleaningFailure(NonCleaningFailureSuperClass):
    """ A Failure subclass that doesn't replace its traceback with repr'd objects. """

    def __init__(self, *a, **kw):
        # default to capturing vars (locals/globals) in frames when using this class, since
        # the user most likely isn't worried about the additional cost. this is the default
        # in twisted <= 11.0
        if (twisted.version.major, twisted.version.minor) > (11, 0):
            kw.setdefault('captureVars', True)

        NonCleaningFailureSuperClass.__init__(self, *a, **kw)

    def cleanFailure(self):
        pass


def create_deferred_state_watcher(obj, attribute_name='_currently'):
    """
    Creates a function that when called with a deferred, assigns the deferred to the
    specified attribute on the target object. When the deferred callbacks or errbacks,
    the attribute is cleared.

    This can be used to implement functions that should only be executed by one concurrent
    invocation:

        >>> class A(object):
        ...     running = None # stores the currently running state
        ...
        ...     def run(self):
        ...         if self.running:
        ...             # in this example we return here, but we could have called
        ...             # ``self.running.cancel()`` to cancel the previous invocation and continued.
        ...             print 'already running'
        ...             return
        ...
        ...         # create the watcher.
        ...         currently = create_deferred_state_watcher(self, 'running')
        ...
        ...         return currently(wait(0))
        ...
        >>> a = A()
        >>> d = a.run()
        >>> a.run()
        already running
    """
    def clear(result):
        setattr(obj, attribute_name, None)
        return result

    def wrapper(retval):
        if isinstance(retval, defer.Deferred):
            setattr(obj, attribute_name, retval)
            retval.addBoth(clear)

        return retval

    return wrapper


def fail_after_delay(delay, exception):
    """ Returns a Deferred that will errback with `exception` after `delay`. """
    d = defer.Deferred()
    reactor.callLater(delay, d.errback, exception)
    return d


def wait_for_first(ds):
    """ Returns a deferred that is callbacked/errbacked with whatever deferred in `ds` fires first. """
    d = defer.DeferredList(ds, fireOnOneCallback=True, fireOnOneErrback=True, consumeErrors=True)
    d.addCallback(operator.itemgetter(0))
    d.addErrback(get_maybe_first_error_failure)
    return d


def get_callable_with_different_side_effects(side_effects):
    """ Returns a callable that either returns a value, returns the
    result of a callable or raises an exception for a call *i*
    depending on the *i*-th value of *side_effects*.

    This is useful when needing different side-effects for mocked calls.

    Example: ..:

        >>> f = get_callable_with_different_side_effects([1, lambda: 42, Exception('err'), 2])
        >>> f()
        1
        >>> f()
        42
        >>> f() # doctest:+ELLIPSIS
        Traceback (most recent call last):
        ...
        Exception: err
        >>> f()
        2
    """
    side_effects = iter(side_effects)

    def _wrapped(*a, **kw):
        side_effect = side_effects.next()

        if isinstance(side_effect, Exception):
            raise side_effect
        elif hasattr(side_effect, '__call__'):
            return side_effect(*a, **kw)
        else:
            return side_effect

    return _wrapped


def get_maybe_first_error_failure(reason):
    """ Get the nested failure if the given failure contains a FirstError exception.

    :param reason: A :class:`twisted.python.failure.Failure` instance
    :return: The nested subFailure if the failure contained a FirstError exception.
    """
    if reason.type == defer.FirstError:
        return reason.value.subFailure
    return reason


def deferred_with_timeout(d, timeout=None, timeout_exception=Exception('timeout')):
    """ Gets a deferred with added support for waiting for a timeout to occur.

    The configured DelayedCall is cancelled if the given deferred callbacks/errbacks before the timeout.

    :param d: The deferred to add a timeout to.
    :param timeout: Timeout (in seconds) before the timeout exception is raised.
    :param timeout_exception: The exception to raise.
    :return:
    """
    if timeout is None:
        return d

    timeout_deferred = defer.Deferred()
    delayed_call = reactor.callLater(timeout, timeout_deferred.errback, timeout_exception)

    def cleanup(_, delayed_call=delayed_call):
        if not delayed_call.called:
            delayed_call.cancel()
        return _

    dl = defer.DeferredList([d, timeout_deferred], fireOnOneCallback=True, fireOnOneErrback=True, consumeErrors=True)

    return_deferred = dl.addCallback(operator.itemgetter(0)).addErrback(get_maybe_first_error_failure)

    return return_deferred.addBoth(cleanup)


class Cancellable(object):

    def __init__(self):
        self._children_cancellables = set()
        self._deferreds_cancellable = set()
        self._parent_cancellable = None

    def set_cancellable_parent(self, parent_cancellable):
        if parent_cancellable == self._parent_cancellable:
            return

        self.disown_cancellable_parent()

        self._parent_cancellable = parent_cancellable

        if parent_cancellable:
            parent_cancellable._add_cancellable_child(self)

    def disown_cancellable_parent(self):
        if not self._parent_cancellable:
            return

        self._parent_cancellable._remove_cancellable_child(self)

        self._parent_cancellable = None

    def disown_cancellable_parent_callback(self, _, cancel=False):
        self.disown_cancellable_parent()
        if cancel:
            self.cancel()
        return _

    def cancel(self):
        """ Cancels cancellables. """
        deferreds_to_cancel, self._deferreds_cancellable = self._deferreds_cancellable, set()
        for deferred in deferreds_to_cancel:
            deferred.cancel()

    def _add_cancellable_child(self, child):
        self._children_cancellables.add(child)

    def _remove_cancellable_child(self, child):
        self._children_cancellables.remove(child)

    def cancellable(self, d):
        """ Add's the deferred to the set of deferreds that will be
        cancelled if `cancel()` is invoked.

        This is useful when you wait for deferreds that do not
        necessarily stop when this service stops --- especially when
        the process will continue on/restart this services and the
        "abandoned" deferreds and their callback-chains consume a lot
        of memory.
        """
        if not isinstance(d, defer.Deferred):
            return d

        self._deferreds_cancellable.add(d)
        # If the deferred is callbacked/errbacked, we no longer need
        # to keep it in the set.
        d = d.addBoth(functools.partial(self._remove_deferred_and_passthrough, d))
        return d

    def _remove_deferred_and_passthrough(self, d, result):
        self._deferreds_cancellable.discard(d)
        return result


class DeferredLock(defer.DeferredLock):
    entered = False

    def __enter__(self):
        self.entered = True
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.entered:
            return self.release()
        return


class BackoffWaiter(object):
    """ waits, longer and longer, until reaching max_delay. """
    factor = math.e
    jitter = 0.11962656472

    def __init__(self, initial_delay=1.0, max_delay=300.0):
        self._waits = 1
        self._initial_delay = initial_delay
        self._max_delay = max_delay

    def wait(self):
        d = defer.Deferred()
        delay = self._initial_delay * self.factor ** self._waits
        if delay > self._max_delay:
            self._waits = 1
            delay = self._max_delay

        delay = random.normalvariate(delay, delay * self.jitter)
        self._waits += 1
        delayed_call = reactor.callLater(delay, d.callback, None)

        def _cancel(failure):
            failure.trap(defer.CancelledError)
            if delayed_call.active():
                delayed_call.cancel()
            return failure

        d.addErrback(_cancel)

        return d

    def reset():
        self._waits = 1
