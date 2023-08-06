import tblib.pickling_support
# allows pickling of basic information from tracebacks:
tblib.pickling_support.install()

import abc
import dill
import functools
import itertools
import multiprocessing
import os
import sys
import Queue
import random
import time
import traceback

from pacer.std_logger import get_logger


class DelayedException(object):

    """store exception for throwing it later.
       we use this for transfering an exception on a worker process to the
       main process.
       only works because we imported and installed tblib above
       """

    def __init__(self, ee):
        self.ee = ee
        __,  __, self.tb = sys.exc_info()

    def re_raise(self):
        raise self.ee, None, self.tb

    def as_string(self):
        return "".join(traceback.format_exception(self.ee, None, self.tb, limit=None))


def printable(what):
    what = repr(what)
    if len(what) > 60:
        return what[:28] + " .. " + what[-28:]
    else:
        return what


def eval_pickled(f_s, args_s):
    """ requires function and args serialized with dill, so we can remote execute even lambdas or
    decorated functions or static methods, which 'pure' multiprocssing can not handle"""

    try:
        args = dill.loads(args_s)
    except Exception, e:
        get_logger(eval_pickled).error("got exception when unpickling args: {}".format(e))
        return DelayedException(e)
    try:
        f = dill.loads(f_s)
    except Exception, e:
        get_logger(eval_pickled).error("got exception when unpickling f: {}".format(e))
        return DelayedException(e)
    try:
        s_args = printable(args)
        get_logger(f).info("start {}{} in process {}".format(f.__name__, s_args, os.getpid()))
        result = f(*args)
        s_result = printable(result)
        get_logger(f).info("got result {!s} from process {}".format(s_result, os.getpid()))
        return result
    except Exception, e:
        get_logger(f).error("got exception: {}".format(e))
        get_logger(f).exception(e)
        return DelayedException(e)


class EnumeratedItem(object):

    def __init__(self, number, value):
        self.number = number
        self.value = value

    def __iter__(self):
        return iter((self.number, self.value))


def wrap_callback(new_enumeration, callback):
    """creates a new callback which builds a EnumeratedItem from the reult """
    def new_callback(result):
        callback(EnumeratedItem(new_enumeration, result))
    return new_callback


class Engine(object):

    pool = None

    @staticmethod
    def set_number_of_processes(n):
        if n is None:
            Engine.pool = None
            return
        if n < 0:
            n = multiprocessing.cpu_count() - n
            n = max(n, 0)
        if n > 0:
            Engine.pool = multiprocessing.Pool(n)
        elif n == 0:
            Engine.pool = None
        else:
            raise Exception("can not set number of processes to %d" % n)

    @staticmethod
    def run_async(f, args, callback, run_local=False, debug=False):
        """ f is not implemented for handling enumerated items, so we exctract the items
        and construct a 'new enumeration' for the result.
        This is needed in order to ensure that the final result of the computations have
        a fixed order although their computation order might be different due to the
        concurrent processing.

        in debug mode the computation runs local but goes through the pickling/unpickling loop
        this enables use of debugger and allows detection of pickling problems

        """
        # we use eval_pickled in both cases to make shure we have the same kind of error handling
        # for local and remote execution. this supports debugging.

        if debug:
            # run computation local so we can use debugger
            # but use the pickling / unpickling procedure to detect pickling problems
            f_s = dill.dumps(f)
            args_s = dill.dumps(args)
            try:
                result = eval_pickled(f_s, args_s)
            except Exception, e:
                result = DelayedException(e)
            callback(result)
        else:
            run_local = run_local is True or Engine.pool is None
            if run_local:
                try:
                    get_logger(Engine).info("start {} with args {}".format(f, printable(args)))
                    result = f(*args)
                    get_logger(Engine).info("function {} returned {}".format(f, printable(result)))
                except Exception, e:
                    get_logger(Engine).info("function {} rose {}".format(f, e))
                    result = DelayedException(e)
                callback(result)
            else:
                f_s = dill.dumps(f)
                args_s = dill.dumps(args)
                Engine.pool.apply_async(eval_pickled, (f_s, args_s),
                                        callback=callback)


def _info(listener):
    return listener.f if hasattr(listener, "f") else listener


class DataStream(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        # self._stream = Queue.Queue()
        self._queues = dict()

    def empty(self, listener):
        get_logger(self).debug("%s asks for empty input queue", _info(listener))
        return self._queues.get(listener).empty()

    def get(self, listener):
        item = self._queues.get(listener).get()
        get_logger(self).debug("%s asks and gets item %d with value %s",
                               _info(listener), item.number, item.value)
        return item

    @abc.abstractmethod
    def size(self):
        pass

    def put(self, item):
        """this is where computation results are passed to."""
        for listener, queue in self._queues.items():
            get_logger(self).debug("put item %d with value %s to %s",
                                   item.number, item.value, _info(listener))
            queue.put(item)

    def register_listener(self, listener):
        assert listener not in self._queues
        self._queues[listener] = Queue.Queue()

    def start_computations(self):
        """
        starts computations at leafs first then up to the root
        """
        get_logger(self).debug("%s.start_computations() called ", self)
        for stream in self.input_streams:
            stream.start_computations()
        self._start_computation()
        return self


class Source(DataStream):

    def __init__(self, items=None):
        super(Source, self).__init__()
        self.items = items
        self.input_streams = []

    def set_input_items(self, items):
        self.items = items

    def set_input_item(self, item):
        self.items = [item]

    def size(self):
        return len(self.items)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)
        for i, item in enumerate(self.items):
            self.put(EnumeratedItem(i, item))


class Computation(DataStream):

    def __init__(self, f, inputs, run_local=False, debug=False):
        super(Computation, self).__init__()
        self.run_local = run_local
        self.debug = debug
        self.f = f
        self.input_streams = self._setup_inputs(inputs)

    def _setup_inputs(self, inputs):
        streams = []
        for input_ in inputs:
            stream = input_
            if not isinstance(input_, DataStream):
                if isinstance(input_, (tuple, list)):
                    stream = Source(input_)
                else:
                    stream = Source((input_,))
            stream.register_listener(self)
            streams.append(stream)
        return streams

    @abc.abstractmethod
    def _start_computation(self):
        pass

    def _start_async_computation_for(self, result_number, args):
        assert all(isinstance(arg, EnumeratedItem) for arg in args)
        forward_result = wrap_callback(result_number, self.put)
        for arg in args:
            if isinstance(arg.value, DelayedException):
                forward_result(arg.value)
                return
        args = tuple(a for (__, a) in args)
        Engine.run_async(self.f, args, forward_result, self.run_local, self.debug)


class OutputNode(DataStream):

    def __init__(self, input_):
        super(OutputNode, self).__init__()

        if not isinstance(input_, DataStream):
            if isinstance(input_, (tuple, list)):
                input_ = Source(input_)
            else:
                input_ = Source((input_,))

        input_.register_listener(self)
        self.input_ = input_

    def size(self):
        return self.input_.size()

    def __str__(self):
        return "<OutputNode(id=%d, %s)>" % (id(self), self.input_)

    def start_computations(self, do_not_reraise_exceptions=True):
        """
        starts computations at leafs first then up to the root
        """
        self.input_.start_computations()
        get_logger(self).debug("%s.start_computation() called ", self)

        results = []
        for _ in range(self.size()):
            item = self.input_.get(listener=self)
            if isinstance(item.value, DelayedException):
                if not do_not_reraise_exceptions:
                    item.value.re_raise()
            results.append(item)

        results.sort(key=lambda en_item: en_item.number)
        self.results = [item.value for item in results]

    def get_all_in_order(self, re_raise_exceptions=False):
        while self.results is None:
            time.sleep(0.001)
        if re_raise_exceptions:
            for r in self.results:
                if isinstance(r, DelayedException):
                    r.re_raise()
        return self.results


class _UpdateManagerForJoin(object):

    """ manages input data from sources which might come in in arbitrary order.  handles
    incremental generation of input_streams for computations.  """

    def __init__(self, input_streams):
        self.seen = set()
        self.data = [[None for __ in range(a.size())] for a in input_streams]
        self.next_ = [0] * len(input_streams)

    def new_function_arguments_for(self, stream_index, item):
        self.data[stream_index][self.next_[stream_index]] = item
        self.next_[stream_index] += 1
        # cross product over all indices of available data:
        sizes = [len(v) for v in self.data]
        for perm in itertools.product(*(range(size) for size in sizes)):
            if perm not in self.seen:
                args = tuple(self.data[j][pi] for j, pi in enumerate(perm))
                if all(ai is not None for ai in args):
                    number = args[0].number
                    for ai, si in zip(args[1:], sizes[1:]):
                        number = si * number + ai.number
                    yield number, args
                    self.seen.add(perm)

    def input_data_pending(self, size):
        return len(self.seen) < size


class JoinComputation(Computation):

    def size(self):
        return reduce(lambda x, y: x * y, (a.size() for a in self.input_streams))

    def __str__(self):
        return "<JoinComputation(id=%d, %s)>" % (id(self), self.f)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)

        manager = _UpdateManagerForJoin(self.input_streams)
        while manager.input_data_pending(self.size()):
            started_computation = False
            for i, stream in enumerate(self.input_streams):
                if not stream.empty(listener=self):
                    item = stream.get(listener=self)
                    if isinstance(item.value, DelayedException):
                        self.put(item)
                        return
                    for number, args in manager.new_function_arguments_for(i, item):
                        self._start_async_computation_for(number, args)
                        started_computation = True
            if not started_computation:
                time.sleep(0.001)


class FetchAllComputation(Computation):

    def _collect_input_data(self):
        items = []
        stream = self.input_streams[0]
        for i in range(stream.size()):
            item = stream.get(listener=self)
            if isinstance(item.value, DelayedException):
                self.put(item)
                return None, None
            items.append(item)

        fixed_args = []
        for other_stream in self.input_streams[1:]:
            assert other_stream.size() == 1
            item = other_stream.get(listener=self)
            if isinstance(item.value, DelayedException):
                self.put(item)
                return None, None
            fixed_args.append(item)

        items.sort(key=lambda item: item.number)
        values = [v for __, v in items]
        return values, fixed_args


class SummarizeComputation(FetchAllComputation):

    def size(self):
        return 1

    def __str__(self):
        return "<SummarizeComputation(id=%d, %s)>" % (id(self), self.f)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)

        values, fixed_args = self._collect_input_data()
        if values is None:
            return
        arg = EnumeratedItem(0, values)
        args = (arg,) + tuple(fixed_args)
        self._start_async_computation_for(0, args)


class FullStreamComputation(FetchAllComputation):

    def size(self):
        return self.input_streams[0].size()

    def __str__(self):
        return "<FullStreamComputation(id=%d, %s)>" % (id(self), self.f)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)

        values, fixed_args = self._collect_input_data()
        if values is None:
            return

        # this uses the plain engine because we hava a special callback which
        # creates a stream from a single computed list
        # this is why we have to work with plain data, not EnumeratedItem instances:
        def forward_result(result):
            if hasattr(result, "__iter__"):
                for i, item in enumerate(result):
                    self.put(EnumeratedItem(i, item))
            else:
                self.put(EnumeratedItem(0, result))

        args = (values,) + tuple(a.value for a in fixed_args)
        Engine.run_async(self.f, args, forward_result, self.run_local, self.debug)


class ComputedSource(Computation):

    def __init__(self, f, args):
        super(ComputedSource, self).__init__(f, [], True, False)
        self.f = f
        self.args = args
        self.items = None

    def size(self):
        return len(self.items)

    def __str__(self):
        return "<ComputedSource(id=%d, %s)>" % (id(self), self.f)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)
        args = self.args
        if len(args) == 1 and isinstance(args[0], Source):
            args = args[0].items
            assert len(args) == 1, "exepected source which only produces one data item"
        else:
            args = self.args
        self.items = list(self.f(*args))
        for i, item in enumerate(self.items):
            self.put(EnumeratedItem(i, item))


class ZipComputation(Computation):

    """either input_streams provide all n inputs or one fixed input. The latter is managed by
    ConstantSource class.
    """

    def size(self):
        sizes = set(s.size() for s in self.input_streams)
        if 1 in sizes:
            sizes.remove(1)
        if len(sizes) > 1:
            msg = "allow ownly sources with same sized outputs or constant constant source"
            raise Exception(msg)
        if len(sizes) == 1:
            return sizes.pop()
        # sizes has size 0 means: we only had inputs of size 1
        return 1

    def __str__(self):
        return "<ZipComputation(id=%d, %s)>" % (id(self), self.f)

    def _start_computation(self):
        get_logger(self).debug("%s._start_computation() called ", self)
        # wait and get the constant args which we need anyway:
        cip = self._collect_data_from_constant_input_streams()

        if self._found_and_handled_exception_in(cip):
            return

        # only constant inputs ?
        if self.size() == 1:
            self._start_async_computation_for(0, cip)
        else:
            self._zip_all(cip)

    def _collect_data_from_constant_input_streams(self):
        constant_inputs = [None] * len(self.input_streams)
        for i, stream in enumerate(self.input_streams):
            if stream.size() == 1:
                constant_inputs[i] = stream.get(listener=self)
        return constant_inputs

    def _found_and_handled_exception_in(self, args):
        for item in args:
            if item is not None:
                if isinstance(item.value, DelayedException):
                    self.put(item)
                    True
        return False

    def _zip_all(self, cip):
        seen = set()
        n = 0
        input_matrix = self._setup_input_matrix(cip)
        while n < self.size():
            avail = self._check_for_any_new_data()
            if avail:
                for number, args in self._assemble_function_arguments(input_matrix, seen):
                    if self._found_and_handled_exception_in(args):
                        return
                    self._start_async_computation_for(number, args)
                    n += 1
            else:
                time.sleep(0.001)

    def _setup_input_matrix(self, cip):
        input_matrix = [[None for __ in self.input_streams] for k in range(self.size())]
        for i, is_ in enumerate(self.input_streams):
            if is_.size() == 1:
                for ii in range(self.size()):
                    input_matrix[ii][i] = cip[i]
        return input_matrix

    def _check_for_any_new_data(self):
        for stream in self.input_streams:
            if stream.size() > 1:
                if not stream.empty(listener=self):
                    return True
        return False

    def _assemble_function_arguments(self, input_matrix, seen):
        for i, stream in enumerate(self.input_streams):
            if not stream.empty(listener=self):
                item = stream.get(listener=self)
                input_matrix[item.number][i] = item

        for ni, arg in enumerate(input_matrix):
            if ni not in seen:
                if all(c is not None for c in arg):
                    yield ni, arg
                    seen.add(ni)


def create_decorator(clz, debug, run_local):
    def decorator(inner):
        @functools.wraps(inner)
        def wrapped(*args):
            return clz(inner, args, debug=debug, run_local=run_local)
        wrapped.inner = inner
        return wrapped
    return decorator


apply = create_decorator(ZipComputation, False, False)
apply_local = create_decorator(ZipComputation, False, True)
apply_debug = create_decorator(ZipComputation, True, False)

join = create_decorator(JoinComputation, False, False)
join_local = create_decorator(JoinComputation, False, True)
join_debug = create_decorator(JoinComputation, True, False)

summarize = create_decorator(SummarizeComputation, False, False)
summarize_local = create_decorator(SummarizeComputation, False, True)
summarize_debug = create_decorator(SummarizeComputation, True, False)

fullstream = create_decorator(FullStreamComputation, False, False)
fullstream_local = create_decorator(FullStreamComputation, False, True)
fullstream_debug = create_decorator(FullStreamComputation, True, False)


def source(inner):
    @functools.wraps(inner)
    def wrapped(*args):
        return ComputedSource(inner, args)
    wrapped.inner = inner
    return wrapped


def output(inner):
    if isinstance(inner, (Computation)):
        return OutputNode(inner)

    @functools.wraps(inner)
    def wrapped(*args):
        return OutputNode(inner(*args))
    wrapped.inner = inner
    return wrapped


if __name__ == "__main__":

    @join
    def add(*args):
        time.sleep(0.5 * random.random())
        return sum(args)

    @apply
    def inc(x, config=dict()):
        time.sleep(0.5 * random.random())
        return x + config.get("increment", 1)

    @summarize
    def avg(values):
        return float(sum(values)) / len(values)

    Engine.set_number_of_processes(7)
    N = 3

    s1 = range(N)
    s2 = range(1, N + 1)
    r = add(0, 1, s1)

    r = inc(avg(inc(add(0, 1, add(inc(s1), inc(s2), inc(7))), dict(increment=2))))

    r = output(r)
    r.start_computations()

    print(sorted(r.get_all_in_order()))
