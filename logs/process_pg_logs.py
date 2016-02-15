import re
import sys
import pytz
import datetime

DB_USER = 'dbuser'
DB_NAME = 'dbname'

filename = sys.argv[1]

f = file(name=filename, mode='r', buffering=1)

cur_tz = pytz.timezone('America/Montevideo')

#   %a = application name
#   %h = remote host
#   %t = timestamp without milliseconds
#   %m = timestamp with milliseconds
#   %i = command tag
#   %e = SQL state
#   %c = session ID
#   %l = session line number
#   %s = session start timestamp
#   %v = virtual transaction ID
#   %x = transaction ID (0 if none)
#   %q = stop here in non-session processes
#   %% = '%'

#   %t = timestamp without milliseconds
#   %r = remote host and port
#   %u = user name
#   %d = database name
#   %p = process ID

#%t:%r:%u@%d:[%p]:

cons = []
discons = []

pattern_conn = r'(....-..-.. ..:..:..) UTC:(10\.0\..*\..*)\((.*)\):%(db_user)s@%(db_name)s:\[(.*)\]:LOG:  connection authorized: user=%(db_user)s database=%(db_name)s' % {'db_user': DB_USER, 'db_name': DB_NAME}
pattern_disconn = r'(....-..-.. ..:..:..) UTC:(10\.0\..*\..*)\((.*)\):%(db_user)s@%(db_name)s:\[(.*)\]:LOG:  disconnection: session time: (.+) user=%(db_user)s database=%(db_name)s host=(10\.0\..*\..*) port=.+' % {'db_user': DB_USER, 'db_name': DB_NAME}
for line in f:
    g = re.match(pattern=pattern_conn, string=line)
    if g:
        ip = g.group(2)
        d = g.group(1)
        d = datetime.datetime.strptime(d ,'%Y-%m-%d %H:%M:%S')
        d = d.replace(tzinfo=pytz.UTC)
        req_id = g.group(3)
        pid = g.group(4)

        cons.append((ip, d, req_id, pid, ))

    g = re.match(pattern=pattern_disconn, string=line)
    if g:
        ip = g.group(2)
        d = g.group(1)
        d = datetime.datetime.strptime(d ,'%Y-%m-%d %H:%M:%S')
        d = d.replace(tzinfo=pytz.UTC)
        req_id = g.group(3)
        pid = g.group(4)
        e_time = g.group(5)
        ip_2 = g.group(6)

        discons.append((ip, d, req_id, pid, e_time, ip_2, ))


print len(discons)
print len(cons)
