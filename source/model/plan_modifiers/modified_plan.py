"""imports for Problem """
from typing import Optional
from collections import OrderedDict
from unified_planning.model import Problem
from unified_planning.shortcuts import InstantaneousAction, Action, Fluent
from unified_planning.environment import Environment
import unified_planning

class ModifiedProblemInfo:
    """class to hold all info regarding the transformed problem"""
    def __init__(self,modified_problem: Problem,
            grounded_modified_actions_mapping: dict[str, str],
            modified_grounded_actions_mapping: dict[str, str],
            action_to_left_precondition_mapping: dict[str, list[Fluent]]
            ):
        self.grounded_modified_actions_mapping: dict[str, str] = grounded_modified_actions_mapping
        self.modified_grounded_actions_mapping: dict[str, str] = modified_grounded_actions_mapping
        self.problem: Problem = modified_problem
        self.action_to_left_precondition_mapping: dict[str, list[Fluent]] = action_to_left_precondition_mapping

class ModifiedAction(InstantaneousAction):
    """give additional information""" 
    def __init__(self,
        _name: str,
        _parameters:Optional[OrderedDict[str, unified_planning.model.types.Type]] = None,
        _env: Optional[Environment] = None,
        _left_precondition_index: list[int] | None = None,
        _action_reference: Action | None = None,
        **kwargs: "up.model.types.Type",):
        InstantaneousAction.__init__(_name, _parameters, _env, **kwargs)
        self.left_precondition_index: list[int] | None = _left_precondition_index
        self.action_reference: Action | None = _action_reference

class ModifiedPlanInformation():
    """info regarding the found plan"""
    def __init__(self, plan_found: bool):
        self.plan_found = plan_found
