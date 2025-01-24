from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, \
    calculate_total_action_cost_metric
from source.utility.problem_creator import ProblemCreator
from unified_planning.shortcuts import Problem, Fluent, InstantaneousAction, BoolType, Compiler, CompilationKind #type: ignore
import unified_planning.shortcuts  # type: ignore
# import unified_planning.shortcuts as us
import sqlite3
import os
import timeit
from unified_planning.engines.results import CompilerResult  # type: ignore
from source.model.plan_modifiers.exp_modifier import ExpModifier, permutation_info
from source.model.plan_modifiers.lin_modifier import LinModifier
from unified_planning.shortcuts import *
from unified_planning.io import PDDLWriter, PDDLReader #type: ignore
from source.utility.directory_scanner import DirectoryScanner
from source.utility.db_handler import DBHandler
from source.utility.problem_destroyer import ProblemDestroyer



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
        [("x", True), ("y", False), ("z", False), ("p", False), ("q", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True), ("q", False)]),
            ("a2", ["z"], [("q", True), ("p", False)])
        ],
        ["p", "q"]
    )
    pm = ExpModifier(problem)
    pm.try_solving_plan()
    print(pm.plan_info.plan_results.status)

def basic_unsolvable_solvable():
    #problem = ProblemCreator.create_problem(
    #    [
    #        ("x", True),
    #        ("y", False),
    #        ("z", False),
    #        ("p", False),
    #        ("q", False)
    #    ],
    #    [
    #        ("a1", ["x", "y"], [("z", True), ("p", True)]),
    #        ("a2", ["z"], [("q", True)])
    #    ],
    #    ["p", "q"]
    #)
    problem = Problem()
    #variables
    x = Fluent("x", BoolType())
    y = Fluent("y", BoolType())
    z = Fluent("z", BoolType())
    p = Fluent("p", BoolType())
    q = Fluent("q", BoolType())
    #add variables and set initial values
    problem.add_fluent(x, default_initial_value=True)
    problem.add_fluent(y, default_initial_value=False)
    problem.add_fluent(z, default_initial_value=False)
    problem.add_fluent(p, default_initial_value=False)
    problem.add_fluent(q, default_initial_value=False)
    #add goals
    problem.add_goal(p)
    problem.add_goal(q)
    #actions
    a1 = InstantaneousAction("a1")
    a1.add_precondition(x)
    a1.add_precondition(y)
    a1.add_effect(z, True)
    a1.add_effect(p, True)
    problem.add_action(a1)
    a2 = InstantaneousAction("a2")
    a2.add_precondition(z)
    a2.add_effect(q, True)
    problem.add_action(a2)


    pm = LinModifier(problem)
    pm.try_solving_plan()
    print("original problem")
    print(pm.original_problem)
    #print(pm.modified_problem_info.problem)
    print("grounded information")
    print(pm.grounded_information)
    print("")
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


def write_problem_read_problem_test():
    Location = UserType('Location')

    robot_at = unified_planning.model.Fluent('robot_at', BoolType(), l=Location)
    connected = unified_planning.model.Fluent('connected', BoolType(), l_from=Location, l_to=Location)

    move = InstantaneousAction('move', l_from=Location, l_to=Location)
    l_from = move.parameter('l_from')
    l_to = move.parameter('l_to')
    move.add_precondition(connected(l_from, l_to))
    move.add_precondition(robot_at(l_from))
    move.add_effect(robot_at(l_from), False)
    move.add_effect(robot_at(l_to), True)

    problem = Problem('robot')
    problem.add_fluent(robot_at, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_action(move)

    NLOC = 10
    locations = [Object('l%s' % i, Location) for i in range(NLOC)]
    problem.add_objects(locations)

    problem.add_goal(robot_at(locations[-1]))


    compiler: Compiler = Compiler(problem_kind=problem.kind, compilation_kind=CompilationKind.GROUNDING)#, params={"remove_statics_from_initial_state=True": 'False', 'remove_irrelevant_operators': "False"})

    compiler_result: CompilerResult = compiler.compile(
        problem,
        compilation_kind=CompilationKind.GROUNDING)
    
    grounded_problem = compiler_result.problem
    print("grounded")
    print(grounded_problem)

    writer = PDDLWriter(grounded_problem)
    writer.write_domain("domain_test_file.pddl")
    writer.write_problem("problem_test_file.pddl")

    reader = PDDLReader()
    expected_problem = reader.parse_problem(domain_filename="domain_test_file.pddl",problem_filename="problem_test_file.pddl")
    print("expected")
    print(expected_problem)

def some_solvable_example_with_basic_code_plus_save():
    problem = Problem()
    #variables
    x = Fluent("x", BoolType())
    y = Fluent("y", BoolType())
    z = Fluent("z", BoolType())
    p = Fluent("p", BoolType())
    q = Fluent("q", BoolType())
    #add variables and set initial values
    problem.add_fluent(x, default_initial_value=True)
    problem.add_fluent(y, default_initial_value=True)
    problem.add_fluent(z, default_initial_value=False)
    problem.add_fluent(p, default_initial_value=False)
    problem.add_fluent(q, default_initial_value=False)
    #add goals
    problem.add_goal(p)
    problem.add_goal(q)
    #actions
    a1 = InstantaneousAction("a1")
    a1.add_precondition(x)
    a1.add_precondition(y)
    a1.add_effect(z, True)
    a1.add_effect(p, True)
    problem.add_action(a1)
    a2 = InstantaneousAction("a2")
    a2.add_precondition(z)
    a2.add_effect(q, True)
    problem.add_action(a2)

    #ground problem
    #compiler = Compiler(name ="pyperplan")
    compiler = Compiler(name ="up_grounder", params={"prune_actions": False})

    compiler_result = compiler.compile(problem, compilation_kind = CompilationKind.GROUNDING)

    to_save_problem = compiler_result.problem
    writer = PDDLWriter(to_save_problem)
    writer.write_domain("evaluation/easy_benchmark/subfolder1/subfolder2/domain.pddl")
    writer.write_problem("evaluation/easy_benchmark/subfolder1/subfolder2/problem.pddl")

def comparison_problem_fluents():
    problem = Problem()
    #variables
    x = Fluent("x", BoolType())
    y = Fluent("y", BoolType())
    z = Fluent("z", BoolType())
    p = Fluent("p", BoolType())
    q = Fluent("q", BoolType())
    #add variables and set initial values
    problem.add_fluent(x, default_initial_value=True)
    problem.add_fluent(y, default_initial_value=False)
    problem.add_fluent(z, default_initial_value=False)
    problem.add_fluent(p, default_initial_value=False)
    problem.add_fluent(q, default_initial_value=False)
    #add goals
    problem.add_goal(p)
    problem.add_goal(q)
    #actions
    a1 = InstantaneousAction("a1")
    a1.add_precondition(x)
    a1.add_precondition(y)
    a1.add_effect(z, True)
    a1.add_effect(p, True)
    problem.add_action(a1)
    a2 = InstantaneousAction("a2")
    a2.add_precondition(z)
    a2.add_effect(q, True)
    problem.add_action(a2)

    c1 = False
    for initial_value_key, value in problem.initial_values.items():
        print(initial_value_key.fluent().name + " " + str(not value.is_false()))
    print("1: " + str())
    for action in problem.actions:
        print(action.name)
        current_action: InstantaneousAction = action
        for precon in current_action.preconditions:
            print(precon.fluent().name)
        for effect in current_action.effects:
            print(effect.fluent.fluent().name + " " + str(effect.value))
    for goal in problem.goals:
        print(goal.fluent().name)


def some_unsolvable_example_with_basic_code():
    problem = Problem()
    #variables
    x = Fluent("x", BoolType())
    y = Fluent("y", BoolType())
    z = Fluent("z", BoolType())
    p = Fluent("p", BoolType())
    q = Fluent("q", BoolType())
    #add variables and set initial values
    problem.add_fluent(x, default_initial_value=True)
    problem.add_fluent(y, default_initial_value=False)
    problem.add_fluent(z, default_initial_value=False)
    problem.add_fluent(p, default_initial_value=False)
    problem.add_fluent(q, default_initial_value=False)
    #add goals
    problem.add_goal(p)
    problem.add_goal(q)
    #actions
    a1 = InstantaneousAction("a1")
    a1.add_precondition(x)
    a1.add_precondition(y)
    a1.add_effect(z, True)
    a1.add_effect(p, True)
    problem.add_action(a1)
    a2 = InstantaneousAction("a2")
    a2.add_precondition(z)
    a2.add_effect(q, True)
    problem.add_action(a2)

    #ground problem
    #compiler = Compiler(name ="pyperplan")
    compiler = Compiler(name ="up_grounder", params={"prune_actions": False})

    compiler_result = compiler.compile(problem, compilation_kind = CompilationKind.GROUNDING)

    print(compiler_result.problem)

def run_directory_scan():
    dir_scanner = DirectoryScanner()
    for result in dir_scanner.scan_benchmark('./evaluation/ipc2014_cleaned_benchmark'):
        print(result.domain_dir)

def run_db_stuff():
    #remove file first
    try:
        os.remove('evaluation/database/eval.db')
    except FileNotFoundError:
        #ignore if file does not exist
        pass

    con = sqlite3.connect('evaluation/database/eval.db')
    curs = con.cursor()
    scriptdata: str= ""
    with open("evaluation/database/setup.sql", mode="r", encoding="utf-8") as file:
        scriptdata = file.read().rstrip()
    curs.executescript(scriptdata)

def run_db_handler():
    dbh = DBHandler("evaluation/database/eval.db")
    dbh.insert_into_original_problems("domain", "original", 1 , 2)

    needed_id = dbh.find_corresponding_original_problem_id("domain", "original")
    print(dbh.get_original_problem_from_id(needed_id))
    dbh.insert_destroy_problems(needed_id ,"dm","pm", "domain_content", "problem_content")
    print(dbh.get_all_destroyed_problems())
    dbh.insert_into_results(needed_id, 4, 42)
    print(dbh.get_all_from_results())

    dbh.insert_into_added_preconditions(needed_id, "some_action", "some_fluent")
    print(dbh.get_all_add_preconditions())
    result_id = dbh.find_corresponding_result_id(needed_id, 4, 42)
    dbh.insert_into_left_preconditions_results(result_id, "another_action", "another_fluent")
    print(dbh.get_all_left_preconditions_results())
    dbh.remove_db_file()


def time_calc():
    start = timeit.default_timer()
    end = timeit.default_timer()
    print((end - start) * 10 ** 9)

def run_problem_destroyer():
    pd = ProblemDestroyer()
    pd.load_all_problems()
    
    pd.destroy_problems()


if __name__ == '__main__':
    # readInWithActionCost()
    # instantiatePlanModifier()
    # permutationTest()
    #basic_example()
    #basic_unsolvable()
    #run_modifier()
    #run_next()
    #basic_unsolvable_solvable()
    #write_problem_read_problem_test()
    #some_unsolvable_example_with_basic_code()
    #run_directory_scan()
    #run_db_stuff()
    #run_db_handler()
    #time_calc()
    
    run_problem_destroyer()
    #some_solvable_example_with_basic_code_plus_save()
    #comparison_problem_fluents()
