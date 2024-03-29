#! /usr/bin/env python
import fd.grounding
import sys
import os
from libbfws import BFWS
from timeit import default_timer as timer
# MRJ: Profiler imports
#from prof import profiler_start, profiler_stop


def main(domain_file, problem_file, search_alg):
    task = BFWS()

    task.ignore_action_costs = True

    dual_BFWS = search_alg == 'dual-1-BFWS'
    if dual_BFWS:
        search_alg = '1-BFWS'
        fdTask, groups, mutex_groups, translation_key, actions, axioms = fd.grounding.dual_translate(domain_file, problem_file, task)
    else:
        start = timer()
        fd.grounding.default(domain_file, problem_file, task)
        end = timer()
        print "Translate time:", end - start, 's'

    # NIR: Uncomment to check what actions are being loaded
    # for i in range( 0, task.num_actions() ) :
    #	task.print_action( i )

    # NIR: Setting planner parameters is as easy as setting the values
    # of Python object attributes

    # NIR: log filename set
    task.log_filename = 'bfws.log'

    # NIR: search alg
    task.search = search_alg

    # NIR: Set Max novelty to 2
    task.max_novelty = 2

    # NIR: Set M to 32
    task.m_value = 32

    # NIR: Comment line below to deactivate profiling
    #profiler_start( 'bfws.prof' )

    # NIR: We call the setup method in SIW_Planner
    task.setup()

    # NIR: And then we're ready to go
    task.solve()

    if dual_BFWS and os.path.getsize('plan.ipc') == 0:
        sas_timer = fd.timers.Timer()
        fd.grounding.translateToSas(fdTask, groups, mutex_groups, translation_key, actions, axioms)
        print "Output sas file completed in", sas_timer.report(), 'secs'
    elif not dual_BFWS:
        end = timer()
        print "TOTAL TIME:", end - start, 's'
    # NIR: Comment lines below to deactivate profile
    # profiler_stop()

    #rv = os.system( 'google-pprof --pdf libbfws.so bfws.prof > bfws.pdf' )
    # if rv != 0 :
    #	print >> sys.stderr, "An error occurred while translating google-perftools profiling information into valgrind format"


def debug():
    main("/Users/nirlipo/Sandboxes/trapper/trapper/examples/domain.pddl",
         "/Users/nirlipo/Sandboxes/trapper/trapper/examples/prob3.pddl",
         "fast")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
