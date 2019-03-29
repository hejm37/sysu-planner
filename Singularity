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
    export LAPKT_PATH=/planner/LAPKT-public
    ## The "%post"-part of this script is called after the container has
    ## been created with the "%setup"-part above and runs "inside the
    ## container". Most importantly, it is used to install dependencies
    ## and build the planner. Add all commands that have to be executed
    ## once before the planner runs in this part of the script.

    ## Install all necessary dependencies.
    dnf upgrade -y
    dnf group install -y "Development Tools"
    dnf install -y python python-devel gcc-c++ cmake boost boost-devel glibc-static libstdc++-static clang scons boost-python
    # some bug with boost-python
    ln -s /usr/lib64/libboost_python.so.1.66.0 /usr/lib64/libboost_python.so

    cd /planner/BFWS-public/fd-version
    ./build.py -j4

    ## Build your planner
    cd /planner/fast-downward-conjunctions
    ./build.py release64 -j4

    ## Clean up
    rm -rf /planner/fast-downward-conjunctions/builds/release64/search/CMakeFiles
    dnf remove -y gcc-c++ cmake python-devel glibc-static libstdc++-static clang scons
    dnf autoremove -y
    dnf clean all
    rm /usr/lib64/libboost_python.so

%runscript

    ## The runscript is called whenever the container is used to solve
    ## an instance.

    SEED=37

    DOMAINFILE=$1
    PROBLEMFILE=$2
    PLANFILE=$3
    export BFWS_HOME="/planner/BFWS-public"

    ## Call your planner.
    /planner/fast-downward-conjunctions/fast-downward.py \
        --dual --build=release64 \
        --plan-file $PLANFILE \
        $DOMAINFILE \
        $PROBLEMFILE \
    --search-options \
    --heuristic "hcff=cff(seed=$SEED, cache_estimates=false, cost_type=ONE)" \
    --heuristic "hn=novelty(cache_estimates=false)" \
    --search "ehc_cn(seed=$SEED, h=hcff, novelty=hn, learning_stagnation=PROCEED, learning_stagnation=1, preferred=hcff, cost_type=ONE, max_growth=8)"
    # --preprocess-options --h2_time_limit 30

    #     --heuristic "tmp=novelty_linker(hcff, [hn])" \
    # --heuristic "hlm=lmcount(lm_rhw(reasonable_orders=true, lm_cost_type=ONE), cost_type=ONE)" \
    # --search "ipc18_iterated([ehc_cn(hcff, preferred=hcff, novelty=hn, seed=$SEED, cost_type=ONE, max_growth=8, max_time=180), lazy_greedy_c([hcff, hlm], preferred=[hcff], conjunctions_heuristic=hcff, strategy=maintain_fixed_size_probabilistic(initial_removal_mode=UNTIL_BOUND, base_probability=0.02, target_growth_ratio=1.50), cost_type=ONE)], continue_on_solve=false, continue_on_fail=true, delete_after_phase_heuristics=[hn, tmp], delete_after_phase_phases=[0, 0])" \

## Update the following fields with meta data about your submission.
## Please use the same field names and use only one line for each value.
%labels
# Name        OLCFF
# Description Online-Learning hCFF in EHC with Novelty Pruning and GBFS with Landmarks
# Authors     Maximilian Fickert <fickert@cs.uni-saarland.de> and Jörg Hoffmann <hoffmann@cs.uni-saarland.de>
# SupportsDerivedPredicates no
# SupportsQuantifiedPreconditions no
# SupportsQuantifiedEffects yes
