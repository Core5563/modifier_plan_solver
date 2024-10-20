""" Imports"""
from unified_planning.shortcuts import Problem, Action, InstantaneousAction
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

        for action in problem.actions:
            if not isinstance(action, InstantaneousAction):
                raise Exception("Given Actions must be Instantaneous")
                continue
            inst_action: InstantaneousAction = action
            if(len(inst_action.preconditions) == 0):
                #todo finish
                pass
            precondition_permutation = [False for i in range(len(inst_action.preconditions))]
            

            


        return AlteredPlanInfo({},{},Problem())
