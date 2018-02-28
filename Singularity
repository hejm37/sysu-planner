bootstrap: docker
From:      fedora:latest

%setup
     ## The "%setup"-part of this script is called to bootstrap an empty
     ## container. It copies the source files from the branch of your
     ## repository where this file is located into the container to the
     ## directory "/planner". Do not change this part unless you know
     ## what you are doing and you are certain that you have to do so.

    REPO_ROOT=`dirname $SINGULARITY_BUILDDEF`
    cp -r $REPO_ROOT/ $SINGULARITY_ROOTFS/planner

%post

    ## The "%post"-part of this script is called after the container has
    ## been created with the "%setup"-part above and runs "inside the
    ## container". Most importantly, it is used to install dependencies
    ## and build the planner. Add all commands that have to be executed
    ## once before the planner runs in this part of the script.

    ## Install all necessary dependencies.
    dnf upgrade -y
    dnf group install -y "Development Tools"
    dnf install -y python gcc-c++ cmake boost boost-devel glibc-static libstdc++-static

    ## Build your planner
    cd /planner/fast-downward-conjunctions
    ./build.py release64 -j4

%runscript
    ## The runscript is called whenever the container is used to solve
    ## an instance.

    SEED=42

    DOMAINFILE=$1
    PROBLEMFILE=$2
    PLANFILE=$3
    ## The cost bound is only used in the cost-bounded track.
    COSTBOUND=$4

    ## Call your planner.
    /planner/fast-downward-conjunctions/fast-downward.py \
        --build=release64 \
        --plan-file $PLANFILE \
        $DOMAINFILE \
        $PROBLEMFILE \
    --heuristic "hcff=cff(seed=$SEED, cache_estimates=false, cost_type=ONE)" \
    --heuristic "hn=novelty(cache_estimates=false)" \
    --heuristic "tmp=novelty_linker(hcff, [hn])" \
    --search "ehc_cn(hcff, preferred=hcff, novelty=hn, seed=$SEED, cost_type=ONE)"

## Update the following fields with meta data about your submission.
## Please use the same field names and use only one line for each value.
%labels
Name        Planner 4
Description Refinement-EHC with hCFF and novelty pruning
Authors     Maximilian Fickert <fickert@cs.uni-saarland.de>
SupportsDerivedPredicates no
SupportsQuantifiedPreconditions no
SupportsQuantifiedEffects no
