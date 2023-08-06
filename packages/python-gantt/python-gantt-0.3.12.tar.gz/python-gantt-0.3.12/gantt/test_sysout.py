#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import gantt
import sys
import logging
gantt.init_log_to_sysout(level=logging.CRITICAL)



# Create two resources
rANO = gantt.Resource('ANO')
rJLS = gantt.Resource('JLS')

# Add vacations for one lucky resource
rANO.add_vacations(
    dfrom=datetime.date(2014, 12, 29), 
    dto=datetime.date(2015, 1, 4) 
    )
rANO.add_vacations(
    dfrom=datetime.date(2015, 1, 6), 
    dto=datetime.date(2015, 1, 8) 
    )



# Create some tasks
t1 = gantt.Task(name='task1', start=datetime.date(2014, 12, 25), duration=4, percent_done=44, resources=[rANO], color="#FF8080")
t2 = gantt.Task(name='task2', start=datetime.date(2014, 12, 28), duration=6, resources=[rJLS])
t7 = gantt.Task(name='task7', start=datetime.date(2014, 12, 28), duration=5, percent_done=50)
t3 = gantt.Task(name='task3', start=datetime.date(2014, 12, 25), duration=4, depends_of=[t1, t7, t2], resources=[rJLS])
t4 = gantt.Task(name='task4', start=datetime.date(2015, 01, 01), duration=4, depends_of=t1, resources=[rJLS])
t5 = gantt.Task(name='task5', start=datetime.date(2014, 12, 23), duration=3)
t6 = gantt.Task(name='task6', start=datetime.date(2014, 12, 25), duration=4, depends_of=t7, resources=[rANO])
t8 = gantt.Task(name='task8', start=datetime.date(2014, 12, 25), duration=4, depends_of=t7, resources=[rANO, rJLS])


# Create a project
p1 = gantt.Project(name='Project 1')

# Add tasks to this project
p1.add_task(t1)
p1.add_task(t7)
p1.add_task(t2)
p1.add_task(t3)
p1.add_task(t5)
p1.add_task(t8)



# Create another project
p2 = gantt.Project(name='Project 2', color='#FFFF40')

# Add tasks to this project
p2.add_task(t2)
p2.add_task(t4)


# Create another project
p = gantt.Project(name='Gantt')
# wich contains the first two projects
# and a single task
p.add_task(p1)
p.add_task(p2)
p.add_task(t6)




##########################$ MAKE DRAW ###############
p.make_svg_for_tasks(filename=sys.stdout, today=datetime.date(2014, 12, 31), start=datetime.date(2014,12, 15), end=datetime.date(2015, 01, 14))
p.make_svg_for_resources(filename='test.svg', today=datetime.date(2014, 12, 31), resources=[rANO, rJLS])
##########################$ /MAKE DRAW ###############
