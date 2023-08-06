import multiprocessing
import dill

"""
This module is a non complete replacement for pythons multiprocessing module.
The existing multiprocessing module is restricted for remote execution of eg lambda functions,
decorated functions and static member functions.

We use dill for pickling instead of cPickle for transfering function code, arguments
and results.
"""


def dill_apply(fun_s, args_s, kwargs_s=None):
    """
    this function is executed in a separate process and decodes the input string
    into a functino and its args.
    """
    try:
        fun = dill.loads(fun_s)
        args = dill.loads(args_s)
        if kwargs_s is not None:
            kwargs = dill.loads(kwargs_s)
        else:
            kwargs = dict()
        res = fun(*args, **kwargs)
        return dill.dumps(res)
    except:
        import traceback
        traceback.print_exc()
        raise


class AsyncResult(object):

    def __init__(self, job):
        self.job = job

    def get(self):
        return dill.loads(self.job.get())


class SyncResult(object):

    def __init__(self, fun, args):
        self.fun = fun
        self.args = args
        self.res = self.fun(*self.args)

    def get(self):
        return self.res


class Pool(object):

    def __init__(self, n):
        self.n = n
        if self.n > 0:
            self.pool = multiprocessing.Pool(n)

    def apply_async(self, fun, args, kwargs=None):
        if self.n == 0:
            return SyncResult(fun, args)
        try:
            fun_c = dill.dumps(fun)
        except dill.PicklingError, e:
            raise Exception("%s\ndill failed to  pickle %s" % (e, fun))
        try:
            args_c = dill.dumps(args)
        except dill.PicklingError, e:
            raise Exception("%s\ndill failed to  pickle %s" % (e, args))
        kwargs_c = None
        if kwargs is not None:
            try:
                kwargs_c = dill.dumps(kwargs)
            except dill.PicklingError, e:
                raise Exception("%s\ndill failed to  pickle %s" % (e, kwargs))
        job = self.pool.apply_async(dill_apply, (fun_c, args_c, kwargs_c))
        return AsyncResult(job)
