""" Imports"""
from uuid import uuid4
from unified_planning.shortcuts import Problem, InstantaneousAction, MinimizeActionCosts, Action,Expression, Fluent, BoolType
from .plan_modifier import PlanModifier
from .modified_plan import ModifiedProblemInfo

class ExpModifier(PlanModifier):
    """Plan Modifier actions are permuted according to its preconditions"""
    #def __init__(self, problem: Problem):
    #    PlanModifier.__init__(self, problem)
    def _transform_grounded_plan(self) -> ModifiedProblemInfo:
        #clone the problem
        problem: Problem = self.grounded_information.problem
        modified_problem = problem.clone()

        #altered problem is saturated with new actions
        modified_problem.clear_actions()

        #quality metric is created new
        modified_problem.clear_quality_metrics()
        modified_problem_cost_mapping = dict[Action, int]()

        #create mappings for backtracking later
        modified_grounded_actions_mapping = dict[str, str]()
        grounded_modified_actions_mapping = dict[str, str]()
        action_to_left_precondition_mapping = dict[str, list[Fluent]]()

        for action in problem.actions:
            if not isinstance(action, InstantaneousAction):
                raise ValueError("Given Actions must be Instantaneous")
            inst_action: InstantaneousAction = action

            #if there are no preconditions simply copy the already existing action
            if len(inst_action.preconditions) == 0:
                #create new action name
                new_action_name:str = (inst_action.name) + str(uuid4())

                #remember mapping via names
                modified_grounded_actions_mapping[new_action_name] = inst_action.name
                grounded_modified_actions_mapping[inst_action.name] = new_action_name

                #create the new action
                new_action = inst_action.clone()
                new_action._name = new_action_name

                #add action to new problem
                modified_problem.add_action(new_action)

                #set cost mapping for minimizing metric later
                modified_problem_cost_mapping[new_action] = (self.cost_mapping[inst_action.name]
                    if self.cost_mapping[inst_action.name] is not None else 0)

                continue

            create_resulting_actions(
                inst_action,
                modified_problem,
                modified_grounded_actions_mapping,
                grounded_modified_actions_mapping,
                action_to_left_precondition_mapping,
                self.cost_mapping,
                modified_problem_cost_mapping,
                self.total_action_cost
            )
        modified_problem.add_quality_metric(MinimizeActionCosts(modified_problem_cost_mapping))
        return ModifiedProblemInfo(
            modified_problem,
            grounded_modified_actions_mapping,
            modified_grounded_actions_mapping,
            action_to_left_precondition_mapping
        )


def permutation_info(permutation: list[bool]) -> tuple[int, int]:
    """
    calculate how many preconditions are left out in this permutation 
    returns (amount of used preconditions, amount left out preconditions)
    """
    used_preconditions = sum(1 for position in permutation if position)
    left_out_preconditions = len(permutation) - used_preconditions
    return (used_preconditions, left_out_preconditions)

def increase_permutation(permutation: list[bool]) -> None:
    """like adding 1 to a number increase change the permutation """
    index: int = 0
    while index < len(permutation):
        if permutation[index]:
            permutation[index] = False
            index += 1
            continue
        else:
            permutation[index] = True
            break

def create_action_according_to_permutation(
        permutation: list[bool], 
        original_action: InstantaneousAction,
        modified_grounded_actions_mapping: dict[str, str],
        grounded_modified_actions_mapping: dict[str, str],
        action_to_left_precondition_mapping: dict[str, list[Fluent]],
        cost_mapping_grounded: dict[str, int],
        modified_problem_cost_mapping: dict[Action, int],
        total_action_cost: int,
        ) -> tuple[InstantaneousAction, InstantaneousAction]:
    """
    create new entry action according to the permutation 
    while setting the appropriate actions
    returns (entry action, exit action)
    """
    #create entry to exit fluent
    entry_exit_fluent_name = "precon_entry_exit_" + original_action.name + "_" + str(uuid4())
    entry_exit_fluent = Fluent(entry_exit_fluent_name, BoolType())

    #create entry action
    entry_action_name ="entry_action_" + original_action.name + "_" + str(uuid4())
    entry_action = InstantaneousAction(entry_action_name)

    #add effect
    entry_action.add_effect(entry_exit_fluent, True)

    #create entry to map left precondition if choosing this entry
    action_to_left_precondition_mapping[entry_action_name] = []

    #set cost for entryappropriately
    amount_used_precon, left_out_precon = permutation_info(permutation)
    total_amount_of_actions_grounded_problem = len(cost_mapping_grounded)
    cost_of_entry_action = (left_out_precon
        * total_amount_of_actions_grounded_problem
        * total_action_cost)
    modified_problem_cost_mapping[entry_action] = cost_of_entry_action

    #create exit condition
    exit_action = original_action.clone()
    exit_action_name ="exit_action_" + original_action.name + "_" + str(uuid4())
    exit_action._name = exit_action_name
    exit_action.clear_preconditions()

    #add precondition for exit_action
    exit_action.add_precondition(entry_exit_fluent)

    #add mapping back to original problem
    modified_grounded_actions_mapping[exit_action_name] = original_action.name
    grounded_modified_actions_mapping[original_action.name] = exit_action_name

    #add cost for exit action
    modified_problem_cost_mapping[exit_action] = (cost_mapping_grounded[original_action.name]
        if cost_mapping_grounded[original_action.name] is not None else 0)

    #add all preconditions according to premutation
    for permutation_index, position_value in enumerate(permutation):
        current_precondition = original_action.preconditions[permutation_index]
        if position_value:
            exit_action.add_precondition(current_precondition)
        else:
            precon_list = action_to_left_precondition_mapping[entry_action_name]
            precon_list.append(current_precondition)

    return (entry_action, exit_action)


def create_resulting_actions(
        original_action: InstantaneousAction,
        modified_problem: Problem,
        modified_grounded_actions_mapping: dict[str, str],
        grounded_modified_actions_mapping: dict[str, str],
        action_to_left_precondition_mapping: dict[str, list[Fluent]],
        cost_mapping_grounded: dict[str, int],
        modified_problem_cost_mapping: dict[Action, int],
        total_action_cost: int
) -> None:
    """create all actions with all permutations of the current action """
    #create permutation | True = use precondition
    precondition_permutation: list[bool] = [False for i in range(len(original_action.preconditions))]
    all_preconditions_seen: bool = False
    #once one action is chosen only this action should be executed
    #precondition to actions mapping
    choose_preconditions = dict[Fluent, tuple[InstantaneousAction, InstantaneousAction]]()

    #go through all possible permutations
    while not all_preconditions_seen:
        
        #create actions for this iteration of permutation
        entry_action, exit_action = create_action_according_to_permutation(
            precondition_permutation,
            original_action,
            modified_grounded_actions_mapping,
            grounded_modified_actions_mapping,
            action_to_left_precondition_mapping,
            cost_mapping_grounded,
            modified_problem_cost_mapping,
            total_action_cost
        )

        #create fluent and add mapping
        choose_precondition_name = "choose_precon_" + entry_action.name
        choose_precondition = Fluent(choose_precondition_name, BoolType())
        choose_preconditions[choose_precondition] = (entry_action, exit_action)

        #all preconditions
        all_preconditions_seen = all(precondition_permutation)

        #next permutation
        increase_permutation(precondition_permutation)

    #make sure only one action can be executed
    #by adding atoms to the inital state
    #later deleting atoms when choosing an action
    for fluent, (entry_action, exit_action) in choose_preconditions.items():
        modified_problem.add_fluent(fluent, default_initial_value=True)
        entry_action.add_precondition(fluent)
        for compare_fluent in choose_preconditions.keys():
            if fluent.name == compare_fluent.name:
                continue
            entry_action.add_effect(compare_fluent, False)

        #add entry and exit actions to plan
        modified_problem.add_action(entry_action)
        modified_problem.add_action(exit_action)
