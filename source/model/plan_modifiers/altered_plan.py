"""imports for Problem """
from typing import Optional
from collections import OrderedDict
from unified_planning.model import Problem
from unified_planning.shortcuts import InstantaneousAction, Action
from unified_planning.environment import Environment
import unified_planning

class AlteredPlanInfo:
    """class to hold all info regarding the transformed problem"""
    def __init__(self, grounded_altered_actions_mapping: dict[str, str],
            altered_grounded_actions_mapping: dict[str, str],
            altered_problem: Problem):
        self.grounded_altered_actions_mapping: dict[str, str] = grounded_altered_actions_mapping
        self.altered_grounded_actions_mapping: dict[str, str] = altered_grounded_actions_mapping
        self.altered_plan: Problem = altered_problem

class AlteredAction(InstantaneousAction):
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
