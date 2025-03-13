"""Import for abstract classes """
import sys
from abc import ABC, abstractmethod
from typing import Callable
from unified_planning.model import Problem #type: ignore
from unified_planning.shortcuts import OneshotPlanner, InstantaneousAction, Fluent, OptimalityGuarantee, FNode #type: ignore
from unified_planning.engines.results import CompilerResult, PlanGenerationResult, PlanGenerationResultStatus #type: ignore
from source.model.plan_modifiers.modifier_util import (
    read_problem_from_file, ground_problem, calculate_total_action_cost_metric, cost_leaving_precondition, read_problem_from_text)
from source.model.plan_modifiers.modified_plan import ModifiedProblemInfo, ModifiedPlanInformation
from source.model.plan_modifiers.modified_plan_validator import ModifiedPlanValidator
from source.utility.transform_grounded import transform_grounded_problem_to_standard, find_corresponding_action_in_left_preconditions
from unified_planning.io import PDDLReader, PDDLWriter

class ProblemModifier(ABC):
    """abstract base class for modification of a Problem"""
    def __init__(self, problem: Problem, calc_leave_precon: Callable[[Problem], int] = cost_leaving_precondition, is_grounded: bool = False):
        #remember original problem
        self.original_problem: Problem = problem

        #ground the problem
        self.grounded_problem: Problem = Problem()
        if is_grounded:
            self.grounded_problem = self.original_problem
        else:
            self.grounded_information: CompilerResult = ground_problem(problem)
            self.grounded_problem = self.grounded_information.problem
        self.grounded_problem = transform_grounded_problem_to_standard(self.grounded_problem)

        #calculate and assign cost information
        _ , mapping = calculate_total_action_cost_metric(self.grounded_problem)
        self.cost_cut_precondition: int = calc_leave_precon(self.grounded_problem)
        self.cost_mapping: dict[str, int] = mapping
        #create altered plan
        self.modified_problem_info: ModifiedProblemInfo = self._transform_grounded_plan()

        #create object for plan solving
        self.plan_info: ModifiedPlanInformation | None = None
        #create object for plan verification
        self.plan_validator: ModifiedPlanValidator | None = None

    @classmethod
    def from_file(cls, domain_filepath: str, problem_filepath: str):
        """create object from domain and problem files"""
        problem = read_problem_from_file(domain_filepath, problem_filepath)
        return cls(problem)


    @classmethod
    def from_text(cls, domain_string: str, problem_string: str):
        """create object from domain and problem files"""
        problem = read_problem_from_text(domain_string, problem_string)
        return cls(problem)

    @classmethod
    def from_text_eval(cls, domain_string: str, problem_string: str):
        """create object from domain and problem files"""
        problem = read_problem_from_text(domain_string, problem_string)
        return cls(problem, is_grounded=True)

    @abstractmethod
    def _transform_grounded_plan(self) -> ModifiedProblemInfo:
        """create substitute plan from original plan """
        raise NotImplementedError

    def try_solving_plan(self) -> None:
        """use a planner to solve and backtrack on the modified problem """
        #Solve modified Plan
        #perform transformation steps
        writer = PDDLWriter(self.modified_problem_info.problem)
        reader = PDDLReader()
        problem_to_solve = reader.parse_problem_string(writer.get_domain(), writer.get_problem())

        params = {
            'fast_downward_translate_options': ['--invariant-generation-max-candidates', '0'],
            'fast_downward_search_config': 'astar(lmcut())'
        }
        planer = OneshotPlanner(name="fast-downward", params=params)
        
        plan_results: PlanGenerationResult = planer.solve(self.modified_problem_info.problem)

        backtracked_grounded_plan_with_left_preconditions: list[InstantaneousAction] = []
        left_preconditions: dict[str, list[Fluent]] = dict[str, list[FNode]]()

        #create backtrack to plan if solvable
        if plan_results.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY or plan_results.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            for action_instance in plan_results.plan.actions:
                if action_instance.action.name in self.modified_problem_info.action_to_left_precondition_mapping:
                    original_grounded_action, list_of_left_preconditions = \
                        self.modified_problem_info.action_to_left_precondition_mapping[action_instance.action.name]
                    left_preconditions[original_grounded_action.name] = list_of_left_preconditions #type: ignore
                
                if action_instance.action.name in self.modified_problem_info.modified_grounded_actions_mapping:
                    backtracked_grounded_plan_with_left_preconditions.append(self.modified_problem_info.modified_grounded_actions_mapping[action_instance.action.name])
        self.plan_info = ModifiedPlanInformation(plan_results, left_preconditions, backtracked_grounded_plan_with_left_preconditions)

        #self.plan_validator = ModifiedPlanValidator(self.plan_info, self.grounded_problem, self.modified_problem_info)