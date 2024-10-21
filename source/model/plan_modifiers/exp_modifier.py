""" Imports"""
from unified_planning.shortcuts import Problem, InstantaneousAction
from .plan_modifier import PlanModifier
from .altered_plan import AlteredPlanInfo

class ExpModifier(PlanModifier):
    """Plan Modifier actions are permutated according to its preconditions"""
    #def __init__(self, problem: Problem):
    #    PlanModifier.__init__(self, problem)
    def _transform_grounded_plan(self) -> AlteredPlanInfo:
        #clone the problem
        problem: Problem = self.grounded_information.problem
        altered_problem = problem.clone()
        #altered problem is saturated with new actions
        altered_problem.actions.clear()
        altered_problem.quality_metrics.clear()
        altered_grounded_actions_mapping = dict[str, str]()
        grounded_altered_actions_mapping = dict[str, str]()
        action_index = 0
        for action in problem.actions:
            if not isinstance(action, InstantaneousAction):
                raise ValueError("Given Actions must be Instantaneous")
            inst_action: InstantaneousAction = action
            if(len(inst_action.preconditions) == 0):
                #todo finish
                new_action_name = inst_action.name + str(action_index)
                altered_grounded_actions_mapping[new_action_name] = inst_action.name
                grounded_altered_actions_mapping[inst_action.name] = new_action_name
                action_index += 1
                #new_action
                continue
            precondition_permutation = [False for i in range(len(inst_action.preconditions))]
            
        return AlteredPlanInfo({},{},Problem())


