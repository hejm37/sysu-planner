# sysu-planner
The SYSU-Planner is a two-stage planner designed to solve classical planning problems. It first performs the 1-BFWS ([Nir and Hector 2017](https://people.eng.unimelb.edu.au/nlipovetzky/papers/aaai17-BFWS-novelty-exploration.pdf)) with very fast speed. If it fails to find a solution, it will then perform a modified online refinement algorithm named [Forward-RHC](http://ada.liacs.nl/events/sparkle-planning-19/documents/solver_description/SYSU-planner-description.pdf) (see also [Maximilian and Jorg 2018](https://ipc2018-classical.bitbucket.io/planner-abstracts/team8.pdf)). 

## Build and run with container
Using the planner with [Singularity](https://sylabs.io/docs/#singularity) is rather simple. First install Singularity following [this guide](https://sylabs.io/guides/3.3/user-guide/quick_start.html#quick-installation-steps). Then run the following script in CLI and you will have the plan file *sas_plan* under *$RUNDIR*. 
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

### Supported problems
The formulation of supported problems is the same as [IPC 2018](https://ipc2018-classical.bitbucket.io/#pddl). We also provide a set of supported domains and problems in [benchmark-domains](https://github.com/hejm37/benchmark-domains).

## Notes on playing with the source code
The source code of the planner contains two part:
* BFWS-public and its dependency, LAPKT-public
* fast-downward-conjunctions

Then planner should be invoked in the fast-downward-conjunctions part (using --dual option and it will call BFWS-public/fd-version/bfws.py to perform 1-BFWS, see [the Singularity script](https://github.com/hejm37/sysu-planner/blob/master/Singularity) for more details).

### Potential Failures
If the above build has failed, it may appears to be a cmake cache fail. In this case, remove the *builds* (if it exists) directory under fast-downward-conjunctions and rerun the singularity command shall solve the problem.

Or it may appears to be a scons build fail. In this case, remove all the *.sconsign.dblite* files under the directory shall solve the problem.

Both cases would occur if the planner was built outside a container.
