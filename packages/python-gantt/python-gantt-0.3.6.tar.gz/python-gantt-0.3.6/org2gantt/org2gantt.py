#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
org2gantt.py - version and date, see below

Author : Alexandre Norman - norman at xael.org
Licence : GPL v3 or any later version


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = 'Alexandre Norman (norman at xael.org)'
__version__ = '0.3.0'
__last_modification__ = '2015.01.08'


import copy
import datetime
import logging
import os
import sys
import re
import uuid

############################################################################

try:
    import clize
except ImportError:
    print("This program uses clize. See : https://github.com/epsy/clize")
    sys.exit(1)

############################################################################

try:
    import Orgnode
except ImportError:
    print("This program uses Orgnode. See : http://members.optusnet.com.au/~charles57/GTD/orgnode.html")
    sys.exit(1)

############################################################################

def __show_version__(name, **kwargs):
    """
    Show version
    """
    print("{0} version {1}".format(os.path.basename(name), __version__))
    return True


############################################################################

def _iso_date_to_datetime(isodate):
    """
    """
    __LOG__.debug("_iso_date_to_datetime ({0})".format({'isodate':isodate}))
    y, m, d = isodate.split('-')
    if m[0] == '0':
        m = m[1]
    if d[0] == '0':
        d = d[1]
    return "datetime.date({0}, {1}, {2})".format(y, m, d)

############################################################################

__LOG__ = None

############################################################################

def _init_log_to_sysout(level=logging.INFO):
    """
    """
    global __LOG__
    logger = logging.getLogger("org2gantt")
    logger.setLevel(level)
    fh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    __LOG__ = logging.getLogger("org2gantt")
    return


############################################################################

def make_task_from_node(n, prop={}, prev_task=''):
    """
    """
    __LOG__.debug('make_task_from_node ({0})'.format({'n':n.headline, 'prop':prop, 'prev_task':prev_task}))
    gantt_code = ''

    try:
        name = n.properties['task_id'].strip()
        if name == '':
            name = str(uuid.uuid4()).replace('-', '_')
    except KeyError:
        name = str(uuid.uuid4()).replace('-', '_')
    
    if ' ' in name:
        __LOG__.critical('** Space in task_id: [{0}]'.format(name))
        sys.exit(1)
    
    fullname = n.headline.strip().replace("'", '_')
    start = end = duration = None
    if n.scheduled != '':
        start = "{0}".format(_iso_date_to_datetime(str(n.scheduled)))
    if n.deadline != '':
        end = "{0}".format(_iso_date_to_datetime(str(n.deadline)))
    if 'Effort' in n.properties:
        duration = n.properties['Effort'].replace('d', '')

    if 'BLOCKER' in n.properties and n.properties['BLOCKER'].strip() == 'previous-sibling':
        depends_of = ['task_{0}'.format(prev_task)]
    else:
        try:
            depends = n.properties['BLOCKER'].split()
        except KeyError:
            depends_of = None
        else: # no exception raised
            depends_of = []
            for d in depends:
                depends_of.append('task_{0}'.format(d))

    if 'ordered'in prop and prop['ordered'] and prev_task is not None and prev_task != '':
        depends_of = ['task_{0}'.format(prev_task)]

    if depends_of is not None and len(depends_of) == 0:
        depends_of = None
    
    try:
        percentdone = n.properties['PercentDone']
    except KeyError:
        percentdone = None
    
    if n.todo == 'DONE':
        if percentdone is not None or percentdone != '100':
            __LOG__.warning('** Task [{0}] marked as done but PercentDone is set to {1}'.format(name, percentdone))
        percentdone = 100

    # Resources as tag
    if len(n.tags) > 0:
        ress = "{0}".format(["{0}".format(x) for x in n.tags.keys()]).replace("'", "")
    # Resources as properties
    elif 'allocate' in n.properties:
        ress = "{0}".format(["{0}".format(x) for x in n.properties['allocate'].replace(",", " ").split()]).replace("'", "")
    else:
        try:
            ress = prop['resources']
        except KeyError:
            ress = None
        except TypeError:
            ress = None


    # get color from task properties
    if 'color' in n.properties:
        color = "'{0}'".format(n.properties['color'].strip())

    # inherits color if defined
    elif 'color' in prop and prop['color'] is not None and n.todo in prop['color'] and  prop['color'][n.todo] is not None:
        color = "'{0}'".format(prop['color'][n.todo])
        
    else:
        color = None

    
    gantt_code += "task_{0} = gantt.Task(name='{1}', start={2}, stop={6}, duration={3}, resources={4}, depends_of={5}, percent_done={7}, fullname='{8}', color={9})\n".format(name, name, start, duration, ress, None, end, percentdone, fullname, color)

    # store dependencies for later
    dependencies = str(depends_of).replace("'", "")
    
    return (name, gantt_code, dependencies)


############################################################################

@clize.clize(
    alias = {
        'debug': ('d',),
        'gantt': ('g',),
        'start_date': ('s',),
        'end_date': ('e',),
        'today': ('t',),
        },
    extra = (
        clize.make_flag(
            source=__show_version__,
            names=('version', 'v'),
            help="Show the version",
            ),
        )
    )
def __main__(org, gantt='', start_date='', end_date='', today='', debug=False):
    """
    org2gantt.py
    
    org: org-mode filename

    gantt: output python-gantt filename (default sysout)

    start_date: force start date for output

    end_date: force end date for output

    today: force today date
    
    debug: debug

    Example :
    python org2gantt.py TEST.org

    Written by : Alexandre Norman <norman at xael.org>
    """

    gantt_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import gantt
"""

    global __LOG__
    if debug:
        _init_log_to_sysout(logging.DEBUG)
        gantt_code += "\nimport logging\ngantt.init_log_to_sysout(logging.DEBUG)\n"

    else:
        _init_log_to_sysout()

    if not os.path.isfile(org):
        __LOG__.error('** File do not exist : {0}'.format(org))
        sys.exit(1)
    
    # load orgfile
    nodes = Orgnode.makelist(org)

    __LOG__.debug('_analyse_nodes ({0})'.format({'nodes':nodes}))

    # Get all todo items
    LISTE_TODOS = {'TODO':None, 'DONE':None}
    with open(org) as f:
        for line in f.readlines():
            if line[:10] == '#+SEQ_TODO':
                kwlist = re.findall('([A-Z]+)\(', line)
                for kw in kwlist:
                    LISTE_TODOS[kw] = None

    # Find CONFIGURATION in heading
    n_configuration = None
    for n in nodes:
        if n.headline.strip() == "CONFIGURATION":
            n_configuration = n

    planning_start_date = None
    planning_end_date = None
    planning_today_date = _iso_date_to_datetime(str(datetime.date.today()))
    my_today = datetime.date.today()
    bar_color = {'TODO':'#FFFF90'}
    one_line_for_tasks = False

    # Generate code for configuration
    if n_configuration is not None:
        for t in LISTE_TODOS:
            if 'color_{0}'.format(t) in n_configuration.properties:
                bar_color[t] = n_configuration.properties['color_{0}'.format(t)].strip()


        if 'one_line_for_tasks' in n_configuration.properties and n_configuration.properties['one_line_for_tasks'].strip() == 't':
             one_line_for_tasks = True

        if today != '':
            planning_today_date = _iso_date_to_datetime(today)
            y, m, d = today.split('-')
            my_today = datetime.date(int(y), int(m), int(d))

        elif 'today' in n_configuration.properties:
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['today'])
            if len(dates) == 1:
                planning_today_date = _iso_date_to_datetime(dates[0])
                y, m, d = dates[0].split('-')
                my_today = datetime.date(int(y), int(m), int(d))

        if start_date != '':
            y, m, d = start_date.split('-')
            planning_start_date = _iso_date_to_datetime(start_date)

        elif 'start_date' in n_configuration.properties:
            # find date and use it
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['start_date'])
            if len(dates) == 1:
                planning_start_date = _iso_date_to_datetime(dates[0])
            # find +1m
            elif n_configuration.properties['start_date'].startswith('-') or n_configuration.properties['start_date'].startswith('+'):
                sign = n_configuration.properties['start_date'][0]
                qte = int(n_configuration.properties['start_date'][1:-1])
                what = n_configuration.properties['start_date'][-1]

                sign = -1*(sign=='-') + 1*(sign=='+')
                if what == 'd':
                    planning_start_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(days=qte*sign)))
                elif what == 'w':
                    planning_start_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(weeks=qte*sign)))


        if end_date != '':
            y, m, d = end_date.split('-')
            planning_end_date = _iso_date_to_datetime(end_date)

        elif 'end_date' in n_configuration.properties:
            # find date and use it
            dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', n_configuration.properties['end_date'])
            if len(dates) == 1:
                planning_end_date = _iso_date_to_datetime(dates[0])
            # find +1m
            elif n_configuration.properties['end_date'].startswith('-') or n_configuration.properties['end_date'].startswith('+'):
                sign = n_configuration.properties['end_date'][0]
                qte = int(n_configuration.properties['end_date'][1:-1])
                what = n_configuration.properties['end_date'][-1]

                sign = -1*(sign=='-') + 1*(sign=='+')
                if what == 'd':
                    planning_end_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(days=qte*sign)))
                elif what == 'w':                                 
                    planning_end_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(weeks=qte*sign)))
                elif what == 'm':                                 
                    planning_end_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(month=qte*sign)))
                elif what == 'y':                                 
                    planning_end_date = _iso_date_to_datetime(str(my_today + datetime.timedelta(years=qte*sign)))




    # Find RESOURCES in heading
    n_resources = []
    resources_id = []
    found = False
    plevel = 0
    for n in nodes:
        if found == True and n.level > plevel:
            n_resources.append(n)
        elif found == True and n.level <= plevel:
            break
        if found == False and n.headline.strip() == "RESOURCES":
            found = True
            plevel = n.level

    # Generate code for resources
    gantt_code += "\n#### Resources \n"
    next_level = 0
    current_level = 0
    current_group = None

    for nr in range(len(n_resources)):
        r = n_resources[nr]

        rname = r.headline.strip().replace("'","_")
        try:
            rid = r.properties['resource_id'].strip()
        except KeyError:
            rid = 'r_'+str(uuid.uuid4()).replace('-', '_')

        if rid in resources_id:
            __LOG__.critical('** Duplicate resource_id: [{0}]'.format(rid))
            sys.exit(1)

        resources_id.append(rid)

        if ' ' in rid:
            __LOG__.critical('** Space in resource_id: [{0}]'.format(rid))
            sys.exit(1)

        new_group_this_turn = False

        current_level = r.level
        if nr < len(n_resources) - 2:
            next_level = n_resources[nr+1].level

        # Group mode
        if current_level < next_level:
            gantt_code += "{0} = gantt.GroupOfResources('{1}')\n".format(rid, rname)
            current_group = rid
            new_group_this_turn = True
        # Resource
        else:
            gantt_code += "{0} = gantt.Resource('{1}')\n".format(rid, rname)
            
        # Vacations in body of node
        for line in r.body.split('\n'):
            if line.startswith('-'):
                dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', line)
                if len(dates) == 2:
                    start, end = dates
                    gantt_code += "{0}.add_vacations(dfrom={1}, dto={2})\n".format(rid, _iso_date_to_datetime(start), _iso_date_to_datetime(end))
                elif len(dates) == 1:
                    start = dates[0]
                    gantt_code += "{0}.add_vacations(dfrom={1})\n".format(rid, _iso_date_to_datetime(start))
                
            else:
                if line != '' and not line.strip().startswith(':'):
                    __LOG__.warning("Unknown resource line : {0}".format(line))


        if new_group_this_turn == False and current_group is not None:
            gantt_code += "{0}.add_resource(resource={1})\n".format(current_group, rid)

            # end of group
            if current_level > next_level:
                current_group = None


    # Find VACATIONS in heading
    n_vacations = None
    for n in nodes:
        if n.headline.strip() == "VACATIONS":
            n_vacations = n

    # Generate code for vacations
    gantt_code += "\n#### Vacations \n"
    if n_vacations is not None:
        for line in n_vacations.body.split('\n'):
            if line.startswith('-'):
                dates = re.findall('[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}', line)
                if len(dates) == 2:
                    start, end = dates
                    gantt_code += "gantt.add_vacations({0}, {1})\n".format(_iso_date_to_datetime(start), _iso_date_to_datetime(end))
                elif len(dates) == 1:
                    start = dates[0]
                    gantt_code += "gantt.add_vacations({0})\n".format(_iso_date_to_datetime(start))

            else:
                if line != '':
                    __LOG__.warning("Unknown vacation line : {0}".format(line))


    # Generate code for Projects
    gantt_code += "\n#### Projects \n"
    # Mother of all
    gantt_code += "project = gantt.Project(color='{0}')\n".format(bar_color['TODO'])

    prj_found = False
    tasks_name = []
    # for inheriting project, ORDERED, color, resources
    prop_inherits = []
    prev_task = None
    no_gantt_level = None
    late_dependencies = []
    for nr in range(len(nodes)):
        n = nodes[nr]

        __LOG__.debug('Analysing {0}'.format(n.headline))
        
        # it's a task / level 1
        if n.level == 1 \
               and  not n.headline.strip() in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
               and 'no_gantt' not in n.tags \
               and n.todo in LISTE_TODOS:

            __LOG__.debug(' task / level 1')

            prop_inherits = []
            prj_found = True
            prev_task = None
            no_gantt_level = None

            # Add task
            name, code, dependencies = make_task_from_node(n)
            late_dependencies.append([name, dependencies])

            if name in tasks_name:
                __LOG__.critical("Duplicate task id: {0}".format(name))
                sys.exit(1)
            else:
                tasks_name.append(name)

            gantt_code += code
            gantt_code += "project.add_task(task_{0})\n".format(name)
        elif 'no_gantt' in n.tags:
            if no_gantt_level is not None and no_gantt_level > n.level:
                no_gantt_level = n.level
                __LOG__.debug('no_gantt_tag {0}'.format(n.level))
            elif no_gantt_level is None:
                no_gantt_level = n.level
                __LOG__.debug('no_gantt_tag {0}'.format(n.level))

        # new project heading
        # Not a task, it's a project
        # it should have children
        elif n.level >= 1 \
                 and  not n.headline.strip() in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
                 and 'no_gantt' not in n.tags \
                 and not n.todo in LISTE_TODOS:

            if no_gantt_level is not None and n.level > no_gantt_level:
                __LOG__.debug('no_gantt_tag {0}/{1}'.format(n.level, no_gantt_level))
                continue
            else:
                __LOG__.debug('remove no_gantt_tag {0}/{1}'.format(n.level, no_gantt_level))
                no_gantt_level = None

            if n.level == 1:
                __LOG__.debug('** cleanup prop_inherits')
                prev_task = None
                prop_inherits = []

            if n.level > 1 and prj_found == False:
                __LOG__.debug(' do not keep')
                continue

            if len(prop_inherits) >= n.level:
                __LOG__.debug(' go one level up')
                prop_inherits = prop_inherits[:-1]


            __LOG__.debug(' new project heading')

            gantt_code += "###### Project {0} \n".format(n.headline.strip())

            try:
                name = n.properties['task_id'].strip()
            except KeyError:
                name = str(uuid.uuid4()).replace('-', '_')
    

            __LOG__.debug('{0}'.format(prop_inherits))

            if bar_color['TODO'] is not None:
                gantt_code += "project_{0} = gantt.Project(name='{1}', color='{2}')\n".format(name, n.headline.strip().replace("'", '_'), bar_color['TODO'])
            else:
                gantt_code += "project_{0} = gantt.Project(name='{1}', color=None)\n".format(name, n.headline.strip().replace("'", '_'))
                
            try:
                gantt_code += "project_{0}.add_task(project_{1})\n".format(prop_inherits[-1]['project_id'], name)
            except KeyError:
                gantt_code += "project.add_task(project_{0})\n".format(name)
            except IndexError:
                gantt_code += "project.add_task(project_{0})\n".format(name)

            if n.level == 1:
                prop_inherits = []

            # Inherits ORDERED
            if 'ORDERED' in n.properties and n.properties['ORDERED'] == 't':
                ordered = True
            else:
                if len(prop_inherits) > 0:
                    ordered = prop_inherits[-1]['ordered']
                else:
                    prev_task = None
                    ordered = False

            color = copy.deepcopy(bar_color)
            # Inherits color            
            if 'color' in n.properties:
                color['TODO'] = n.properties['color']
            else:
                if len(prop_inherits) > 0:
                    color['TODO'] = prop_inherits[-1]['color']['TODO']
                else:
                    color['TODO'] = bar_color['TODO']


            # Inherits resources
            # Resources as tag
            if len(n.tags) > 0:
                ress = "{0}".format(["{0}".format(x) for x in n.tags.keys()]).replace("'", "")
                # Resources as properties
            elif 'allocate' in n.properties:
                ress = "{0}".format(["{0}".format(x) for x in n.properties['allocate'].replace(",", " ").split()]).replace("'", "")
            else:
                try:
                    ress = prop_inherits[-1]['resources']
                except KeyError:
                    ress = None
                except IndexError:
                    ress = None


            prop_inherits.append({'ordered':ordered, 'color':color, 'project_id':name, 'resources':ress})
            prj_found = True



        # It's a task
        elif n.level >= 1 \
                 and prj_found == True \
                 and  not n.headline.strip() in ('RESOURCES', 'VACATIONS', 'CONFIGURATION') \
                 and 'no_gantt' not in n.tags \
                 and n.todo in LISTE_TODOS:

            __LOG__.debug(' new task under project {0}'.format(n.headline))

            if n.level == 1:
                prev_task = None
                prop_inherits = []
                __LOG__.debug(' clean prop_inherits')

            if no_gantt_level is not None and n.level > no_gantt_level:
                __LOG__.debug('no_gantt_tag {0}/{1}'.format(n.level, no_gantt_level))
                continue
            else:
                __LOG__.debug('remove no_gantt_tag {0}/{1}'.format(n.level, no_gantt_level))
                no_gantt_level = None

                
            if n.level > 1 and len(prop_inherits) < n.level - 1:
                __LOG__.critical('pb in structure : task "{0}" do not belong to a project but a task - possible inheritance problem'.format(n.headline))
                

            if len(prop_inherits) >= n.level:
                __LOG__.debug(' go one level up')
                prop_inherits = prop_inherits[:-1]

            __LOG__.debug(' bar_color {0}'.format(bar_color))

            # Add task
            if len(prop_inherits) > 0:
                name, code, dependencies = make_task_from_node(n, prop_inherits[-1], prev_task)
                late_dependencies.append([name, dependencies])
            else:
                name, code, dependencies = make_task_from_node(n, [], prev_task)
                late_dependencies.append([name, dependencies])


            if name in tasks_name:
                __LOG__.critical("Duplicate task id: {0}".format(name))
                sys.exit(1)
            else:
                tasks_name.append(name)

            prev_task = name

            gantt_code += code
            #gantt_code += "project.add_task(task_{0})\n".format(name)

            try:
                gantt_code += "project_{0}.add_task(task_{1})\n".format(prop_inherits[-1]['project_id'], name)
            except KeyError:
                gantt_code += "project.add_task(task_{0})\n".format(name)
            except IndexError:
                gantt_code += "project.add_task(task_{0})\n".format(name)

        else:
            prj_found = False
            prop_inherits = []

            __LOG__.debug(' nothing')
            

    gantt_code += "\n#### Dependencies \n"
    # Late dependencies
    for name, dep in late_dependencies:
        gantt_code += "task_{0}.add_depends(depends_of={1})\n".format(name, dep)


    # Full project
    gantt_code += "\n#### Outputs \n"

    gantt_code += "project.make_svg_for_tasks(filename='project.svg', today={0}, start={1}, end={2})\n".format(planning_today_date, planning_start_date, planning_end_date)
    gantt_code += "project.make_svg_for_resources(filename='project_resources.svg', today={0}, start={1}, end={2}, one_line_for_tasks={3})\n".format(planning_today_date, planning_start_date, planning_end_date, one_line_for_tasks)



    # write Gantt code
    if gantt == '':
        print(gantt_code)
    else:
        open(gantt, 'w').write(gantt_code)




    __LOG__.debug("All done. Exiting.")
    
    return



############################################################################



# MAIN -------------------
if __name__ == '__main__':

    clize.run(__main__)
    sys.exit(0)

    
#<EOF>######################################################################

