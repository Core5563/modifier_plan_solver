from uuid import uuid4
from unified_planning.shortcuts import Action, InstantaneousAction, Problem, Fluent, BoolType, MinimizeActionCosts #type: ignore
from .plan_modifier import PlanModifier
from .modified_plan import ModifiedProblemInfo

class LinModifier(PlanModifier):
    """creates Modified Plan by adding actions linear to preconditions """
    def  _transform_grounded_plan(self) -> ModifiedProblemInfo:
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
        action_to_left_precondition_mapping = dict[str, tuple[InstantaneousAction, list[Fluent]]]()
        name_to_action = dict[str, InstantaneousAction]()

        #create dictionary with first entries for fluents
        precon_to_changed_precon: dict[str, tuple[Fluent, list[Fluent]]] = dict[str, tuple[Fluent, list[Fluent]]]()
        negative_effect_mapping: dict[str, tuple[Fluent, list[InstantaneousAction]]] = (
            dict[str, tuple[Fluent, list[InstantaneousAction]]]())

        for fluent in problem.fluents:
            precon_to_changed_precon[str(fluent.name)] = (fluent, [])
            negative_effect_mapping[str(fluent.name)] = (fluent, [])

        for action in problem.actions:
            if not isinstance(action, InstantaneousAction):
                raise ValueError("Given Actions must be Instantaneous")
            inst_action: InstantaneousAction = action
            created_actions = create_resulting_actions(
                inst_action,
                modified_problem,
                modified_grounded_actions_mapping,
                name_to_action,
                action_to_left_precondition_mapping,
                self.cost_mapping,
                modified_problem_cost_mapping,
                self.cost_cut_precondition,
                precon_to_changed_precon,
                negative_effect_mapping
            )
            modified_problem.add_actions(created_actions)
        
        modified_problem.add_quality_metric(MinimizeActionCosts(modified_problem_cost_mapping, default = 1))

        return ModifiedProblemInfo(
            modified_problem,
            modified_grounded_actions_mapping,
            action_to_left_precondition_mapping,
            name_to_action)


def create_resulting_actions(
        original_action: InstantaneousAction,
        modified_problem: Problem,
        modified_grounded_actions_mapping: dict[str, str],
        name_to_action: dict[str, InstantaneousAction],
        action_to_left_precondition_mapping: dict[str, tuple[InstantaneousAction, list[Fluent]]],
        cost_mapping_grounded: dict[str, int],
        modified_problem_cost_mapping: dict[Action, int],
        cost_cut_precondition: int,
        precon_to_changed_precon: dict[str, tuple[Fluent, list[Fluent]]],
        negative_effect_mapping: dict[str, tuple[Fluent, list[InstantaneousAction]]]
) -> list[InstantaneousAction]:
    """create actions for that """
    #list to return later
    action_list: list[InstantaneousAction] = []

    #uuid
    uuid_name_modifier = str(uuid4())

    #create unified action
    exit_action_name = "exit_" + original_action.name + "_" + uuid_name_modifier
    exit_action = original_action.clone()
    exit_action.name = exit_action_name
    exit_action.clear_preconditions()

    #mapping
    name_to_action[exit_action_name] = [exit_action]
    modified_grounded_actions_mapping[exit_action_name] = original_action.name

    #copy cost from original action
    modified_problem_cost_mapping[exit_action] = (cost_mapping_grounded[original_action.name]
        if cost_mapping_grounded[original_action.name] is not None else 0)

    #check if negative effects in action
    for effect in original_action.effects:
        if not effect.value:
            _ , list_of_negative_precondition_actions = negative_effect_mapping[str(effect.fluent)]
            list_of_negative_precondition_actions.append(exit_action)

    for current_precondition in original_action.preconditions:
        #create fluent
        precondition_fluent_name = (
            "precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        precondition_fluent = Fluent(precondition_fluent_name, BoolType())

        #make taking precondition Action
        take_precondition_action_name = (
            "take_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        take_precondition_action = InstantaneousAction(take_precondition_action_name)

        #create choose precondition
        choose_take_precondition_fluent_name = (
            "choose_take_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        choose_take_precondition_fluent = Fluent(choose_take_precondition_fluent_name, BoolType())

        #create one-time leave precondition action
        leave_one_time_precondition_action_name = (
            "leave_one_time_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        leave_one_time_precondition_action = InstantaneousAction(
            leave_one_time_precondition_action_name)
        #mapping to left precondition
        action_to_left_precondition_mapping[
            leave_one_time_precondition_action_name] = (original_action, [current_precondition])

        #create leave precondition action
        leave_precondition_action_name = (
            "leave_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        leave_precondition_action = InstantaneousAction(leave_precondition_action_name)

        #create one_time to often leave precondition fluent
        connect_leave_precondition_fluent_name = (
            "connect_leave_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        connect_leave_precondition_fluent = Fluent(
            connect_leave_precondition_fluent_name,
            BoolType())

        #create choosing to leave precondition fluent
        choose_leave_precondition_fluent_name = (
            "choose_leave_precon_" + str(current_precondition) 
            + "_" + original_action.name + "_" + uuid_name_modifier)
        choose_leave_precondition_fluent = Fluent(choose_leave_precondition_fluent_name, BoolType())

        #add fluents to actions
        exit_action.add_precondition(precondition_fluent)

        take_precondition_action.add_precondition(current_precondition)
        take_precondition_action.add_precondition(choose_take_precondition_fluent)
        take_precondition_action.add_effect(precondition_fluent, True)
        take_precondition_action.add_effect(choose_leave_precondition_fluent, False)

        leave_one_time_precondition_action.add_precondition(choose_leave_precondition_fluent)
        leave_one_time_precondition_action.add_effect(connect_leave_precondition_fluent, True)
        leave_one_time_precondition_action.add_effect(choose_take_precondition_fluent, False)

        leave_precondition_action.add_precondition(connect_leave_precondition_fluent)
        leave_precondition_action.add_effect(precondition_fluent, True)

        #set costs
        modified_problem_cost_mapping[take_precondition_action] = 0
        modified_problem_cost_mapping[leave_precondition_action] = 0
        modified_problem_cost_mapping[leave_one_time_precondition_action] = cost_cut_precondition

        #mapping of precondition
        _ , list_of_new_precons = precon_to_changed_precon[str(current_precondition)]
        list_of_new_precons.append(precondition_fluent)

        #add name action mapping
        name_to_action[take_precondition_action_name] = take_precondition_action
        name_to_action[leave_one_time_precondition_action_name] = leave_one_time_precondition_action
        name_to_action[leave_precondition_action_name] = leave_precondition_action

        #add to action list
        action_list.append(take_precondition_action)
        action_list.append(leave_one_time_precondition_action)
        action_list.append(leave_precondition_action)

        #add fluents to problem
        modified_problem.add_fluent(precondition_fluent, default_initial_value=False)
        modified_problem.add_fluent(choose_take_precondition_fluent, default_initial_value=True)
        modified_problem.add_fluent(choose_leave_precondition_fluent, default_initial_value=True)
        modified_problem.add_fluent(connect_leave_precondition_fluent, default_initial_value=False)

    #actions with negative effects need to delete the corresponding fluents
    for neg_precon, list_of_actions in negative_effect_mapping.values():
        for current_action in list_of_actions:
            for _ , list_of_to_set_fluents in precon_to_changed_precon[str(neg_precon)]:
                for to_set_fluent in list_of_to_set_fluents:
                    current_action.add_effect(to_set_fluent, False)

    #add actions
    action_list.append(exit_action)

    #return created actions
    return action_list
