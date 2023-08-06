from .computation_engine import (apply, join, summarize, fullstream,
                                 apply_local, join_local, summarize_local, fullstream_local,
                                 apply_debug, join_debug, summarize_debug, fullstream_debug,
                                 source,
                                 Engine, output, DelayedException,
                                 Source,
                                 )

from .fs_cache import CacheBuilder, LocalCacheBuilder, LazyCacheBuilder, CacheItem

from .std_logger import get_logger

# DO NOT TOUCH THE FOLLOWING LINE:
import sys
if not getattr(sys, "frozen", False):
    import pkg_resources  # part of setuptools
    __version__ = tuple(map(int, pkg_resources.require(__name__)[0].version.split(".")))
else:
    __version__ = (0, 0, 0)
