import pdb
# encoding: utf-8

import os
import hashlib
import weakref

import dill

import multiprocessing

from .std_logger import get_logger


class CacheItem(object):

    def __init__(self, name, path, value, loaded, hash_code):
        self.path = path
        self.loaded = loaded
        self.name = name
        self.hash_code = hash_code
        self.set_value(value)

    def set_value(self, value):
        self.value = value
        if value is not None:
            self.class_name = str(value.__class__)
            self.loaded = True
        else:
            self.class_name = None

    def __str__(self):
        return "<CacheItem name=%s path=%s value=%r loaded=%s hash_code=%s>" % (
                self.name, self.path, self.value, self.loaded, self.hash_code)


class _CacheBuilder(object):

    def __init__(self, root_dir=None):
        self.root_dir = root_dir
        self.reset_handlers()

    def reset_handlers(self):
        self._type_handlers = list()

    def register_handler(self, type_, hash_data_source, file_extension, load_function,
                               save_function, info_getter):
        self._type_handlers.append((type_,
                                    self._pickler(hash_data_source),
                                    file_extension,
                                    self._pickler(load_function),
                                    self._pickler(save_function),
                                    self._pickler(info_getter),
                                    )
                                   )

    def _setup_folder(self, function):
        folder = function.__name__
        if self.root_dir is not None:
            folder = os.path.join(self.root_dir, folder)
        return folder

    def _lookup_load_function_for(self, ext):
        for (__, __, ext_i, load_function, __, __) in self._type_handlers:
            if ext == ext_i:
                return self._unpickler(load_function)
        return None

    def load(self, item):
        assert isinstance(item, CacheItem)

        __, f_ext = os.path.splitext(item.path)
        load_function = self._lookup_load_function_for(f_ext)
        if load_function is not None:
            obj = load_function(item.path)
        else:
            obj = dill.load(open(item.path, "rb"))

        item.set_value(obj)
        return obj

    def __call__(self, function):
        folder = self._setup_folder(function)
        cache, lock, counter, handlers = self._setup_cache_internals()

        clz = self._cache_function_class()
        c = clz(function, folder, lock, cache, counter, handlers, self._pickler, self._unpickler)
        return c

    def _cache_function_class(self):
        return _CachedFunction


class CacheBuilder(_CacheBuilder):

    def __init__(self, root_dir=None):
        super(CacheBuilder, self).__init__(root_dir)
        self._pickler = dill.dumps
        self._unpickler = dill.loads
        self._manager = multiprocessing.Manager()

        # shutdown manager if object is deleted, this has less impact to garbage collector
        # than implementing __del__:
        def on_die(ref, manager=self._manager, logger=get_logger()):
            logger.info("try to shutdown multiprocessings manager process")
            manager.shutdown()
            logger.info("finished shutdown multiprocessings manager process")
        self._del_ref = weakref.ref(self, on_die)

    def _setup_cache_internals(self):
        cache = self._manager.dict()
        lock = self._manager.Lock()
        counter = self._manager.Value('d', 0)
        handlers = self._manager.list(self._type_handlers)
        return cache, lock, counter, handlers


class LazyCacheBuilder(CacheBuilder):

    def _cache_function_class(self):
        return _LazyCachedFunction


class LocalCounter(object):

    def __init__(self):
        self.value = 0


class NoOpContextManager(object):

    def __enter__(self, *a, **kw):
        pass

    __exit__ = __enter__


class LocalCacheBuilder(_CacheBuilder):

    """Cache which only resists in current process, can not be used with pacerd distributed
    computation capabilities ! Use CacheBuilder instead.
    """

    def __init__(self, root_dir=None):
        super(LocalCacheBuilder, self).__init__(root_dir)
        self._manager = None
        self._pickler = self._unpickler = lambda o: o

    def _setup_cache_internals(self):
        cache = dict()
        lock = NoOpContextManager()
        counter = LocalCounter()
        handlers = list(self._type_handlers)
        return cache, lock, counter, handlers


class _CachedFunction(object):

    """ Instances of this class can be used to decorate function calls for caching their
    results, even if the functions are executed across different processes started by Python
    multiprocessing modules Pool class.

    The cache is backed up on disk, so that cache entries are persisted over different
    runs.
    """

    def __init__(self, function, folder, _lock, _cache, _counter, _handlers, _pickler, _unpickler):

        self.function = function
        self.__name__ = function.__name__
        self.folder = folder

        self._cache = _cache
        self._lock = _lock
        self._hit_counter = _counter
        self._type_handlers = _handlers

        self._pickler = _pickler
        self._unpickler = _unpickler

        self._logger = get_logger(self)
        self._setup_cache()

    def __getstate__(self):
        dd = self.__dict__.copy()
        if "_logger" in dd:
            del dd["_logger"]
        return dd

    def __setstate__(self, dd):
        self.__dict__.update(dd)
        self._logger = get_logger(self)

    def reset_handlers(self):
        del self._type_handlers[:]

    def register_handler(self, type_, hash_data_source, file_extension, load_function,
                               save_function, info_getter):

        self._type_handlers.append((type_,
                                    self._pickler(hash_data_source),
                                    file_extension,
                                    self._pickler(load_function),
                                    self._pickler(save_function),
                                    self._pickler(info_getter),
                                    )
                                   )

    def _lookup_for_type_of(self, obj):
        for row in self._type_handlers:
            if isinstance(obj, row[0]):
                return row
        nonf = self._pickler(None)
        return [None, nonf, None, nonf, nonf, nonf, nonf]

    def _lookup_hash_data_extractor_for(self, key):
        return self._unpickler(self._lookup_for_type_of(key)[1])

    def _lookup_load_function_for(self, ext):
        for (__, __, ext_i, load_function, __, __) in self._type_handlers:
            if ext == ext_i:
                return self._unpickler(load_function)
        return None

    def _lookup_ext_and_save_function_for(self, what):
        row = self._lookup_for_type_of(what)
        return row[2], self._unpickler(row[4])

    def _lookup_info_getter(self, what):
        row = self._lookup_for_type_of(what)
        return self._unpickler(row[5])

    def get_number_of_hits(self):
        return self._hit_counter.value

    def _setup_cache(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        for file_name in os.listdir(self.folder):
            stem, ext = os.path.splitext(file_name)
            if ext == ".cache_meta_file":
                with open(os.path.join(self.folder, file_name)) as fp:
                    item = dill.load(fp)
                    self._cache[item.hash_code] = item

    def clear(self):
        self._cache.clear()

    def _compute_hash(self, key, outer=None):
        if isinstance(key, CacheItem):
            return key.hash_code
        extractor = self._lookup_hash_data_extractor_for(key)
        if extractor is not None:
            key = extractor(key)
        if isinstance(key, str):
            data = key
        elif isinstance(key, unicode):
            data = key.encode("utf-8")
        elif hasattr(key, "__dict__"):
            data = self._compute_hash(key.__dict__, outer=key)
        elif isinstance(key, (bool, int, long, float,)):
            data = str(self._pickler(key))
        elif key is None:
            data = "__None__"
        elif isinstance(key, (tuple, list)):
            data = "".join(self._compute_hash(item, outer=key) for item in key)
        elif isinstance(key, set):
            data = "".join(self._compute_hash(item, outer=key) for item in sorted(key))
        elif isinstance(key, dict):
            data = "".join(self._compute_hash(item, outer=key) for item in key.items())
        else:
            raise Exception("can not compute hash for %r contained in %r" % (key, outer))
        if not isinstance(data, basestring):
            raise RuntimeError("implementation error: data should be str, but is %s" % type(data))
        muncher = hashlib.sha1()
        muncher.update(data)
        return muncher.hexdigest()

    def _contains(self, hash_code):
        return hash_code in self._cache.keys()

    def _get(self, hash_code):
        item = self._cache[hash_code]
        if not item.loaded:
            value = self._load(item.path)
            item.value = value
            item.loaded = True
        self._cache[hash_code] = item
        return item.value

    def _put(self, name, hash_code_args, args, result):
        item = self._store(name, result, hash_code_args)
        self._cache[hash_code_args] = item
        return item

    def _load(self, path):
        __, f_ext = os.path.splitext(path)
        load_function = self._lookup_load_function_for(f_ext)
        if load_function is not None:
            obj = load_function(path)
        else:
            obj = dill.load(open(path, "rb"))
        self._logger.info("loaded %s" % path)
        return obj

    def _store(self, name, what, hashcode_fingerprint):
        ext, save_function = self._lookup_ext_and_save_function_for(what)

        if ext is None or save_function is None:
            ext = ".pickled"
            def save_function(what, path):
                with open(path, "wb") as fp:
                    dill.dump(what, fp)
        path = os.path.join(self.folder, hashcode_fingerprint + ext)
        if not os.path.exists(path):
            save_function(what, path)
            self._logger.info("stored %s" % path)
        else:
            self._logger.info("no need to store item to %s" % path)

        item = CacheItem(name, path, None, False, hashcode_fingerprint)
        path = os.path.join(self.folder, hashcode_fingerprint + ".cache_meta_file")
        if not os.path.exists(path):
            with open(path, "w") as fp:
                dill.dump(item, fp)
        return item

    def _get_names(self, args):
        for arg in args:
            if isinstance(arg, CacheItem):
                yield arg.name
            else:
                getter = self._lookup_info_getter(arg)
                if getter is not None:
                    yield getter(arg)

    def cached_call(self, args, kw):
        all_args = args + tuple(sorted(kw.items()))
        try:
            hash_code = self._compute_hash(all_args)
        except RuntimeError:
            raise Exception("could not compute hash for %r. maybe you should register your own "
                            "handler" % (all_args,))
        if self._contains(hash_code):
            with self._lock:
                self._hit_counter.value += 1
            self._logger.info("cache hit for %s" % hash_code)
            ci = self._get(hash_code)
            return ci, ci

        args = self.resolve_inputs(args)
        result = self.function(*args, **kw)
        self._logger.info("new result for %s" % hash_code)
        name = "--".join(a for a in self._get_names(args) if a is not None)
        if name == "":
            name = None
        item = self._put(name, hash_code, args, result)
        return result, item

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return result

    def resolve_inputs(self, i):
        return i


class _LazyCachedFunction(_CachedFunction):

    def _get(self, hash_code):
        item = self._cache[hash_code]
        return item

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return item

    def resolve_inputs(self, args):
        if isinstance(args, (tuple,)):
            args = tuple(self._load(a.path) if isinstance(a, CacheItem) else self.resolve_inputs(a) for a in args)
        if isinstance(args, (list,)):
            args = [self._load(a.path) if isinstance(a, CacheItem) else self.resolve_inputs(a) for a in args]
            return args
        if isinstance(args, CacheItem):
            return self._load(args.path)
        return args
