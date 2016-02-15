import time
import pprint

from sw_utils.profile import profiled, get_profiler, push_context, pop_context, configure, \
    profiler_log_handler_getter
from sw_utils.logs.log_handler import log_init_manual, log_trace, log_error
from sw_utils.storage import LocalStorage


profiler = configure(True, LocalStorage())
log_init_manual(
    appName='test_profile', home_dir="/tmp/",
    custom_handler_getter=profiler_log_handler_getter,
    aws=None, log_verb=0, log_lvl=15, log_host=None)


@profiled()
def some_fun_1(*args):
    time.sleep(0.5)
    print "Hola"


@profiled()
def some_fun_2(*args):
    time.sleep(0.2)
    print "Hola que tal"


def no_context_test(*args):
    with(get_profiler()):
        with(get_profiler()):
            print 'hola'


def nested_contexting_test(*args):
    push_context('context0')
    push_context('context0_0')
    with(get_profiler()):
        with(get_profiler()):
            push_context('context0_1')
            pop_context()
    pop_context()
    pop_context()


def timing_test(*args):
    push_context('context1')
    with(get_profiler()):
        time.sleep(1)
        some_fun_2()
        with(get_profiler()):
            time.sleep(0.3)
            print "Adios dios dios"
            some_fun_2()
    pop_context()


def log_integration_test(*args):
    push_context('context2')
    log_trace('No debe aparecer')
    log_error('No debe aparecer')
    with(get_profiler()):
        log_error('Error MSG 1')
        log_trace('Trace MSG 1')
    pop_context()


def exception_test(*args):
    push_context('context3')
    try:
        try:
            with(get_profiler()):
                raise Exception("No se debe mostrar")
        except BaseException as e:
            print e
            log_error(e)
        with(get_profiler()):
            try:
                raise Exception("SI se debe mostrar")
            except BaseException as e:
                print e
                log_error(e)
        with(get_profiler()):
            raise Exception("No se debe mostrar")
    finally:
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


# def same_callid_test(*args):
#     push_context('context6')
#     with(get_profiler_mng(exec_id='snippet6')):
#         with(get_profiler_mng(exec_id='snippet6')):
#             print "Coso 6"
#     with(get_profiler_mng(exec_id='snippet6')):
#         print "Coso 6"
#     with(get_profiler_mng(exec_id='snippet_diff_6')):
#         print "Coso 6"
#     pop_context()


# def no_callid_test(*args):
#     push_context('context7')
#     with(get_profiler()):
#         with(get_profiler()):
#             print "Coso 7"
#     with(get_profiler()):
#         print "Coso 7"
#     pop_context()


# some_fun_1()
# some_fun_2()
many_hits()
no_context_test()
nested_contexting_test()
timing_test()
log_integration_test()
try:
    exception_test()
except BaseException as e:
    print e
# same_callid_test()
# no_callid_test()


s_key = ['context4',"(('__main__', 'many_called_1', 91), ('__main__', 'many_hits', 103))"]
all_p = profiler.filterResult(store_key=s_key)

avg_p = profiler.get_avg_time(store_key=s_key)
hits_p = profiler.get_hits(store_key=s_key)
med_p = profiler.get_mediana_time(store_key=s_key)
sum_p = profiler.get_sum_time(store_key=s_key)
profiler.print_brief(['context4'])
profiler.print_brief()

pprint.pprint(profiler.storage.data.data)
