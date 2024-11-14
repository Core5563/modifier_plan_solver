from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, \
    calculate_total_action_cost_metric
from source.utility.problem_creator import ProblemCreator
import unified_planning.shortcuts  # type: ignore
# import unified_planning.shortcuts as us
from unified_planning.engines.results import CompilerResult  # type: ignore
from source.model.plan_modifiers.exp_modifier import ExpModifier, permutation_info
from source.model.plan_modifiers.lin_modifier import LinModifier


def runReadInFromFile():
    problem = read_problem_from_file('example_files/domain_simple_solvableA.pddl',
                                     'example_files/problem_simple_solvableA.pddl')
    print(problem)


def useCompiler2():
    # problem = read_problem_from_file('example_files/domain_simple_solvableA.pddl', 'example_files/problem_simple_solvableA.pddl')
    # problem = read_problem_from_file('example_files/action_cost/domain_missing_action_cost_decision.pddl', 'example_files/action_cost/problem_missing_action_cost_decision.pddl')
    problem = read_problem_from_file('example_files/action_cost/domain_action_cost_exampleA.pddl',
                                     'example_files/action_cost/problem_action_cost_exampleA.pddl')
    result = ground_problem(problem)
    total, action_dict = calculate_total_action_cost_metric(result.problem)
    print(total)
    print(len(action_dict))
    # print(result.map_back_action_instance)
    # print(result.problem)
    print(result.problem.quality_metrics)


def readInWithActionCost():
    problem = read_problem_from_file('example_files/action_cost/domain_missing_action_cost_decision.pddl',
                                     'example_files/action_cost/problem_missing_action_cost_decision.pddl')
    grounded_problem = ground_problem(problem)

    print(grounded_problem.problem)
    planner = unified_planning.shortcuts.OneshotPlanner(problem_kind=grounded_problem.problem.kind,
                                                        optimality_guarantee=unified_planning.shortcuts.OptimalityGuarantee.SOLVED_OPTIMALLY)
    print(planner.solve(grounded_problem.problem))


def instantiatePlanModifier():
    problem = read_problem_from_file('example_files/action_cost/domain_action_cost_exampleA.pddl',
                                     'example_files/action_cost/problem_action_cost_exampleA.pddl')
    pm = ExpModifier(problem)
    print(pm.original_problem)
    print(pm.grounded_information.problem)
    print(pm.modified_problem_info.problem)


def run_permutation():
    print(permutation_info([True, True, True, True]))


def basic_example():
    problem = unified_planning.shortcuts.Problem()
    # atoms
    x = unified_planning.shortcuts.Fluent("x", unified_planning.shortcuts.BoolType())
    y = unified_planning.shortcuts.Fluent("y", unified_planning.shortcuts.BoolType())
    z = unified_planning.shortcuts.Fluent("z", unified_planning.shortcuts.BoolType())
    p = unified_planning.shortcuts.Fluent("p", unified_planning.shortcuts.BoolType())
    q = unified_planning.shortcuts.Fluent("q", unified_planning.shortcuts.BoolType())
    # define actions
    action1 = unified_planning.shortcuts.InstantaneousAction("action1")
    action1.add_precondition(x)
    action1.add_precondition(y)
    action1.add_effect(x, False)
    action1.add_effect(y, False)
    action1.add_effect(z, True)
    action1.add_effect(p, True)
    action2 = unified_planning.shortcuts.InstantaneousAction("action2")
    action2.add_precondition(z)
    action2.add_effect(z, False)

    action2.add_effect(q, True)
    # add actions
    problem.add_action(action1)
    problem.add_action(action2)
    # initial values
    problem.add_fluent(x, default_initial_value=True)
    problem.add_fluent(y, default_initial_value=False)
    problem.add_fluent(z, default_initial_value=False)
    problem.add_fluent(p, default_initial_value=False)
    problem.add_fluent(q, default_initial_value=False)
    # goal
    problem.add_goal(p)
    problem.add_goal(q)

    pm = ExpModifier(problem)
    #pm = LinModifier(problem)
    # print(pm.modified_problem_info.action_to_left_precondition_mapping)
    # print(pm.modified_problem_info.modified_grounded_actions_mapping)
    print(pm.modified_problem_info.problem)
    pm.try_solving_plan()
    print(pm.plan_info.plan_results.plan.kind)
    print(pm.plan_info.plan_results.plan.actions)
    print(pm.plan_info.backtracked_grounded_plan_result)
    print(pm.plan_info.left_preconditions)
    print(pm.plan_info.plan_to_str())


def basic_unsolvable():
    problem = ProblemCreator.create_problem(
        [("x", True), ("y", False), ("z", False), ("p", False), ("q", False), "wrong"],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True), ("q", False)]),
            ("a2", ["z"], [("q", True), ("p", False)])
        ],
        ["p", "q"]
    )
    pm = ExpModifier(problem)
    pm.try_solving_plan()
    print(pm.plan_info.plan_results.status)

def run_modifier():
    problem = ProblemCreator.create_problem(
        [
            ("x", True),
            ("y", True),
            ("z", True),
            ("u", False),
            ("v", False),
            ("w", False),
            ("q", False),
            ("p", False),
            ("d", False)
        ],
        [
            ("a1", ["x", "y"], [("z", True), ("q", True)]),
            ("a2", ["z"], [("u", True), ("p", True)]),
            ("a3", ["x", "y", "z", "u"], [("z", False), ("v", True), ("w", True)]),
            ("a4", [], [("z", False)]),
            ("a5", ["x", "y"], [("z", False)])
         ],
        ["p", "q", "v", "w"]
    )
    pm = ExpModifier(problem)

def run_next():
    mylist = iter([1,2,3])
    x = next(mylist)
    print(x)
    x = next(mylist)
    print(x)
    x = next(mylist)
    print(x)


if __name__ == '__main__':
    # readInWithActionCost()
    # instantiatePlanModifier()
    # permutationTest()
    #basic_example()
    #basic_unsolvable()
    run_modifier()
    #run_next()
