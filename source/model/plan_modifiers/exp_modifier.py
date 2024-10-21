""" Imports"""
from uuid import uuid4
from unified_planning.shortcuts import Problem, InstantaneousAction, MinimizeActionCosts, Action,Expression
from .plan_modifier import PlanModifier
from .altered_plan import AlteredPlanInfo

class ExpModifier(PlanModifier):
    """Plan Modifier actions are permuted according to its preconditions"""
    #def __init__(self, problem: Problem):
    #    PlanModifier.__init__(self, problem)
    def _transform_grounded_plan(self) -> AlteredPlanInfo:
        #clone the problem
        problem: Problem = self.grounded_information.problem
        altered_problem = problem.clone()
        
        #altered problem is saturated with new actions
        altered_problem.actions.clear()
        
        #quality metric is created new
        altered_problem.quality_metrics.clear()
        altered_problem_cost_mapping = dict[Action, int]()

        #create mappings for backtracking later
        altered_grounded_actions_mapping = dict[str, str]()
        grounded_altered_actions_mapping = dict[str, str]()
        
        for action in problem.actions:
            if not isinstance(action, InstantaneousAction):
                raise ValueError("Given Actions must be Instantaneous")
            inst_action: InstantaneousAction = action

            #if there are no preconditions simply copy the already existing action
            if len(inst_action.preconditions) == 0:
                #create new action name
                new_action_name = inst_action.name + uuid4()

                #remember mapping via names
                altered_grounded_actions_mapping[new_action_name] = inst_action.name
                grounded_altered_actions_mapping[inst_action.name] = new_action_name
                
                #create the new action
                new_action = inst_action.clone()
                new_action.name(new_name = new_action_name)

                #add action to new problem
                altered_problem.add_action(new_action)

                #set cost mapping for minimizing metric later
                altered_problem_cost_mapping[new_action] = (self.cost_mapping[inst_action.name]
                    if self.cost_mapping[inst_action.name] is not None else 1)

                continue

            precondition_permutation = [False for i in range(len(inst_action.preconditions))]
            
        return AlteredPlanInfo({},{},Problem())


def cost_multiplier(permutation: list[bool]) -> int:
    """calculate how many preconditions are left out in this permutation """
    return sum(1 for position in permutation if not position)

def increase_precondition(permutation: list[bool]) -> None:
    """like adding 1 to a number increase change the permutation """
    index: int = 0
    while index < len(permutation):
        if permutation[index]:
            permutation[index] = False
            continue
        else:
            permutation[index] = True
            break

def create_action_according_to_permutation(permutation: list[bool], original_action: InstantaneousAction):
    #todo implement
    pass
