# -*- coding: utf-8 -*-
from __future__ import print_function

import logging
import subprocess
import sys

from . import aliases
from . import arguments
from . import cleanup
from . import run_components
from timeit import default_timer as timer


def main():
    start = timer()
    args = arguments.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()),
                        format="%(levelname)-8s %(message)s",
                        stream=sys.stdout)
    logging.debug("processed args: %s" % args)

    if args.show_aliases:
        aliases.show_aliases()
        sys.exit()

    if args.cleanup:
        cleanup.cleanup_temporary_files(args)
        sys.exit()

    # If validation succeeds, exit with the search component's exitcode.
    exitcode = None
    plan_found, validated = False, False

    for component in args.components:
        try:
            if component == "translate":
                if args.dual_fd:
                    dual_first_found = run_components.run_1_bfws_fd(args)
                    if dual_first_found:
                        print("Plan found by 1-BFWS-fd.")
                        plan_found = True
                    else:
                        print("Plan not found by 1-BFWS-fd, entering second phase")
                elif args.dual_ff:
                    dual_first_found = run_components.run_1_bfws_ff(args)
                    if dual_first_found:
                        print("Plan found by 1-BFWS-ff.")
                        plan_found = True
                    else:
                        print("Plan not found by 1-BFWS-ff, entering second phase")
                        run_components.run_translate(args)
                else:
                    run_components.run_translate(args)
            elif component == "preprocess":
                if not plan_found:
                    run_components.run_preprocess(args)
            elif component == "search":
                if not plan_found:
                    exitcode = run_components.run_search(args)
            elif component == "validate":
                end = timer()
                print("TOTAL TIME:", end - start, 's')
                validated = True
                run_components.run_validate(args)
            else:
                assert False
        except subprocess.CalledProcessError as err:
            print(err)
            exitcode = err.returncode
            break
    if not validated:
        end = timer()
        print("TOTAL TIME:", end - start, 's')
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
