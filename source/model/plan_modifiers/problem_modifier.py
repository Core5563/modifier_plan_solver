"""Import for abstract classes """
from abc import ABC, abstractmethod
from typing import Callable
from unified_planning.model import Problem #type: ignore
from unified_planning.shortcuts import OneshotPlanner, OptimalityGuarantee, InstantaneousAction, Fluent #type: ignore
from unified_planning.engines.results import CompilerResult, PlanGenerationResult, PlanGenerationResultStatus #type: ignore
from source.model.plan_modifiers.modifier_util import (
    read_problem_from_file, ground_problem, calculate_total_action_cost_metric, cost_leaving_precondition)
from source.model.plan_modifiers.modified_plan import ModifiedProblemInfo, ModifiedPlanInformation
from source.model.plan_modifiers.modified_plan_validator import ModifiedPlanValidator


class ProblemModifier(ABC):
    """abstract base class for modification of a Problem"""
    def __init__(self, problem: Problem, calc_leave_precon: Callable[[Problem], int] = cost_leaving_precondition):
        #remember original problem
        self.original_problem: Problem = problem
        #ground the problem
        self.grounded_information: CompilerResult = ground_problem(problem)
        #calculate and assign cost information
        _ , mapping = calculate_total_action_cost_metric(self.grounded_information.problem)
        self.cost_cut_precondition: int = calc_leave_precon(self.grounded_information.problem)
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

    @abstractmethod
    def _transform_grounded_plan(self) -> ModifiedProblemInfo:
        """create substitute plan from original plan """
        raise NotImplementedError

    def try_solving_plan(self) -> None:
        """use a planner to solve and backtrack on the modified problem """
        #Solve modified Plan
        planer = OneshotPlanner(
            problem_kind=self.modified_problem_info.problem.kind,
            optimality_guarantee=OptimalityGuarantee.SOLVED_OPTIMALLY)
        plan_results: PlanGenerationResult = planer.solve(self.modified_problem_info.problem)

        backtracked_grounded_plan_with_left_preconditions: list[InstantaneousAction] = []
        left_preconditions: dict[str, tuple[InstantaneousAction, list[Fluent]]] = (
            dict[str, tuple[InstantaneousAction, list[Fluent]]]())

        #create backtrack to plan if solvable
        if plan_results.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY:
            for action_instance in plan_results.plan.actions:
                if action_instance.action.name in self.modified_problem_info.action_to_left_precondition_mapping:
                    original_grounded_action, list_of_left_preconditions = self.modified_problem_info.action_to_left_precondition_mapping[action_instance.action.name]
                    left_preconditions[original_grounded_action.name] = list_of_left_preconditions #type: ignore
                
                if action_instance.action.name in self.modified_problem_info.modified_grounded_actions_mapping:
                    backtracked_grounded_plan_with_left_preconditions.append(self.modified_problem_info.modified_grounded_actions_mapping[action_instance.action.name])
        self.plan_info = ModifiedPlanInformation(plan_results, left_preconditions, backtracked_grounded_plan_with_left_preconditions)

        #self.plan_validator = ModifiedPlanValidator(self.plan_info, self.grounded_information.problem, self.modified_problem_info)