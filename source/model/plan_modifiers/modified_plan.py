"""imports for Problem """
from typing import Optional
from collections import OrderedDict
from unified_planning.model import Problem
from unified_planning.engines import PlanGenerationResult
from unified_planning.shortcuts import InstantaneousAction, Action, Fluent
from unified_planning.environment import Environment
import unified_planning

class ModifiedProblemInfo:
    """class to hold all info regarding the transformed problem"""
    def __init__(
            self, modified_problem: Problem,
            modified_grounded_actions_mapping: dict[str, str],
            action_to_left_precondition_mapping: dict[str, tuple[InstantaneousAction, list[Fluent]]],
            name_to_action: dict[str, InstantaneousAction]
            ):
        self.modified_grounded_actions_mapping: dict[str, str] = modified_grounded_actions_mapping
        self.problem: Problem = modified_problem
        self.action_to_left_precondition_mapping: dict[str, tuple[InstantaneousAction, list[Fluent]]] = action_to_left_precondition_mapping
        self.name_to_action: dict[str, InstantaneousAction] = name_to_action

class ModifiedPlanInformation():
    """info regarding the found plan"""
    def __init__(
            self,
            plan_results: PlanGenerationResult,
            left_preconditions: dict[str, tuple[InstantaneousAction, list[Fluent]]],
            backtracked_grounded_plan_result: list[InstantaneousAction]):
        #result from planner
        self.plan_results: PlanGenerationResult = plan_results
        #preconditions left based on actions
        #name -> (action, left_preconditions as list)
        self.left_preconditions: dict[str, tuple[InstantaneousAction, list[Fluent]]] = left_preconditions
        #list starting from first Action determining which action is actually used
        self.backtracked_grounded_plan_result: list[InstantaneousAction] = backtracked_grounded_plan_result
