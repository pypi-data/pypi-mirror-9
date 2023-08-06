# encoding: utf-8

import glob
import hashlib
import os
import weakref

import dill

import multiprocessing

from .std_logger import get_logger


def _fallback_save_function():
    ext = ".pickled"

    def save_function(what, path):
        with open(path, "wb") as fp:
            dill.dump(what, fp)
    return ext, save_function


def _fallback_load_function():

    def load_function(path):
        with open(path, "rb") as fp:
            return dill.load(fp)
    return load_function


class CacheItem(object):

    def __init__(self, meta, hash_code, tr):
        self.meta = meta
        self.hash_code = hash_code
        self.tr = tr
        self.path = None
        self.loaded = False
        self.value = None

    def __str__(self):
        return "<CachedItem meta=%s path=%s value=%r loaded=%s hash_code=%s>" % (
            self.meta, self.path, self.value, self.loaded, self.hash_code)

    def load(self):
        __, f_ext = os.path.splitext(self.path)
        load_function = self.tr.lookup_load_function_for(f_ext)
        if load_function is None:
            load_function = _fallback_load_function()
        obj = load_function(self.path)
        return obj


class CacheListItem(CacheItem):

    def __init__(self, meta, hash_code, tr):
        super(CacheListItem, self).__init__(meta, hash_code, tr)
        self.sub_items = []

    def __str__(self):
        return "<CacheListItem meta=%s path=%s value=%r loaded=%s hash_code=%s>" % (
            self.meta, self.path, self.value, self.loaded, self.hash_code)

    def save(self, what, path):
        self.sub_items = []
        for i, item in enumerate(what):
            ext, save_function = self.tr.lookup_ext_and_save_function_for(item)
            if ext is None or save_function is None:
                ext, save_function = _fallback_save_function()
            full_path = path + "_%d" % i + ext
            save_function(item, full_path)
            hash_code = self.tr.compute_hash(item)
            sub_item = CacheItem(self.meta, hash_code, self.tr)
            sub_item.path = full_path
            self.sub_items.append(sub_item)
        self.path = path

    def load(self):
        items = []
        for p in glob.glob(self.path + "_*.*"):
            __, f_ext = os.path.splitext(p)
            load_function = self.tr.lookup_load_function_for(f_ext)
            if load_function is None:
                load_function = _fallback_load_function()
            obj = load_function(p)
            items.append(obj)
        return items

    def __iter__(self):
        return iter(self.sub_items)



class CacheDictItem(CacheItem):

    def __str__(self):
        return "<CacheDictItem meta=%s path=%s value=%r loaded=%s hash_code=%s>" % (
            self.meta, self.path, self.value, self.loaded, self.hash_code)

    def save(self, what, path):
        def save(what, identifier):
            ext, save_function = self.tr.lookup_ext_and_save_function_for(what)
            if ext is None or save_function is None:
                ext, save_function = _fallback_save_function()
            full_path = path + "_%s_%d" % (identifier, i) + ext
            save_function(what, full_path)
        for i, (key, value) in enumerate(what.items()):
            save(key, "key")
            save(value, "value")
        self.path = path

    def load(self):
        items = []

        def load(path):
            __, f_ext = os.path.splitext(os.path.basename(path))
            load_function = self.tr.lookup_load_function_for(f_ext)
            if load_function is None:
                load_function = _fallback_load_function()
            obj = load_function(path)
            return obj

        keys = {}
        values = {}
        for p in glob.glob(self.path + "_*.*"):
            stem, identifier, __ = os.path.basename(p).split("_")
            obj = load(p)
            if identifier == "key":
                keys[stem] = obj
            elif identifier == "value":
                values[stem] = obj
            else:
                raise Exception("have no idea how to read %s" % p)
        assert set(keys.iterkeys()) == set(values.iterkeys()), "invalid chache state"
        items = {}
        for stem in keys.iterkeys():
            key = keys[stem]
            value = values[stem]
            items[key] = value
        return items


class DistributedTypeRegistry(object):

    def __init__(self):
        self._pickler = dill.dumps
        self._unpickler = dill.loads
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

    def lookup_load_function_for(self, ext):
        for (__, __, ext_i, load_function, __, __) in self._type_handlers:
            if ext == ext_i:
                return self._unpickler(load_function)
        return None

    def _lookup_for_type_of(self, obj):
        for row in self._type_handlers:
            if isinstance(obj, row[0]):
                return row
        nonf = self._pickler(None)
        return [None, nonf, None, nonf, nonf, nonf, nonf]

    def lookup_hash_data_extractor_for(self, key):
        return self._unpickler(self._lookup_for_type_of(key)[1])

    def lookup_ext_and_save_function_for(self, what):
        row = self._lookup_for_type_of(what)

        ext = row[2]
        save_function = self._unpickler(row[4])

        return ext, save_function

    def lookup_info_getter(self, what):
        row = self._lookup_for_type_of(what)
        return self._unpickler(row[5])

    def compute_hash(self, key, outer=None):
        if isinstance(key, CacheItem):
            return key.hash_code
        extractor = self.lookup_hash_data_extractor_for(key)
        if extractor is not None:
            key = extractor(key)
        if isinstance(key, str):
            data = key
        elif isinstance(key, unicode):
            data = key.encode("utf-8")
        elif hasattr(key, "__dict__"):
            data = self.compute_hash(key.__dict__, outer=key)
        elif isinstance(key, (bool, int, long, float,)):
            data = str(dill.dumps(key))
        elif key is None:
            data = "__None__"
        elif isinstance(key, (tuple, list)):
            data = "".join(self.compute_hash(item, outer=key) for item in key)
        elif isinstance(key, set):
            data = "".join(self.compute_hash(item, outer=key) for item in sorted(key))
        elif isinstance(key, dict):
            data = "".join(self.compute_hash(item, outer=key) for item in key.items())
        else:
            raise Exception("can not compute hash for %r contained in %r" % (key, outer))
        if not isinstance(data, basestring):
            raise RuntimeError("implementation error: data should be str, but is %s" % type(data))
        muncher = hashlib.sha1()
        muncher.update(data)
        return muncher.hexdigest()


class LocalTypeRegistry(DistributedTypeRegistry):

    def __init__(self):
        noop = lambda x: x
        self._pickler = noop
        self._unpickler = noop
        self.reset_handlers()


class _CacheBuilder(object):

    def __init__(self, root_dir=None):
        self.root_dir = root_dir

    def register_handler(self, *a, **kw):
        self.tr.register_handler(*a, **kw)

    def _setup_folder(self, function):
        folder = function.__name__
        if self.root_dir is not None:
            folder = os.path.join(self.root_dir, folder)
        return folder

    def __call__(self, function):
        folder = self._setup_folder(function)
        cache, lock, counter = self._setup_cache_internals()

        clz = self._cache_function_class()
        c = clz(function, folder, lock, cache, counter, self.tr)
        return c

    def _cache_function_class(self):
        return _CachedFunction


class CacheBuilder(_CacheBuilder):

    def __init__(self, root_dir=None):
        super(CacheBuilder, self).__init__(root_dir)
        self.tr = DistributedTypeRegistry()
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
        return cache, lock, counter

    def __str__(self):
        return "<CacheBuilder(%s)>" % self.root_dir


class LazyCacheBuilder(CacheBuilder):

    def _cache_function_class(self):
        return _LazyCachedFunction

    def __str__(self):
        return "<LazyCacheBuilder(%s)>" % self.root_dir


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
        self.tr = LocalTypeRegistry()
        self._manager = None

    def _setup_cache_internals(self):
        cache = dict()
        lock = NoOpContextManager()
        counter = LocalCounter()
        #handlers = list(self._type_handlers)
        return cache, lock, counter  # , handlers

    def __str__(self):
        return "<LocalCacheBuilder(%s)>" % self.root_dir


class _CachedFunction(object):

    """ Instances of this class can be used to decorate function calls for caching their
    results, even if the functions are executed across different processes started by Python
    multiprocessing modules Pool class.

    The cache is backed up on disk, so that cache entries are persisted over different
    runs.
    """

    def __init__(self, function, folder, _lock, _cache, _counter, tr):

        self.function = function
        self.__name__ = function.__name__
        self.folder = folder

        self._cache = _cache
        self._lock = _lock
        self._hit_counter = _counter

        self.tr = tr

        self._logger = get_logger(self)
        self._setup_cache()

    def __getstate__(self):
        dd = self.__dict__.copy()
        if "_logger" in dd:
            del dd["_logger"]
        return dd

    def register_handler(self, *a, **kw):
        self.tr.register_handler(*a, **kw)

    def __setstate__(self, dd):
        self.__dict__.update(dd)
        self._logger = get_logger(self)

    def get_number_of_hits(self):
        return self._hit_counter.value

    def _setup_cache(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        for file_name in os.listdir(self.folder):
            stem, ext = os.path.splitext(file_name)
            if ext == ".cache_meta_file":
                with open(os.path.join(self.folder, file_name), "rb") as fp:
                    item = dill.load(fp)
                    self._cache[item.hash_code] = item

    def clear(self):
        self._cache.clear()


    def _contains(self, hash_code):
        return hash_code in self._cache.keys()

    def _get(self, hash_code):
        item = self._cache[hash_code]
        if not item.loaded:
            value = item.load()
            item.value = value
            item.loaded = True
        self._cache[hash_code] = item
        return item.value

    def _put(self, name, hash_code_args, args, result):
        """
        if isinstance(result, (list)):
            item = [self._put(name, hash_code + "_%d" % i, args, item) for (i, item) in
                    enumerate(result)]
        """
        item = self._store(name, result, hash_code_args)
        self._cache[hash_code_args] = item
        return item

    def _store(self, name, what, hashcode_args):

        meta = dict(name=name)

        if isinstance(what, list):
            item = CacheListItem(meta, hashcode_args, self.tr)
            save_function = item.save
            ext = ""
        elif isinstance(what, dict):
            item = CacheDictItem(meta, hashcode_args, self.tr)
            save_function = item.save
            ext = ""
        else:
            item = CacheItem(meta, hashcode_args, self.tr)
            ext, save_function = self.tr.lookup_ext_and_save_function_for(what)
            if ext is None or save_function is None:
                ext, save_function = _fallback_save_function()

        path = os.path.join(self.folder, hashcode_args + ext)
        item.path = path

        if not os.path.exists(path):
            save_function(what, path)
            self._logger.info("stored %s" % path)
        else:
            self._logger.info("no need to store item to %s" % path)

        self._write_meta(hashcode_args, item)
        return item

    def _write_meta(self, hashcode_args, item):
        path = os.path.join(self.folder, hashcode_args + ".cache_meta_file")
        if not os.path.exists(path):
            with open(path, "wb") as fp:
                dill.dump(item, fp)
        return item

    def _get_names(self, args):
        for arg in args:
            if isinstance(arg, CacheItem):
                yield arg.name
            else:
                getter = self.tr.lookup_info_getter(arg)
                if getter is not None:
                    yield getter(arg)

    def cached_call(self, args, kw):
        all_args = args + tuple(sorted(kw.items()))
        try:
            hash_code = self.tr.compute_hash(all_args)
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

    """
    TODO: CacheItemContainer.

        1. wird von _put erzeugt wenn "enabled" und argument ist liste
        2. items werde in order geschrieben (ein meta eintrag, mehrere subitems / pathes !?)
        3. beim cache laden werden diese items erkannt
        4. bei cache hit 


        auf disk: meta hat mehrere pathes
        laden:    ein cacheitem mit mehreren pathes
        bei hit:  aus einem item wird liste von cache items erzeugt
                  (_get)
        put:      tuple/liste erkannt, mehrere pathes werden ezreugt

    TODO:
        @fullstream(cache) etc !


    strategie:

        1. bestehdend datenfluss fuer lazy cache aufdröseln / hinschreiben
        2. modifikationen bestimmen

    """

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return result

    def resolve_inputs(self, i):
        return i

    def __str__(self):
        return "<_CachedFunction(%s)>" % self.function.__name__


class _LazyCachedFunction(_CachedFunction):

    def _get(self, hash_code):
        item = self._cache[hash_code]
        # item ist multiple + modues is "beak lists" ?
        # aufliösen zu liste von cacheitems
        return item

    def __call__(self, *args, **kw):
        result, item = self.cached_call(args, kw)
        return item

    def __str__(self):
        return "<_LazyCachedFunction(%s)>" % self.function.__name__

    def resolve_inputs(self, args):
        if isinstance(args, (list, tuple)):
            loaded = [a.load() if isinstance(a, CacheItem) else self.resolve_inputs(a) for a in args]
            if isinstance(args, (tuple,)):
                loaded = tuple(loaded)
            return loaded
        if isinstance(args, CacheItem):
            return args.load()
        return args
