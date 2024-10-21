from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, calculate_total_action_cost_metric
from unified_planning.shortcuts import *
#import unified_planning.shortcuts as us
from unified_planning.engines.results import CompilerResult
from source.model.plan_modifiers.exp_modifier import ExpModifier, cost_multiplier


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



def permutationTest():
    print(cost_multiplier([False, False, False, True]))



if __name__ == '__main__':
    #testReadInFromFile()
    #testCompiler2()
    #readInWithActionCost()
    #instantiatePlanModifier()
    permutationTest()