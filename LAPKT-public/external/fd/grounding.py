from __future__ import print_function

from collections import defaultdict

import build_model
import pddl_to_prolog
import pddl
import fact_groups
import timers
import sys


import normalize
import pddl_parser
import translate
import simplify

from instantiate import get_fluent_facts, get_objects_by_type, instantiate, explore

class PropositionalDetAction:

    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        self.precondition = []
        self.effects = []
        self.cond_effs = {}
        self.negated_conditions = []

    def set_precondition(self, prec, atom_table):
        precset = set()
        negprecset = set()
        for p in prec:
            sym = atom_table[p.text()]
            if p.negated and sym not in self.negated_conditions:
                negprecset.add(sym)
                self.negated_conditions.append(sym)
            precset.add((sym, p.negated))
        for sym, negated in precset:
            self.precondition.append((sym, negated))
        for sym in negprecset:
            self.negated_conditions.append(sym)

    def add_effect(self, adds, dels, atom_table, atom_names, axioms):
        effs = []
        for cond, lit in adds:
            if len(cond) == 0:
                effs.append((atom_table[lit.text()], False))
            else:
                condition_unfiltered = [
                    (atom_table[cond_lit.text()], cond_lit.negated) for cond_lit in cond]
                condition = []
                axioms_changed = []
                for c in condition_unfiltered:
                    if c[1] and c[0] not in self.negated_conditions:
                        has_axiom = False
                        for a in axioms:
                            if '('+atom_names[c[0]]+')' == a.name:
                                axioms_changed.append(a)
                                has_axiom = True
                        if has_axiom is False:
                            self.negated_conditions.append(c[0])
                    else:
                        condition.append(c)
                # Reencode axioms from universal quantifier introduced by the normalize.remove_universal_quantifier function
                # Remove once we add proper support for axioms
                has_axiom = False
                for a in axioms_changed:
                    has_axiom = True
                    for c in a.condition:
                        if c.negated == False:
                            self.negated_conditions.append(
                                atom_table[c.text()])
                            condition.append((atom_table[c.text()], True))
                        else:
                            condition.append((atom_table[c.text()], False))

                condition = tuple(condition)
                try:
                    self.cond_effs[condition].append(
                        (atom_table[lit.text()], False))
                except KeyError:
                    self.cond_effs[condition] = [
                        (atom_table[lit.text()], False)]
        for cond, lit in dels:
            if len(cond) == 0:
                effs.append((atom_table[lit.text()], True))
            else:
                condition_unfiltered = [
                    (atom_table[cond_lit.text()], cond_lit.negated) for cond_lit in cond]
                condition = []
                axioms_changed = []
                for c in condition_unfiltered:
                    if c[1] and c[0] not in self.negated_conditions:
                        has_axiom = False
                        for a in axioms:
                            if '('+atom_names[c[0]]+')' == a.name:
                                axioms_changed.append(a)
                                has_axiom = True
                        if has_axiom is False:
                            self.negated_conditions.append(c[0])
                    else:
                        condition.append(c)
                # Reencode axioms from universal quantifier introduced by the normalize.remove_universal_quantifier function
                # Remove once we add proper support for axioms
                has_axiom = False
                for a in axioms_changed:
                    has_axiom = True
                    for c in a.condition:
                        if c.negated == False:
                            self.negated_conditions.append(
                                atom_table[c.text()])
                            condition.append((atom_table[c.text()], True))
                        else:
                            condition.append((atom_table[c.text()], False))

                condition = tuple(condition)
                try:
                    self.cond_effs[condition].append(
                        (atom_table[lit.text()], True))
                except KeyError:
                    self.cond_effs[condition] = [
                        (atom_table[lit.text()], True)]

        if len(effs) > 0:
            self.effects.append(effs)
        # if len(self.cond_effs) > 0 :
        #     print( "Conditional effects: \n" )
        #     for cond, eff in self.cond_effs.iteritems() :
        #         print( "Condition: %s %s\n"%(cond,eff) )


def encode(lits, atom_table):
    encoded = []
    if isinstance(lits, pddl.Atom) or isinstance(lits, pddl.NegatedAtom):
        # singleton
        index = atom_table[lits.text()]
        encoded.append((index, lits.negated))
        return encoded

    if isinstance(lits, pddl.Conjunction):
        lits = [p for p in lits.parts]

    for p in lits:
        if isinstance(p, pddl.Assign):
            continue  # MRJ: we don't handle assigns
        try:
            index = atom_table[p.text()]
        except KeyError:
            continue
        encoded.append((index, p.negated))
    return encoded


def fodet(domain_file, problem_file, output_task):
    parsing_timer = timers.Timer()

    print("Domain: %s Problem: %s" % (domain_file, problem_file))

    with timers.timing("Parsing", True):
        task = pddl_parser.open(
            domain_filename=domain_file, task_filename=problem_file)

    with timers.timing("Normalizing task"):
        normalize.normalize(task)

    relaxed_reachable, atoms, actions, axioms, reachable_action_params = explore(
        task)
    print("goal relaxed reachable: %s" % relaxed_reachable)
    if not relaxed_reachable:
        print("No plan exists")
        sys.exit(2)

    print("%d atoms" % len(atoms))

    with timers.timing("Computing fact groups", block=True):
        groups, mutex_groups, translation_key = fact_groups.compute_groups(
            task, atoms, reachable_action_params)

    index = 0
    atom_table = {}

    atom_names = [atom.text() for atom in atoms]
    atom_names.sort()

    for atom in atom_names:
        atom_table[atom] = index
        output_task.add_atom(atom)
        index += 1

    print("Axioms %d" % len(axioms))
    for axiom in axioms:
        axiom.dump()
        output_task.add_axiom(
            encode(axiom.condition, atom_table), encode([axiom.effect], atom_table))

    print("Deterministic %d actions" % len(actions))
    nd_actions = []
    for action in actions:
        #print( "action: %s cost: %d"%(action.name,action.cost) )
        nd_action = PropositionalDetAction(action.name, action.cost)
        nd_action.set_precondition(action.precondition, atom_table)
        nd_action.add_effect(
            action.add_effects, action.del_effects, atom_table, atom_names, axioms)
        nd_actions.append((nd_action.name, nd_action))

    for name, _ in nd_actions.iteritems():
        output_task.add_action(name)

    index = 0
    for (action_name, action) in nd_actions:
        output_task.add_precondition(index, action.precondition)
        for eff in action.effects:
            output_task.add_effect(index, eff)
        # if len(action.cond_effs) != 0 :
        #    print action.name, len(action.cond_effs), "has conditional effects"
        for cond, eff in action.cond_effs.iteritems():
            output_task.add_cond_effect(index, list(cond), eff)
        output_task.set_cost(index, action.cost)
        index += 1
    output_task.set_domain_name(task.domain_name)
    output_task.set_problem_name(task.task_name)
    output_task.set_init(encode(task.init, atom_table))
    output_task.set_goal(encode(task.goal, atom_table))
    output_task.parsing_time = parsing_timer.report()


def default(domain_file, problem_file, output_task):
    parsing_timer = timers.Timer()
    print("Domain: %s Problem: %s" % (domain_file, problem_file))

    with timers.timing("Parsing", True):
        task = pddl_parser.open(
            domain_filename=domain_file, task_filename=problem_file)

    normalize.normalize(task)

    relaxed_reachable, atoms, actions, axioms, reachable_action_params = explore(
        task)
    print("goal relaxed reachable: %s" % relaxed_reachable)
    if not relaxed_reachable:
        print("No plan exists")
        sys.exit(2)

    print("%d atoms" % len(atoms))

    with timers.timing("Computing fact groups", block=True):
        groups, mutex_groups, translation_key = fact_groups.compute_groups(
            task, atoms, reachable_action_params)

    index = 0
    atom_table = {}

    atom_names = [atom.text() for atom in atoms]
    atom_names.sort()

    for atom in atom_names:
        atom_table[atom] = index
        output_task.add_atom(atom.encode('utf-8'))
        index += 1

    print("Axioms %d" % len(axioms))

    print("Deterministic %d actions" % len(actions))
    nd_actions = []
    for action in actions:
        #print( "action: %s cost: %d"%(action.name,action.cost) )
        nd_action = PropositionalDetAction(action.name, action.cost)
        nd_action.set_precondition(action.precondition, atom_table)
        nd_action.add_effect(
            action.add_effects, action.del_effects, atom_table, atom_names, axioms)
        if len(nd_action.negated_conditions) > 0:
            output_task.notify_negated_conditions(nd_action.negated_conditions)
        nd_actions.append((nd_action.name, nd_action))

    output_task.create_negated_fluents()

    for (name, _) in nd_actions:
        output_task.add_action(name.encode('utf-8'))

    index = 0
    for (_, action) in nd_actions:
        output_task.add_precondition(index, action.precondition)
        for eff in action.effects:
            output_task.add_effect(index, eff)
        # if len(action.cond_effs) != 0 :
        #    print action.name, len(action.cond_effs), "has conditional effects"
        for cond, eff in action.cond_effs.iteritems():
            #print( action.name, cond, atom_names[cond[0][0]] )

            output_task.add_cond_effect(index, list(cond), eff)

        output_task.set_cost(index, action.cost)
        index += 1

    # NIR: Default options assign 0 seconds. Change Options file to 300s to have the same configuration as FD
    # MRJ: Mutex groups processing needs to go after negations are compiled away
    print("Invariants %d" % len(mutex_groups))
    for group in mutex_groups:
        if len(group) >= 2:
            #print("{%s}" % ", ".join(map(str, group)))
            output_task.add_mutex_group(encode(group, atom_table))
            #print( encode( group, atom_table ) )

    output_task.set_domain_name(task.domain_name.encode('utf-8'))
    output_task.set_problem_name(task.task_name.encode('utf-8'))
    output_task.set_init(encode(task.init, atom_table))
    output_task.set_goal(encode(task.goal, atom_table))
    output_task.parsing_time = parsing_timer.report()

def translateToSas(task, groups, mutex_groups, translation_key, actions, axioms):
    print("INFO     Calculating sas")
    if isinstance(task.goal, pddl.Conjunction):
        goal_list = task.goal.parts
    else:
        goal_list = [task.goal]
    for item in goal_list:
        assert isinstance(item, pddl.Literal)

    with timers.timing("Building STRIPS to SAS dictionary"):
        ranges, strips_to_sas = translate.strips_to_sas_dictionary(
            groups, True)

    with timers.timing("Building dictionary for full mutex groups"):
        mutex_ranges, mutex_dict = translate.strips_to_sas_dictionary(
            mutex_groups, assert_partial=False)

    implied_facts = {}

    with timers.timing("Building mutex information", block=True):
        mutex_key = translate.build_mutex_key(strips_to_sas, mutex_groups)

    with timers.timing("Translating task", block=True):
        sas_task = translate.translate_task(
            strips_to_sas, ranges, translation_key,
            mutex_dict, mutex_ranges, mutex_key,
            task.init, goal_list, actions, axioms, task.use_min_cost_metric,
            implied_facts)

    print("%d effect conditions simplified" %
          translate.simplified_effect_condition_counter)
    print("%d implied preconditions added" %
          translate.added_implied_precondition_counter)

    with timers.timing("Detecting unreachable propositions", block=True):
        try:
            simplify.filter_unreachable_propositions(sas_task)
        except simplify.Impossible:
            return translate.unsolvable_sas_task("Simplified to trivially false goal")
        except simplify.TriviallySolvable:
            return translate.solvable_sas_task("Simplified to empty goal")

    translate.dump_statistics(sas_task)

    with timers.timing("Writing output"):
        with open("output.sas", "w") as output_file:
            sas_task.output(output_file)
    print("INFO     Sas saved to file")

def dual_translate(domain_file, problem_file, output_task):
    timer = timers.Timer()
    with timers.timing("Parsing", True):
        task = pddl_parser.open(
            domain_filename=domain_file, task_filename=problem_file)

    with timers.timing("Nomalizing task"):
        normalize.normalize(task)
    
    # JM: It should be noted here that the origin translate process
    # contain 'generate_relaxed_task' option, here I skip it.
    with timers.timing("Instantiating", block=True):
        (relaxed_reachable, atoms, actions, axioms,
        reachable_action_params) = translate.instantiate.explore(task)

    if not relaxed_reachable:
        print("No plan exists")
        sys.exit(2)

    with timers.timing("Computing fact groups", block=True):
        groups, mutex_groups, translation_key = fact_groups.compute_groups(
            task, atoms, reachable_action_params)

    index = 0
    atom_table = {}

    atom_names = [atom.text() for atom in atoms]
    atom_names.sort()

    for atom in atom_names:
        atom_table[atom] = index
        output_task.add_atom(atom.encode('utf-8'))
        index += 1

    print("Axioms %d" % len(axioms))

    print("Deterministic %d actions" % len(actions))
    nd_actions = []
    for action in actions:
        #print( "action: %s cost: %d"%(action.name,action.cost) )
        nd_action = PropositionalDetAction(action.name, action.cost)
        nd_action.set_precondition(action.precondition, atom_table)
        nd_action.add_effect(
            action.add_effects, action.del_effects, atom_table, atom_names, axioms)
        if len(nd_action.negated_conditions) > 0:
            output_task.notify_negated_conditions(nd_action.negated_conditions)
        nd_actions.append((nd_action.name, nd_action))

    output_task.create_negated_fluents()

    for (name, _) in nd_actions:
        output_task.add_action(name.encode('utf-8'))

    index = 0
    for (_, action) in nd_actions:
        output_task.add_precondition(index, action.precondition)
        for eff in action.effects:
            output_task.add_effect(index, eff)
        # if len(action.cond_effs) != 0 :
        #    print action.name, len(action.cond_effs), "has conditional effects"
        for cond, eff in action.cond_effs.iteritems():
            #print( action.name, cond, atom_names[cond[0][0]] )

            output_task.add_cond_effect(index, list(cond), eff)

        output_task.set_cost(index, action.cost)
        index += 1

    # NIR: Default options assign 0 seconds. Change Options file to 300s to have the same configuration as FD
    # MRJ: Mutex groups processing needs to go after negations are compiled away
    print("Invariants %d" % len(mutex_groups))
    for group in mutex_groups:
        if len(group) >= 2:
            #print("{%s}" % ", ".join(map(str, group)))
            output_task.add_mutex_group(encode(group, atom_table))
            #print( encode( group, atom_table ) )

    output_task.set_domain_name(task.domain_name.encode('utf-8'))
    output_task.set_problem_name(task.task_name.encode('utf-8'))
    output_task.set_init(encode(task.init, atom_table))
    output_task.set_goal(encode(task.goal, atom_table))
    output_task.parsing_time = timer.report()

    return task, groups, mutex_groups, translation_key, actions, axioms
