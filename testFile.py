from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, calculate_total_action_cost_metric
from unified_planning.shortcuts import *
#import unified_planning.shortcuts as us
from unified_planning.engines.results import CompilerResult
from source.model.plan_modifiers.exp_modifier import ExpModifier, permutation_info


def testReadInFromFile():
    problem = read_problem_from_file('example_files/domain_simple_solvableA.pddl', 'example_files/problem_simple_solvableA.pddl')
    print(problem)

def testCompiler2():
    #problem = read_problem_from_file('example_files/domain_simple_solvableA.pddl', 'example_files/problem_simple_solvableA.pddl')
    #problem = read_problem_from_file('example_files/action_cost/domain_missing_action_cost_decision.pddl', 'example_files/action_cost/problem_missing_action_cost_decision.pddl')
    problem = read_problem_from_file('example_files/action_cost/domain_action_cost_exampleA.pddl', 'example_files/action_cost/problem_action_cost_exampleA.pddl')
    result = ground_problem(problem)
    total , action_dict= calculate_total_action_cost_metric(result.problem)
    print(total)
    print(len(action_dict))
    #print(result.map_back_action_instance)
    #print(result.problem)
    print(result.problem.quality_metrics)

def readInWithActionCost():
    problem = read_problem_from_file('example_files/action_cost/domain_missing_action_cost_decision.pddl', 'example_files/action_cost/problem_missing_action_cost_decision.pddl')
    grounded_problem = ground_problem(problem)
    
    print(grounded_problem.problem)
    planner = OneshotPlanner(problem_kind=grounded_problem.problem.kind, optimality_guarantee=OptimalityGuarantee.SOLVED_OPTIMALLY)
    print(planner.solve(grounded_problem.problem))



def instantiatePlanModifier():
    problem = read_problem_from_file('example_files/action_cost/domain_action_cost_exampleA.pddl', 'example_files/action_cost/problem_action_cost_exampleA.pddl')
    pm = ExpModifier(problem)
    print(pm.original_problem)
    print(pm.grounded_information.problem)
    print(pm.modified_problem_info.problem)



def permutationTest():
    print(permutation_info([True, True, True ,True]))

def basic_example():
    problem = Problem()
    #atoms
    x = Fluent("x", BoolType())
    y = Fluent("y", BoolType())
    z = Fluent("z", BoolType())
    p = Fluent("p", BoolType())
    q = Fluent("q", BoolType())
    #define actions
    action1 = InstantaneousAction("action1")
    action1.add_precondition(x)
    action1.add_precondition(y)
    action1.add_effect(x, False)
    action1.add_effect(y, False)
    action1.add_effect(z, True)
    action1.add_effect(p, True)
    action2 = InstantaneousAction("action2")
    action2.add_precondition(z)
    action2.add_effect(z, False)

    action2.add_effect(q, True)
    #add actions
    problem.add_action(action1)
    problem.add_action(action2)
    #initial values
    problem.add_fluent(x, default_initial_value = True)
    problem.add_fluent(y, default_initial_value = False)
    problem.add_fluent(z, default_initial_value = False)
    problem.add_fluent(p, default_initial_value = False)
    problem.add_fluent(q, default_initial_value = False)
    #goal
    problem.add_goal(p)
    problem.add_goal(q)
    
    pm = ExpModifier(problem)
    #print(pm.modified_problem_info.action_to_left_precondition_mapping)
    #print(pm.modified_problem_info.modified_grounded_actions_mapping)
    #print(pm.modified_problem_info.grounded_modified_actions_mapping)
    #print(pm.modified_problem_info.problem)
    pm.try_solving_plan()
    print(pm.plan_info.plan_results.plan.kind)
    print(pm.plan_info.plan_results.plan.actions)
    print(pm.plan_info.backtracked_grounded_plan_result)
    print(pm.plan_info.left_preconditions)
    print(pm.plan_info.plan_to_str())
    
    #planer = OneshotPlanner(problem_kind=problem.kind, optimality_guarantee=OptimalityGuarantee.SATISFYING)
    #plan_result = planer.solve(problem)
    
    #planer = OneshotPlanner(problem_kind=pm.modified_problem_info.problem.kind, optimality_guarantee=OptimalityGuarantee.SOLVED_OPTIMALLY)
    #plan_result = planer.solve(pm.modified_problem_info.problem)
    #print(plan_result)
    pass



if __name__ == '__main__':
    #testReadInFromFile()
    #testCompiler2()
    #readInWithActionCost()
    #instantiatePlanModifier()
    #permutationTest()
    basic_example()
