from sw_utils.profile import profiled, get_profiler, push_context, pop_context, configure, \
    profiler_log_handler_getter
from sw_utils.logs.log_handler import log_init_manual, log_trace, log_error
from sw_utils.storage import RedisStorage, LocalStorage, CachedStorage


cache_host = 'localhost'
cache_redis_db = 10
r_store = RedisStorage(host=cache_host, db=cache_redis_db)
l_store = LocalStorage()
c_store = CachedStorage(r_store, l_store)

# profiler = configure(True, c_store)
profiler = configure(True, r_store)
log_init_manual(
    appName='test_profile', home_dir="/tmp/",
    custom_handler_getter=profiler_log_handler_getter,
    aws=None, log_verb=0, log_lvl=15, log_host=None)


def no_context_test(*args):
    with(get_profiler()):
        with(get_profiler()):
            print 'hola'


def nested_contexting(*args):
    push_context('context0')
    push_context('context0_0')
    with(get_profiler()):
        with(get_profiler()):
            push_context('context0_1')
            pop_context()
    pop_context()
    pop_context()


def log_integration_test(*args):
    push_context('context2')
    log_trace('No debe aparecer')
    log_error('No debe aparecer')
    with(get_profiler()):
        log_error('Error MSG 1')
        log_trace('Trace MSG 1')
    pop_context()


def many_hits(*args):
    @profiled()
    def many_called_1():
        pass

    @profiled()
    def many_called_2():
        pass

    push_context('context4')
    many_called_2()
    many_called_1()
    many_called_2()
    many_called_1()
    many_called_2()
    pop_context()


no_context_test()
nested_contexting()
log_integration_test()
many_hits()

profiler.print_brief()

profiler.storage.flush()
