import traceback
import time
from unified_planning.shortcuts import OneshotPlanner, Problem #type:ignore
from unified_planning.engines import PlanGenerationResult, CompilerResult #type: ignore
from source.model.plan_modifiers.modifier_util import ground_solvable_problem


def solve_problem_with_multithreading(problem: Problem, return_dict: dict[int, PlanGenerationResult]) -> None:
    """solve with fast-downward planner"""
    planner = OneshotPlanner(name="fast-downward")
    solution = planner.solve(problem)
    return_dict[0] = solution

def solve_problem_with_multithreading_and_time_calc(
        problem: Problem,
        return_result: dict[int, PlanGenerationResult],
        return_time: dict[int, int],
        return_error: dict[int,str]):
    """solve with fast-downward planner measuring the time"""
    planner = OneshotPlanner(name="fast-downward")
    start = time.perf_counter_ns()
    try:
        solution = planner.solve(problem)
    except Exception:
        error_text = traceback.format_exc()
        return_error[0] = error_text
        return
    end = time.perf_counter_ns()
    
    return_result[0] = solution
    return_time[0] = start
    return_time[1] = end

def ground_solvable_problem_multithread(problem: Problem, return_dict: dict[int, CompilerResult], error_dict: dict[int, str])-> None:
    """ground Problem with multithreading"""
    to_return = ground_solvable_problem(problem)
    return_dict[0] = to_return