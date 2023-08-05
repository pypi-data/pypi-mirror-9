import gc
import lib as epics 

name1 = "Py:ao1"
name2 = "Py:ao2"
name3 = "Py:ao4"
 

def report_usage():
    print("=================================")
    epics.ca.show_cache()
    for xid, val in epics.ca._cache.items():
        print xid
        for e in val.items():
            print e
    gc.collect()
    print("Live PV object count: %d" % len([o for o in gc.get_objects() if type(o) == epics.PV]))
 

def do_some_stuff():

    p = epics.PV(name1)
    
    p = epics.PV(name2)
    
    p = epics.PV(name3)
    
    p = None
    epics.poll(0.1)
    report_usage()
    
do_some_stuff()
# 
do_some_stuff()
# 
do_some_stuff()
