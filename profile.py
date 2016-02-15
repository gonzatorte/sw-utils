import inspect, traceback
# import pdb
import StringIO
import os, sys
import threading
from django.utils import importlib
from sw_utils.dummy_obj import DummyObj
from sw_utils.std_capture import configure as configure_capture, desconfigure as desconfigure_capture, \
    get_capture, get_capture_mng, start_capture, stop_capture
import logging
import re


t_data = threading.local()
enable = False
_is_inited = False


def configure(enable_in, storage_obj):
    thismodule = sys.modules[__name__]
    if not thismodule._is_inited:
        thismodule._is_inited = True
        thismodule.enable = enable_in

        configure_capture()

        pp = getattr(thismodule.t_data, 'profiler', None)
        if pp is None:
            pp = Profiler(storage_obj)
            thismodule.t_data.profiler = pp
            Profiler.admin_time = calibrate(lvl=5)
        return pp
    else:
        return None


def desconfigure():
    thismodule = sys.modules[__name__]
    thismodule.t_data = threading.local()
    thismodule.enable = False
    thismodule._is_inited = False
    desconfigure_capture()


def django_configure():
    # pdb.set_trace()
    thismodule = sys.modules[__name__]
    if not thismodule._is_inited:
        from django.conf import settings
        PROFILING_SETTINGS = getattr(settings, 'PROFILING_SETTINGS', None)
        thismodule.enable = PROFILING_SETTINGS and PROFILING_SETTINGS['ENABLED']

        if not thismodule.enable:
            return DummyObj()

        #ToDo: Usar un diccionario mas complejo para habilitar/des captura, profundidad,
        # parametros del storage (StoreInstanceId, si hay concurrencia sobre el store), host, etc
        # si calibrar o no, cuanto calibrar...
        try:
            storage_module_obj_name = PROFILING_SETTINGS['BACKEND']
            storage_options = PROFILING_SETTINGS['BACKEND_OPTIONS']
            storage_module_name = '.'.join(storage_module_obj_name.split('.')[:-1])
            storage_obj_name = storage_module_obj_name.split('.')[-1]
            storage_module = importlib.import_module(storage_module_name)
            storage_cls = getattr(storage_module, storage_obj_name, None)
            if storage_cls is None:
                raise Exception
            storage = storage_cls(**storage_options)

            pp = configure(enable, storage)
            thismodule._is_inited = True
            return pp
        except BaseException as e:
            print "Error al inicializar profiling"
            print e
            thismodule.enable = False
            return DummyObj()
    else:
        return DummyObj()


class MemLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def handleError(self, record):
        pass


def profiler_log_handler_getter(logger):
    # pdb.set_trace()
    thismodule = sys.modules[__name__]
    if thismodule.enable and thismodule._is_inited:
        p = get_profiler()
        lh = MemLogHandler()
        p.log_handler_output = lh
        return lh
    return None


def get_profiler(activated=True):
    thismodule = sys.modules[__name__]
    if activated and thismodule.enable and thismodule._is_inited:
        pp = thismodule.t_data.profiler
        return pp
    else:
        pp = DummyObj()
        return pp


# ToDo: Lograr que el pop se haga automatico...
# contador de contextos agregados, y que se descarte siempre las cosas de mas alla de la prof
# un tercer tipo de stack, ni exec_id ni context...
# def get_profiler_mng(context, activated=True):
#     thismodule = sys.modules[__name__]
#     if activated and thismodule.enable and thismodule._is_inited:
#         pp = thismodule.t_data.profiler
#         pp.push_context(context)
#         return pp
#     else:
#         pp = DummyObj()
#         return pp


def get_exec_id_here(deep=1):
    frame = sys._getframe(deep)
    fn, lno, func_name, _, _ = inspect.getframeinfo(frame, 0)
    fun_name = func_name
    mod_name = frame.f_globals["__name__"]
    # stack_trace = traceback.extract_stack(f=frame, limit=10)[-3:-1]
    # the_module = frame.f_locals["__name__"]
    # try:
    #     the_class = frame.f_locals["self"].__class__
    #     the_class = str(the_class).split(".")[-1]
    # except KeyError:
    #     the_class = "<no class>"
    # code = frame.f_code
    return mod_name, fun_name, lno


def start_profiling(exec_id=None):
    if exec_id is None:
        call_id = get_exec_id_here(2)
        exec_id = (call_id, call_id)
    return get_profiler()._profile_start(exec_id)


def stop_profiling():
    return get_profiler()._profile_end()


def push_context(context):
    thismodule = sys.modules[__name__]
    if thismodule.enable and thismodule._is_inited:
        pp = thismodule.t_data.profiler
        pp.push_context(context)


def pop_context():
    thismodule = sys.modules[__name__]
    if thismodule.enable and thismodule._is_inited:
        pp = thismodule.t_data.profiler
        return pp.pop_context()


def calibrate(lvl):
    #ToDo: Quizas no calibrar todas las veces, sino que para la instancia sacar la estadistica anteriro...
    sum_admin_t = 0.0
    @profiled()
    def dummy_fun():
        for ii in xrange(1,10):
            pass
            # print ("DummyCalibrate <%s> ... Very large output for capture" % ii)
    for i in xrange(lvl):
        ini_admin_t = os.times()
        #ToDo
        #Usar un urandom (en ese caso recordar borrarlo para no dejar basura) o la id de la instancia para no interferir
        # en el proc de calibracion por cada vez... ni consigo mismo en varias exec...
        push_context('dummy_calibrate_context_1')
        start_profiling()
        dummy_fun()
        with(get_profiler()):
            dummy_fun()
            pass
        stop_profiling()
        pop_context()
        get_profiler().storage.flush()
        end_admin_t = os.times()
        [utime, stime, ch_utime, ch_stime, etime] = map(lambda x,y: x-y, end_admin_t, ini_admin_t)
        sum_admin_t += etime
    avg_admin_t = sum_admin_t/float(2*lvl)
    # ToDo: borrar la entrada de calibracion...
    # get_profiler().reset_context('dummy_calibrate_context_1')
    return avg_admin_t


class Profiler:
    admin_time = 0.0

    def __init__(self, storage):
        self.stats_stack = []
        self.execs_id_stack = []
        self.context_stack = []
        self.deep = 0
        self.storage = storage
        self.log_handler_output = None
        self.log_handler_output_stack = []

    def __enter__(self):
        call_id = get_exec_id_here(2)
        exec_id = (call_id, call_id)
        self._profile_start(exec_id=exec_id)

    def __exit__(self, exc_type, exc_val, exc_tb, *args, **kwargs):
        self._profile_end()

    def push_context(self, context):
        self.context_stack.append(context)
        return self

    def pop_context(self):
        self.context_stack.pop()
        return self

    def reset_context(self, context):
        self.storage.set(context, None)

    def _start_capture(self):
        start_capture(StringIO.StringIO(), StringIO.StringIO())

    def _end_capture(self):
        c = get_capture()
        dst_out = c.curr_out
        dst_err = c.curr_err
        stop_capture()
        dst_out.seek(0)
        stdout_capture = dst_out.read()
        dst_err.seek(0)
        stderr_capture = dst_err.read()
        return (stdout_capture, stderr_capture)

    def _start_log_capture(self):
        if self.log_handler_output:
            self.log_handler_output_stack.append(self.log_handler_output.records)
            self.log_handler_output.records = []

    def _end_log_capture(self):
        log_capture = []
        if self.log_handler_output:
            log_capture = map(lambda x: str(x), self.log_handler_output.records)
            self.log_handler_output.records = self.log_handler_output_stack.pop()
        return log_capture

    def _profile_start(self, exec_id):
        self.deep += 1
        self.execs_id_stack.append("%s" % (exec_id,))

        #ToDo: Dejar esto como configurable
        # self._start_capture()
        # self._start_log_capture()

        ini_t = os.times()
        self.stats_stack.append(ini_t)
        return self

    def _profile_end(self, extra_data=None):
        extra_data_list = []
        if extra_data is not None:
            extra_data_list = [extra_data]
        self.deep -= 1
        fin_t = os.times()

        #ToDo: Dejar esto como configurable
        # stdout_capture, stderr_capture = self._end_capture()
        # log_capture = self._end_log_capture()
        stdout_capture, stderr_capture = ('', '')
        log_capture = []
        captures = (stdout_capture, stderr_capture, log_capture)

        ini_t = self.stats_stack.pop()
        [utime, stime, ch_utime, ch_stime, etime] = map(lambda x,y: x-y, fin_t, ini_t)

        if etime < self.admin_time:
            etime = -1
        else:
            etime -= self.admin_time

        self._process_result(etime, captures, *extra_data_list)

        _ = self.execs_id_stack.pop()
        return self

    def _profiler_update_storage(self, val, *args):
        etime_ = args[0]
        capture = args[1]
        extra_data_ = args[2:]
        if val is None:
            val = {'execs': []}

        # exec_info = {'etimes': etime_, 'capture': capture}
        # if len(extra_data_) > 0:
        #     exec_info['extra'] = extra_data_
        #
        # if not val.has_key('execs'):
        #     val['execs'] = []
        # val['execs'].append(exec_info)

        if not val.has_key('hits'):
            val['hits'] = 0
        val['hits'] += 1

        if not val.has_key('sum'):
            val['sum'] = 0
        if etime_ > 0:
            val['sum'] += etime_

        return val

    def _process_result(self, etime, capture, *extra_data_list):
        # ToDo: meterle algo antes a los contextos o a los exec_ids para saber que son distintos...
        # context = self.context_stack + self.execs_id_stack
        # context = self.execs_id_stack
        # context = [self.execs_id_stack[-1]]
        context = self.context_stack[:]
        context.append(self.execs_id_stack[-1])

        self.storage.update(context, self._profiler_update_storage, etime, capture, *extra_data_list)

    def filterResult(self, **kwargs):

        # #Retornar solo las agregaciones de todos los que matchean esto
        # aggregations = mib.like(exec_id_pattern)
        # O?
        # #Retornar los primeros hijos mib del padre mib
        # mibs = mib.like(exec_id_pattern)

        result = []
        try:
            store_key = kwargs['store_key']
            val = self.storage.get(store_key)
            if val is not None:
                result.append(val)
        except KeyError:
            # r.keys_where(lambda x: True)
            # result.append(self.storage.get([]))
            pass

        # try:
        #     deep = kwargs['abs_deep']
        #     #Solo toma las keys de largo deep, hay que implementar items en DeepDict
        #     for r in result:
        #         new_results = r.keys_where(filter_fun)
        #         for rr in new_results:
        #             result.append(rr)
        #         result.remove(r)
        # except KeyError:
        #     pass

        # try:
        #     fun_name = kwargs['fun_name']
        #     exec_id_pattern = '(.*,%s,.*)' % fun_name
        #     filter_fun = lambda x: re.match(exec_id_pattern, x)
        #     for r in result:
        #         new_results = r.keys_where(filter_fun)
        #         for rr in new_results:
        #             result.append(rr)
        #         result.remove(r)
        # except KeyError:
        #     pass

        # try:
        #     exec_id_pattern = kwargs['call_id_pattern']
        #     filter_fun = lambda x: re.match(exec_id_pattern, x)
        #     for r in result:
        #         new_results = r.keys_where(filter_fun)
        #         for rr in new_results:
        #             result.append(rr)
        #         result.remove(r)
        # except KeyError:
        #     pass
        return result

    def _get_etimes(self, mibs):
        etimess = []
        for mib in mibs:
            try:
                #ToDo: Arreglar esto, no esta dando el arbol...
                # agg = mib['a']
                agg = mib
            except KeyError:
                continue
            execs = agg['execs']
            for execi in execs:
                etimes, capture = execi['etimes'], execi['capture']
                etimess.append(etimes)

        etimess = filter(lambda x: x != -1 , etimess)
        return etimess

    def get_avg_time(self, **filters):
        #ToDo: no va a manejar bien recursion, pero que le vamos a hacer... usar como contexto el deep de la recursion?
        # esto no es verdad, van a parar todos a la misma key de la misma funcion... aparte que que le vamos a hacer en ese caso...

        sum = self.get_sum_time(**filters)
        hits = self.get_hits(**filters)
        avg_time = sum/hits

        # Implementacion vieja, usando cada entrada
        # mibs = self.filterResult(**filters)
        # etimess = self._get_etimes(mibs)
        # if len(etimess) == 0:
        #     avg_time = 0
        # else:
        #     sumtime = reduce(lambda x,y: x+y , etimess, 0)
        #     avg_time = sumtime/len(etimess)

        return avg_time

    def get_sum_time(self, **filters):
        mibs = self.filterResult(**filters)

        sumtime = 0
        for mib in mibs:
            sumtime += int(mib['sum'])

        # Implementacion vieja, usando cada entrada
        # etimess = self._get_etimes(mibs)
        # sumtime = reduce(lambda x,y: x+y , etimess, 0)

        etimess = self._get_etimes(mibs)

        return sumtime

    def get_hits(self, **filters):
        mibs = self.filterResult(**filters)
        hitss = 0
        for mib in mibs:
            hitss += int(mib['hits'])
        return hitss

    def get_percent_time(self, **filters):
        #ToDo: Para esto requiero saber el call_stack
        pass
        # mibs = self.filter(**filters)
        # etimess = self._get_etimes(mibs)
        # sumtime = reduce(lambda x,y: x+y , etimess, 0)
        # return sumtime

    def get_mediana_time(self, **filters):
        mibs = self.filterResult(**filters)
        etimess = self._get_etimes(mibs)
        if len(etimess) == 0:
            mediana = 0
        else:
            s_etime = sorted(etimess, lambda x,y: x<y)
            med_index = int(len(s_etime)/2)
            mediana = s_etime[med_index]
        return mediana

    def print_brief(self, skey=None):
        #ToDo: Imprimir parte del sourcecode usando inspect.getsource() inspect.getsourceline() y etc...
        # o un poco del contexto con
        # fn, lno, func_name, _, _ = inspect.getframeinfo(frame, lineas_contexto)
        childs = self.storage.children(skey)
        for ss, vv in childs.items():
            try:
                sv = eval(ss)
            except NameError:
                print "Ingored <", ss , '>'
                continue
            line = sv[1][2]
            fun = sv[1][1]
            head = "%s:%s" % (fun, line)
            if skey:
                sskey = skey[:]
            else:
                sskey = []
            sskey.append(ss)
            #ToDO, hacer una clase stats que calcule su propio AVG, mediana, etc. el profiler hace demasiada
            #ToDo: agregar mas los datos, para dejarlo corriendo en regimen come mucho espacio de almacen...
            # definir para ello una politica de agregacion para cada caso (update fun)
            stats = "sumtime:%s - hits:%s - mediana:%s" % (self.get_sum_time(store_key=sskey),
                                                       self.get_hits(store_key=sskey),
                                                       self.get_mediana_time(store_key=sskey))
            print "%s -> %s" % (head, stats)


def profiled(*f_args, **f_kwargs):
    def real_decorator(fun):
        frame = sys._getframe(1)
        lineno = frame.f_lineno
        fun_name = fun.__name__
        mod_name = fun.__module__
        definition_info = (mod_name, fun_name, lineno)
        def funfun(*args, **kwargs):
            call_id = get_exec_id_here(2)
            exec_id = (definition_info, call_id)
            pp = get_profiler(*f_args, **f_kwargs)
            pp._profile_start(exec_id=exec_id)
            res = fun(*args, **kwargs)
            pp._profile_end()
            return res
        return funfun
    return real_decorator

