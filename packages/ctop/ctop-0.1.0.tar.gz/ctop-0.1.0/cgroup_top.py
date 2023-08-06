#!/usr/bin/env python
'''
Iterate over all cgroup mountpoints and output global cgroup statistics
'''

import os
import sys
import stat
import pwd
import time
import psutil

from collections import defaultdict

try:
    import curses
except ImportError:
    print >> sys.stderr, "Curse is not available on this system. Exiting."
    sys.exit(0)

HIDE_EMPTY_CGROUP = True
UPDATE_INTERVAL = 1.0 # seconds
CGROUP_MOUNTPOINTS={}

# TODO:
# - react to keyborad/mouse events
# - select display colums
# - select refresh rate
# - select sort column
# - detect container technology
# - visual CPU/memory usage
# - block-io
# - auto-color
# - adapt name / commands to underlying container system
# - hiereachical view

## Utils

def to_human(num, suffix='B'):
    num = int(num)
    for unit in [' ','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "{:.1f}{}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:5.1d}{}{}" % (num, 'Y', suffix)

class Cgroup(object):
    def __init__(self, path, base_path):
        self.path = path
        self.base_path = base_path

    @property
    def name(self):
        return self.path[len(self.base_path):] or '/'

    @property
    def owner(self):
        path = os.path.join(self.base_path, self.path, 'tasks')
        uid = os.stat(path).st_uid
        try:
            return pwd.getpwuid(uid).pw_name
        except:
            return uid

    def _coerce(self, value):
        try:
            return int(value)
        except: 
            pass

        try:
            return float(value)
        except:
            pass

        return value

    def __getitem__(self, name):
        path = os.path.join(self.base_path, self.path, name)
        
        with open(path) as f:
            content = f.read().strip()

        if name == 'tasks' or '\n' in content:
            content = content.split('\n')

            if ' ' in content[0]:
                content = dict((l.split(' ') for l in content))
                for k, v in content.iteritems():
                    content[k] = self._coerce(v)
            else:
                content = [self._coerce(v) for v in content]

        else:
            content = self._coerce(content)

        return content

def cgroups(base_path):
    '''
    Generator of cgroups under path ``name``
    '''
    for cgroup_path, dirs, files in os.walk(base_path):
        yield Cgroup(cgroup_path, base_path)

## Grab cgroup data

def init():
    # Get all cgroup subsystems avalaible on this system
    with open("/proc/cgroups") as f:
        cgroups = f.read().strip()

    subsystems = []
    for cgroup in cgroups.split('\n'):
        if cgroup[0] == '#': continue
        subsystems.append(cgroup.split()[0])

    # Match cgroup mountpoints to susbsytems. Always take the first matching
    with open("/proc/mounts") as f:
        mounts = f.read().strip()

    for mount in mounts.split('\n'):
        mount = mount.split(' ')

        if mount[2] != "cgroup":
            continue

        for arg in mount[3].split(','):
            if arg in subsystems and arg not in CGROUP_MOUNTPOINTS:
                CGROUP_MOUNTPOINTS[arg] = mount[1]

def collect(measures):
    cur = defaultdict(dict)
    prev = measures['data']

    # Collect global data
    if 'cpuacct' in CGROUP_MOUNTPOINTS:
        # list all "folders" under mountpoint
        for cgroup in cgroups(CGROUP_MOUNTPOINTS['cpuacct']):
            # Collect tasks
            cur[cgroup.name]['tasks'] = cgroup['tasks']

            # Collect user
            cur[cgroup.name]['owner'] = cgroup.owner

    # Collect memory statistics
    if 'memory' in CGROUP_MOUNTPOINTS:
        # list all "folders" under mountpoint
        for cgroup in cgroups(CGROUP_MOUNTPOINTS['memory']):
            cur[cgroup.name]['memory.usage_in_bytes'] = cgroup['memory.usage_in_bytes']
            cur[cgroup.name]['memory.max_usage_in_bytes'] = cgroup['memory.usage_in_bytes']
            cur[cgroup.name]['memory.limit_in_bytes'] = min(int(cgroup['memory.limit_in_bytes']), measures['global']['total_memory'])

    # Collect CPU statistics
    if 'cpuacct' in CGROUP_MOUNTPOINTS:
        # list all "folders" under mountpoint
        for cgroup in cgroups(CGROUP_MOUNTPOINTS['cpuacct']):
            # Collect CPU stats
            cur[cgroup.name]['cpuacct.stat'] = cgroup['cpuacct.stat']
            cur[cgroup.name]['cpuacct.stat.diff'] = {'user':0, 'system':0}

            # Collect CPU increase on run > 1
            if cgroup.name in prev:
                for key, value in cur[cgroup.name]['cpuacct.stat'].iteritems():
                    cur[cgroup.name]['cpuacct.stat.diff'][key] = value - prev[cgroup.name]['cpuacct.stat'][key]

    # Apply
    measures['data'] = cur

def display(scr, measures, sort_key):
    # Time
    prev_time = measures['global'].get('time', -1)
    cur_time = time.time()
    time_delta = cur_time - prev_time
    measures['global']['time'] = cur_time
    cpu_to_percent = measures['global']['scheduler_frequency'] * measures['global']['total_cpu'] * time_delta

    # Build data lines
    results = []
    for cgroup, data in measures['data'].iteritems():
        cpu_usage = data.get('cpuacct.stat.diff', {})
        line = {
            'owner': data.get('owner', 'nobody'),
            'tasks': len(data['tasks']),
            'memory_cur': "{: >7}/{: <7}".format(to_human(data.get('memory.usage_in_bytes', 0)), to_human(data.get('memory.limit_in_bytes', measures['global']['total_memory']))),
            'memory_peak': to_human(data.get('memory.max_usage_in_bytes', 0)),
            'cpu_syst': cpu_usage.get('system', 0) / cpu_to_percent,
            'cpu_user': cpu_usage.get('user', 0) / cpu_to_percent,
            'cgroup': cgroup,
        }
        line['cpu_total'] = line['cpu_syst'] + line['cpu_user']
        results.append(line)

    # Sort
    results = sorted(results, key=lambda line: line.get(sort_key, 0), reverse=True)

    # Display statistics
    curses.endwin()
    height, width = scr.getmaxyx()
    LINE_TMPL = "{:"+str(width)+"s}"
    scr.addstr(0, 0, LINE_TMPL.format('                          MEMORY             CPU'), curses.color_pair(1))
    scr.addstr(1, 0, LINE_TMPL.format('OWNER      PROC     CURRENT       PEAK  SYSTEM USER CGROUP'), curses.color_pair(1))
    RES_TMPL = "{owner:10s} {tasks:4d} {memory_cur:15s} {memory_peak:>7s} {cpu_syst: >5.1%} {cpu_user: >5.1%} {cgroup}"

    lineno = 2
    for line in results:
        try:
            line = RES_TMPL.format(**line)
            scr.addstr(lineno, 0, LINE_TMPL.format(line))
        except:
            break
        lineno += 1

    scr.refresh()

def main():
    # Initialization, global system data
    measures = {
        'data': defaultdict(dict),
        'global': {
            'total_cpu': psutil.cpu_count(),
            'total_memory': psutil.virtual_memory().total,
            'scheduler_frequency': os.sysconf('SC_CLK_TCK'),
        }
    }

    init()

    try:
        # Curse initialization
        stdscr = curses.initscr()
        curses.start_color() # load colors
        curses.use_default_colors()
        curses.noecho()      # do not echo text
        curses.cbreak()      # do not wait for "enter"
        curses.curs_set(0)   # hide cursor
        stdscr.keypad(1)     # parse keypad controll sequences

        # Curses colors
        curses.init_pair(1, -1, curses.COLOR_GREEN)

        # Main loop
        while True:
            collect(measures)
            display(stdscr, measures, 'cpu_total')
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()

