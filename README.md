# sysu-planner
This planner is a two phases planner. It first performs a 1-BFWS ([Nir and Hector 2017](https://people.eng.unimelb.edu.au/nlipovetzky/papers/aaai17-BFWS-novelty-exploration.pdf)) with very fast speed. Then if solution is not found, it will perform a modified OLCFF ([Maximilian and Jorg 2018](https://ipc2018-classical.bitbucket.io/planner-abstracts/team8.pdf)). 

So its source code contains two part:
* BFWS-public and LAPKT-public
* fast-downward-conjunctions

Then planner should be invoked by the fast-downward-conjunctions part (using --dual option and it will call BFWS-public/fd-version/bfws.py to perform 1-BFWS).

## Build and run with container
```
sudo singularity build planner.img sysu-planner/Singularity
mkdir rundir
cp path/to/domain.pddl rundir
cp path/to/problem.pddl rundir
RUNDIR="$(pwd)/rundir"
DOMAIN="$RUNDIR/domain.pddl"
PROBLEM="$RUNDIR/problem.pddl"
PLANFILE="$RUNDIR/sas_plan"
singularity run -C -H $RUNDIR planner.img $DOMAIN $PROBLEM $PLANFILE $COSTBOUND
```

### Potential Failure
If the above build has failed, it may appears to be a cmake cache fail. In this case, remove the *builds* (if it exists) directory under fast-downward-conjunctions and rerun the singularity command should solve the problem.

Or it may appears to be a scons build fail. In this case, remove all the *.sconsign.dblite* files under the directory should solve the problem.

Both cases would occur if the planner was built outside a container.
