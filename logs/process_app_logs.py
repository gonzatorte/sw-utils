import re
import sys
import pytz
import datetime
import pprint

filename = sys.argv[1]
try:
    start_line = int(sys.argv[2])
except IndexError:
    start_line = 0

if filename == "-":
    f = sys.stdin
else:
    f = file(name=filename, mode='r', buffering=1)

for i in xrange(start_line):
    f.next()
line_count = start_line

cur_tz = pytz.timezone('America/Montevideo')

# cat app.log | sed -n '/May 19 10:.*/,$ p' | sed -n '0,/May 19 15:.*/ p' | python process_app_logs.py -
#
# May 18 17:45:02 ip-10-0-1-90 [celery-worklog]: 2015-05-18 14:45:02,477 [i-c7a2f410][MainProcess:11922][MainThread:140544422221568][INFO:20][TIN:159,ID:102|STATUS LOCATION <2015-05-18 14:45:02.468744>] <SEMLOCK <5545299097631516610>: request lock. Bussy by <Nada>>
# May 18 17:45:02 ip-10-0-1-90 [celery-worklog]: 2015-05-18 14:45:02,483 [i-c7a2f410][MainProcess:11922][MainThread:140544422221568][INFO:20][TIN:159,ID:102|STATUS LOCATION <2015-05-18 14:45:02.468744>] <SEMLOCK<5545299097631516610>: release lock. e_times:<[0.0, 0.0, 0.0, 0.0, 0.0]>>

LOOP_LOAD = 1000
MAX_LOOPS = 1000
PIVOT_SIZE = 20

DATE_FROM = datetime.datetime(year=2015, month=5, day=19, hour=7, minute=0, second=0, microsecond=0, tzinfo=cur_tz)
DATE_TO = datetime.datetime(year=2015, month=5, day=19, hour=10, minute=0, second=0, microsecond=0, tzinfo=cur_tz)

loop_count = 0
releases = []
requests = []
bloqued = {}

while True:
    # releases = releases[-PIVOT_SIZE:]
    # requests = requests[-PIVOT_SIZE:]
    releases = []
    requests = []

    for line in f:
        line_count += 1
        g = re.match(pattern=r'(.* .. ..:..:..) (.*) \[(.*)\]: (....-..-.. ..:..:..,.*) \[(.*)\]\[(.*):(.*)\]\[(.*):(.*)\]\[(.*):(.*)\]\[(.*)\] <(.*)>', string=line)
        if not g:
            # print line
            # raise Exception("Linea no reconocida")
            #Descarto linea
            continue
        arrive_log_time = g.group(1)
        arrive_log_time = datetime.datetime.strptime(arrive_log_time, '%B %d %H:%M:%S')
        arrive_log_time = arrive_log_time.replace(year=2015)
        arrive_log_time = arrive_log_time.replace(tzinfo=pytz.UTC)

        host_name = g.group(2)
        app = g.group(3)

        create_log_time = g.group(4)
        create_log_time = datetime.datetime.strptime(create_log_time, '%Y-%m-%d %H:%M:%S,%f')
        create_log_time = create_log_time.replace(tzinfo=cur_tz)

        if not (DATE_FROM < create_log_time < DATE_TO):
            continue
        loop_count += 1

        instance_id = g.group(5)
        pname = g.group(6)
        pid = g.group(7)
        tname = g.group(8)
        tid = g.group(9)
        lvl_name = g.group(10)
        lvl_num = g.group(11)
        #TIN:159,ID:102|STATUS LOCATION <2015-05-18 14:45:02.468744>
        context = g.group(12)
        g1 = re.match(pattern=r'TIN:(.*),ID:.*', string=context)
        tin = g1.group(1)
        #SEMLOCK <5545299097631516610>: request lock. Bussy by <Nada>
        msg = g.group(13)
        g2 = re.match(pattern=r'SEMLOCK.?<(.*)>: request lock. Bussy by <(.*)>', string=msg)
        g3 = re.match(pattern=r'SEMLOCK.?<(.*)>: release lock. e_times:<(.*)>', string=msg)
        if not g2 and not g3:
            #Descarta la entrada
            continue
        if g2:
            sem_id = g2.group(1)
            bloked_sem_id = g2.group(2)
            # requests.append((sem_id, bloked_sem_id))
            requests.append((sem_id, bloked_sem_id, #tin,
                             create_log_time.strftime('%H:%M:%S'), arrive_log_time.strftime('%H:%M:%S')))
        elif g3:
            sem_id = g3.group(1)
            e_times = eval(g3.group(2))
            # releases.append((sem_id, e_times))
            releases.append((sem_id, e_times, #tin,
                             create_log_time.strftime('%H:%M:%S'), arrive_log_time.strftime('%H:%M:%S')))

        if loop_count%LOOP_LOAD == 0:
            break
    else:
        break

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>"

    all_requests = set(map(lambda x: x[0], requests))
    all_releases = set(map(lambda x: x[0], releases))
    print "Requests not released"
    pprint.pprint(all_requests.difference(all_releases))
    print "Releases not requested"
    pprint.pprint(all_releases.difference(all_requests))

    print "Blocked by distinct than Nada"
    now_bloqued = filter(lambda x: x[1] != 'Nada', requests)
    pprint.pprint(now_bloqued)
    now_bloqued_ids = map(lambda x: x[0], now_bloqued)
    for id_b in now_bloqued_ids:
        bloqued[id_b] = bloqued.get(id_b,0) + 1
    now_releases_ids = map(lambda x: x[0], releases)
    for id_r in now_releases_ids:
        bloqued[id_b] = bloqued.get(id_b,0) - 1
    # bloqued = filter(lambda x: x[1] > 0, bloqued)

    print "Pending bloqued"
    #Imprimir una lista de pendientes
    pprint.pprint(bloqued)

    # for (k,v) in requests.iteritems():
    #     if

    print "Big time for release"
    pprint.pprint(map(lambda x: (x[0], x[1][4]), filter(lambda x: x[1][4] > 0.1, releases)))

    print "CURRENT LINE %s" % line_count
    print "<<<<<<<<<<<<<<<<<<<<<<<<<<<"


    if loop_count == LOOP_LOAD*MAX_LOOPS:
        break
