from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, \
    calculate_total_action_cost_metric, ground_solvable_problem
from source.utility.problem_creator import ProblemCreator
from unified_planning.shortcuts import Problem, Fluent, InstantaneousAction, BoolType, Compiler, CompilationKind #type: ignore
import unified_planning.shortcuts  # type: ignore
# import unified_planning.shortcuts as us
import sqlite3
import os
import timeit
from multiprocessing import Process, Manager, Queue
from unified_planning.engines.results import CompilerResult  # type: ignore
from source.model.plan_modifiers.exp_modifier import ExpModifier, permutation_info
from source.model.plan_modifiers.lin_modifier import LinModifier
from unified_planning.shortcuts import *
from unified_planning.io import PDDLWriter, PDDLReader #type: ignore
from source.utility.directory_scanner import DirectoryScanner
from source.utility.db_handler import DBHandler
from source.utility.problem_destroyer import ProblemDestroyer
from source.utility.file_util import remove_file
from source.utility.evaluation import eval_all, write_out_problems
from source.utility.transform_grounded import transform_grounded_problem_to_standard
from source.utility.eval_ipc2016 import load_ipc206_problems_into_database


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

def run_exception_fluent():
    

    domain_path = "evaluation/ipc2014_cleaned_benchmark//seq-agl/Childsnack_00/domain.pddl"

    problem_path = "evaluation/ipc2014_cleaned_benchmark//seq-agl/Childsnack_00/problem.pddl"
    
    problem = read_problem_from_file(domain_path, problem_path)
    writer = PDDLWriter(problem)
    print(writer.get_domain())
    #print(writer.get_problem())

    problem_grounded: Problem = ground_solvable_problem(problem).problem
    print([fluent.name for fluent in problem_grounded.fluents])
    print(problem_grounded.fluent("at_kitchen_bread"))
    problem_grounded.action("move_tray_tray3_table2_table1").add_precondition(problem_grounded.fluent("at_kitchen_bread"))

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
    file_path = "evaluation/database/eval.db"
    remove_file(file_path)
    dbh = DBHandler(file_path)
    dbh.initialize_db()

    dbh.insert_into_original_problems("domain", "original", 1 , 2)

    needed_id = dbh.find_corresponding_original_problem_id("domain", "original")
    print(dbh.get_original_problem_from_id(needed_id))
    dbh.insert_destroy_problems(needed_id ,"dm","pm", "domain_content", "problem_content")
    print(dbh.get_all_destroyed_problems())
    dbh.insert_into_results(needed_id, 1, 42, None)
    print(dbh.get_all_from_results())

    dbh.insert_into_added_preconditions(needed_id, "some_action", "some_fluent")
    print(dbh.get_all_add_preconditions())
    result_id = dbh.find_corresponding_result_id(needed_id, 1)
    dbh.insert_into_left_preconditions_results(result_id, "another_action", "another_fluent")
    print(dbh.get_all_left_preconditions_results())
    print(dbh.is_original_problem_in_database("not in", "database"))
    print(dbh.is_original_problem_in_database("domain", "original"))
    print(dbh.get_all_original_problems())
    print(dbh.get_not_used_original_problem_ids())
    dbh.remove_db_file()


def time_calc():
    start = timeit.default_timer()
    end = timeit.default_timer()
    print((end - start) * 10 ** 9)

def run_problem_destroyer():
    file_path = "evaluation/database/eval.db"
    #remove_file(file_path)
    #handler = DBHandler(file_path)
    #handler.initialize_db()
    #handler.close()
    pd = ProblemDestroyer("evaluation/database/eval.db")
    pd.load_all_problems_IPC2014()
    pd.destroy_problems()

def docker_init():
    file_path = "persist/eval.db"
    remove_file(file_path)
    db_handler = DBHandler(file_path)
    db_handler.initialize_db()

def docker_scan():
    file_path = "persist/eval.db"
    db_handler = DBHandler(file_path)
    
    #for (probelm_id, d_path, p_path, cost, time, error, longerThan30min) in db_handler.get_all_original_problems():
    #    print((probelm_id, d_path, p_path, cost, time, 'error' if error is not  None else 'fine', longerThan30min)) 
    
    #print(db_handler.get_all_original_problems())
    
    print(db_handler.get_all_destroyed_problems())
    print("_________________________________")
    print(db_handler.get_all_add_preconditions())
    db_handler.close()

def docker_look_into():
    #file_path = "evaluation/database/eval.db"
    file_path = "evaluation/baseline_destroyed/eval.db"
    #file_path = "out/evalCequals1.db"
    #file_path = "persist/eval.db"
    db_handler = DBHandler(file_path)
    print(db_handler.get_all_original_problems())
    print("====================================")
    for (id, path_domain, path_problem, content_domain, content_problem, error_text) in db_handler.get_all_destroyed_problems():
        print_tuple = (id, path_domain, path_problem, '' if error_text is None else 'error')
        print(print_tuple)
        if error_text is not None:
            error_text_str: str = error_text
            print(error_text_str.replace("|", "\n").replace("#", "\""))

    print("====================================")
    print(db_handler.get_all_add_preconditions())
    print("==========================")
    print(db_handler.get_all_from_results())
    print(db_handler.get_all_left_preconditions_results())

def run_clear_destroy_problems():
    #file_path = "evaluation/baseline_destroyed/eval.db"
    file_path = "evaluation/database/eval.db"
    db_handler = DBHandler(file_path)
    db_handler.clear_destroyed_problems()
    db_handler.clear_destroyed_problems()
    print(db_handler.get_all_original_problems())
    print(db_handler.get_all_destroyed_problems())
    print(db_handler.get_all_add_preconditions())
    db_handler.close()

def run_export_db():
    #db_file = 'evaluation/database/eval.db'
    db_file = 'out/eval.db'
    #dump_file = 'evaluation/database/dump.sql'
    dump_file = 'out/dump.sql'
    con = sqlite3.connect(db_file)
    with open(dump_file, 'w', encoding="utf-8") as f:
        for line in con.iterdump():
            f.write('%s\n' % line)
    #sh("sqlite3 #{db_file} saraksts > from_file/test.sql")

class SomeObject:
    def __init__(self):
        self.a = 1

def mutate_smth(queue: Queue) -> None:
    obj = queue.get()
    obj.a = 2
    queue.put(obj)

def run_mutate():
    smth = SomeObject()
    queue = Queue()
    queue.put(smth)
    process = Process(target= mutate_smth, args=(queue,))
    process.start()
    process.join()
    smth = queue.get()
    print(smth.a)

def run_test_eval():
    #remove file first
    db_file = "some_db_file.db"
    try:
        os.remove(db_file)
    except FileNotFoundError:
        #ignore if file does not exist
        pass

    db_handler = DBHandler(db_file)

    db_handler.initialize_db()

    #insert some problem into db
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
    problem.add_quality_metric(MinimizeActionCosts({problem.action("action1"): 1, problem.action("action2"): 1}, default=1))

    #print(problem)
    writer = PDDLWriter(problem)

    db_handler.insert_into_original_problems("1","1",2,0)
    original_id = db_handler.find_corresponding_original_problem_id("1","1")
    db_handler.insert_destroy_problems(original_id,"", "", writer.get_problem(), writer.get_domain())
    db_handler.insert_into_added_preconditions(original_id, "action1", "y")
    db_handler.close()
    
    #evaluate all
    eval_all(db_file)

    db_handler = DBHandler(db_file)
    #for (d_id, d_dom, d_prob) in db_handler.get_working_destroyed_problems():
    #    
    #    reader = PDDLReader()
    #    problem: Problem = reader.parse_problem_string(d_dom, d_prob)
    #    print(problem)
    #    print(transform_grounded_problem_to_standard(problem))
    
    print(db_handler.get_all_from_results())
    print(db_handler.get_all_left_preconditions_results())

    try:
        os.remove(db_file)
    except FileNotFoundError:
        #ignore if file does not exist
        pass

def run_import_db():
    #remove file first
    # try:
    #     os.remove('evaluation/database/eval.db')
    # except FileNotFoundError:
    #     #ignore if file does not exist
    #     pass
    db_file = "out/OUTeval.db"
    con = sqlite3.connect(db_file)
    curs = con.cursor()
    scriptdata: str= ""
    with open("out/dump_execute.sql", mode="r", encoding="utf-8") as file:
        scriptdata = file.read().rstrip()
    curs.executescript(scriptdata)

def change_db():
    db_file = "out/eval.db"
    db_handler: DBHandler = DBHandler(db_file)
    db_handler.run_command("DROP TABLE results")
    command_string: str = "CREATE TABLE results (resultID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,destroyedProblemID INTEGER NOT NULL,modifierVersionID INTEGER NOT NULL,timeInMilliseconds INTEGER,errorText TEXT,FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),FOREIGN KEY (modifierVersionID) REFERENCES modifiers(modifierVersionID))"
    db_handler.run_command(command_string)
    db_handler.close()


def run_destroy_yourself():
    #db_file = "out/eval.db"
    db_file = "tempEval.db"

    #db_handler = DBHandler(db_file)
    #db_handler.initialize_db()
    #db_handler.close()

    pd = ProblemDestroyer(db_file)
    #pd.load_all_problems_IPC2014()
    pd.load_all_problems_easy_benchmark()
    pd.destroy_problems()

def run_load_IPC2016():
    db_file = "out/evalIPC2016.db"
    db_handler = DBHandler(db_file)
    #db_handler.initialize_db()
    db_handler.close()
    load_ipc206_problems_into_database(db_file)

def run_eval_all():
    #db_file = "persist/eval.db"
    db_file = "tempEval.db"
    eval_all(db_file)

def look_at_blocksworld():
    reader = PDDLReader()
    benchmark_path = "evaluation/simple_benchmark/blocksworld/subdir1/"
    lifted_problem = transform_grounded_problem_to_standard(reader.parse_problem(benchmark_path + "domain.pddl", benchmark_path + "problem.pddl"))
    print("lifted:")
    print("amount of fluents:" + str(len(lifted_problem.fluents)))
    print("amount of initial values:" +  str(len(lifted_problem.initial_values)))
    print("amount of grounded variables:" +  str(count_grounded_variables(lifted_problem)))
    print("amount of actions:" + str(len(lifted_problem.actions)))
    grounded_problem = transform_grounded_problem_to_standard(reader.parse_problem(benchmark_path + "grounded_domain.pddl", benchmark_path + "grounded_problem.pddl"))
    print("grounded:")
    print("amount of fluents:" + str(len(grounded_problem.fluents)))
    print("amount of initial values:" +  str(len(grounded_problem.initial_values)))
    print("amount of grounded variables:" +  str(count_grounded_variables(grounded_problem)))
    print("amount of actions:" + str(len(grounded_problem.actions)))
    destroyed_problem = transform_grounded_problem_to_standard(reader.parse_problem(benchmark_path + "destroyed_domain.pddl", benchmark_path + "destroyed_problem.pddl"))
    print("destroyed:")
    print("amount of fluents:" + str(len(destroyed_problem.fluents)))
    print("amount of initial values:" +  str(len(destroyed_problem.initial_values)))
    print("amount of grounded variables:" +  str(count_grounded_variables(destroyed_problem)))
    print("amount of actions:" + str(len(destroyed_problem.actions)))
    variants_path = "out/"
    variant1_problem = transform_grounded_problem_to_standard(reader.parse_problem(variants_path + "domainExp1.pddl", variants_path + "problemExp1.pddl"))
    print("variant1:")
    print("amount of fluents:" + str(len(variant1_problem.fluents)))
    print("amount of initial values:" +  str(len(variant1_problem.initial_values)))
    print("amount of grounded variables:" +  str(count_grounded_variables(variant1_problem)))
    print("amount of actions:" + str(len(variant1_problem.actions)))
    variant2_problem = transform_grounded_problem_to_standard(reader.parse_problem(variants_path + "domainLin1.pddl", variants_path + "problemLin1.pddl"))
    print("variant2:")
    print("amount of fluents:" + str(len(variant2_problem.fluents)))
    print("amount of initial values:" +  str(len(variant2_problem.initial_values)))
    print("amount of grounded variables:" +  str(count_grounded_variables(variant2_problem)))
    print("amount of actions:" + str(len(variant2_problem.actions)))

def count_grounded_variables(problem: Problem) -> int:
    list_of_variables: list[str] = []
    for init_val in problem.initial_values:
        if str(init_val) not in list_of_variables:
            list_of_variables.append(str(init_val))
    for action in problem.actions:
        current_action: InstantaneousAction = action
        if len(current_action.parameters) != 0:
            continue
        for precon in current_action.preconditions:
            if str(precon) not in list_of_variables:
                list_of_variables.append(str(precon))
        for effect in current_action.effects:
            if str(effect.fluent) not in list_of_variables:
                list_of_variables.append(str(effect.fluent))
    for goal in problem.goals:
        if str(goal) not in list_of_variables:
            list_of_variables.append(str(goal))
    return len(list_of_variables)
     

def run_dummy_benchmark():
    db_file = "out/dummyEval.db"
    #db_file = "persist/evalSomethingReduced.db"
    db_handler = DBHandler(db_file)
    db_handler.remove_db_file()
    db_handler = DBHandler(db_file)
    db_handler.initialize_db()
    db_handler.close()
    problem_destroyer = ProblemDestroyer(db_file)
    problem_destroyer.load_all_problems_dummy_benchmark()
    problem_destroyer.destroy_problems()
    problem_destroyer.close()
    #write_out_problems(db_file)
    eval_all(db_file)
    
    db_handler = DBHandler(db_file)
    db_handler.look_into()

def create_handcrafted_problems():
    dir_path = "evaluation/dummy_benchmark"
    #dir_path = "out/handcrafted"
    ProblemCreator.create_simple_problems(dir_path)
    

def run_simple_benchmark():
    db_file = "out/simpleEval.db"
    #db_file = "persist/evalSomethingReduced.db"
    #db_handler = DBHandler(db_file)
    #db_handler.remove_db_file()
    #db_handler = DBHandler(db_file)
    #db_handler.initialize_db()
    #db_handler.close()
    #problem_destroyer = ProblemDestroyer(db_file)
    #problem_destroyer.load_all_problems_simple_benchmark()
    #problem_destroyer.destroy_problems()
    #problem_destroyer.close()
    #write_out_problems(db_file)
    eval_all(db_file)
    
    db_handler = DBHandler(db_file)
    db_handler.look_into()

def look_into():
    db_file = "evaluation/evalSomethingReduced.db"
    db_handler = DBHandler(db_file)
    db_handler.look_into()

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
    #run_exception_fluent()
    #create_handcrafted_problems()
    #run_simple_benchmark()
    #look_at_blocksworld()
    #run_mutate()
    #run_test_eval()
    #change_db()
    
    #run_load_IPC2016()

    run_dummy_benchmark()


    #some_solvable_example_with_basic_code_plus_save()
    #comparison_problem_fluents()
    #docker_init()
    #docker_scan()
    #run_destroy_yourself()
    #run_eval_all()
    
    
    #docker_look_into()
    #look_into()
    

    #run_clear_destroy_problems()
    #run_problem_destroyer()

    #run_export_db()
    #run_import_db()
    
    pass
