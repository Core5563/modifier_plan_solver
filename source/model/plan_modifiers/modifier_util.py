"""import for reading in files"""
from typing import Tuple
from unified_planning.io import PDDLReader
from unified_planning.model import Problem
from unified_planning.shortcuts import Compiler, CompilationKind
from unified_planning.engines.results import CompilerResult
from unified_planning.model.metrics import MinimizeActionCosts


def read_problem_from_file(domain_filepath:str, problem_filepath:str) -> Problem:
    """read in Problem from .pddl domain and problem file """
    reader = PDDLReader()
    return reader.parse_problem(domain_filepath, problem_filepath)


def ground_problem(problem: Problem) -> CompilerResult:
    """
    reduce the problem to basic STRIPS and retain information to map back the actions to 
    the original problem
    """
    compiler: Compiler = Compiler(problem_kind = problem.kind,
        compilation_kind = CompilationKind.GROUNDING)
    compiler_result: CompilerResult = compiler.compile(problem,
        compilation_kind = CompilationKind.GROUNDING)
    return compiler_result


def calculate_total_action_cost_metric(problem: Problem) -> Tuple[int, dict[str, int]]:
    """
    calculates all information regarding the action cost
    returns (total actions cost, action cost mapping (name -> cost))
    """
    total_cost: int = 0
    has_action_cost_metric: bool = False
    action_cost_metric: MinimizeActionCosts
    action_cost_mapping = dict[str, int]()
    #check if action cost metric is there
    if problem.quality_metrics is not None:
        for metric in problem.quality_metrics:
            if isinstance(metric, MinimizeActionCosts):
                has_action_cost_metric = True
                action_cost_metric = metric
                break

    for action in problem.actions:
        #increase actions by amount if action cost is set
        #otherwise all actions are set to a cost of 1
        if has_action_cost_metric:

            #check if mapping is there and if not check if default can be used
            action_cost: int = 0
            if action_cost_metric.get_action_cost(action) is not None:
                action_cost = int(str(action_cost_metric.get_action_cost(action)))
                continue
            else:
                if action_cost_mapping.default is not None:
                    action_cost = action_cost_mapping.default
            action_cost_mapping[action.name] = action_cost
            total_cost += action_cost
        else:
            action_cost_mapping[action.name] = 1
            total_cost += 1
    return (total_cost, action_cost_mapping)


def cost_leaving_precondition(problem: Problem) -> int:
    """action"""
    total_action_cost , mapping = calculate_total_action_cost_metric(problem)
    return (total_action_cost * len(mapping))
