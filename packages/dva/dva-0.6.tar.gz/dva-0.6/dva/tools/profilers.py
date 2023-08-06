import logging
logger = logging.getLogger(__name__)

def profiled(fn):
    def profiled_wrapper(*args, **kvs):
        import cProfile
        import pstats
        import os
        import tempfile
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            ret = fn(*args, **kvs)
        finally:
            profiler.disable()
            # for multiprocessing tracking, each process should have a separate file
            _, name = tempfile.mkstemp(prefix="profiler-%s-" % os.getpid(), suffix=".log")
            profiler.dump_stats(name)
        return ret
    return profiled_wrapper


def memprofiledCls(cls):
    '''
    memory profile a class
    dumps stats atexit
    '''
    def profiled_wrapper(*args, **kvs):
        '''
        wraps original class-definition callable
        '''
        from pympler.classtracker import ClassTracker
        import atexit

        tracker = ClassTracker()
        tracker.track_class(cls)

        # monkeypatch the original class __setattr__
        # to take mem usage snapshots at setting attributes
        original_setattr = cls.__setattr__
        def __setattr__(self, attrname, value):
            '''
            snapshot mem usage at attrname access
            '''
            try:
                tracker.create_snapshot(attrname)
            except Exception as e:
                pass
            return original_setattr(self, attrname, value)

        cls.__setattr__ = __setattr__

        def dump_stats_atexit():
            '''
            dumps mem stats at program exit for each process separately
            '''
            import os
            import tempfile
            _, name = tempfile.mkstemp(prefix="mem-%s-%s-" % (cls.__name__, os.getpid()), suffix=".log")
            tracker.stats.dump_stats(name)

        # register the stats dumping
        atexit.register(dump_stats_atexit)
        # back to class instantiation
        return cls(*args, **kvs)
    return profiled_wrapper


