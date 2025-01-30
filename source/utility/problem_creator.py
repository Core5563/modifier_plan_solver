"""imports from unified planning"""
from unified_planning.model import Problem, Fluent #type: ignore
from unified_planning.shortcuts import (#type: ignore
    BoolType, InstantaneousAction, MinimizeActionCosts)


class ProblemCreator:
    """ creates basic problems from string names"""

    # error messages
    VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE = "variable names must be unique."
    ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE = "actions names must be unique."
    PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE = (
        "unknown precondition. preconditions must be in variable list.")
    EFFECT_IS_UNKNOWN_ERROR_MESSAGE = "unknown effect. effect Variables must be in variable list."
    COST_UNKNOWN_ACTION_ERROR_MESSAGE = "cost for unknown action specified."
    GOAL_UNKNOWN_ERROR_MESSAGE = "unknown goal variable. goal variables must be in variable list."
    EMPTY_EFFECT_LIST_MESSAGE = "effect list should not be empty."

    def __init__(
            self,
            variables: list[tuple[str, bool]],
            actions: list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str]):
        self.problem: Problem = self.create_problem(variables, actions, goal)

    @staticmethod
    def create_problem(
            variables: list[tuple[str, bool]],
            actions: list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str],
            cost_dict: dict[str, int] | None = None,
            default_cost: int = 1) -> Problem:
        """
        create STRIPS Problems
        @variables list of variables with the initial boolean value (string_name, bool_init_value)
        @actions list of actions action = (string_name, list_precondition, list_of_effects)
        @goal list of goal vars
        """
        # check if no argument given
        if cost_dict is None:
            cost_dict = dict[str, int]()

        # create Problem to work with
        problem: Problem = Problem()

        # remember defined names
        name_to_fluent: dict[str, Fluent] = dict[str, Fluent]()

        # add variables to problem
        for var_name, initial_value in variables:
            # raise error on same variable Name
            if var_name in name_to_fluent:
                raise ValueError(ProblemCreator.VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE
                    + " name: " + var_name)
            new_fluent = Fluent(var_name, BoolType())
            name_to_fluent[var_name] = new_fluent
            problem.add_fluent(new_fluent, default_initial_value=initial_value)

        # remember defined actions
        name_to_action: dict[str, InstantaneousAction] = dict[str, InstantaneousAction]()

        # add actions
        cost_metric_dict = dict[InstantaneousAction, int]()
        for action_name, precondition_list, effect_list in actions:
            # raise error if name for action used more than one time
            if action_name in name_to_action:
                raise ValueError(ProblemCreator.ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE
                    + " name: " + action_name)
            new_action = InstantaneousAction(action_name)

            # add preconditions
            for precondition_name in precondition_list:
                if precondition_name not in name_to_fluent:
                    raise ValueError(
                        ProblemCreator.PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE
                            + " name: " + precondition_name)
                precondition_fluent = name_to_fluent[precondition_name]
                new_action.add_precondition(precondition_fluent)

            #at least one effect need to be specified
            if len(effect_list) == 0:
                raise ValueError(
                    ProblemCreator.EMPTY_EFFECT_LIST_MESSAGE + " action name: " + action_name)

            # add effects
            for effect_name, effect_result in effect_list:
                if effect_name not in name_to_fluent:
                    raise ValueError(ProblemCreator.EFFECT_IS_UNKNOWN_ERROR_MESSAGE
                        + " name: " + effect_name)
                effect_fluent = name_to_fluent[effect_name]
                new_action.add_effect(effect_fluent, effect_result)

            # add cost metric
            cost_metric_dict[new_action] = (
                cost_dict[action_name]
                if action_name in cost_dict
                else default_cost)

            # add to mapping
            name_to_action[action_name] = new_action

            # add action
            problem.add_action(new_action)

        # add cost metric
        for action_name, _ in cost_dict.items():
            if action_name not in name_to_action:
                raise ValueError(ProblemCreator.COST_UNKNOWN_ACTION_ERROR_MESSAGE
                    + " name: " + action_name)
        problem.add_quality_metric(MinimizeActionCosts(cost_metric_dict, default=default_cost))

        # add goal
        for goal_var_name in goal:
            if goal_var_name not in name_to_fluent:
                raise ValueError(ProblemCreator.GOAL_UNKNOWN_ERROR_MESSAGE
                    + " name: " + goal_var_name)
            goal_var = name_to_fluent[goal_var_name]
            problem.add_goal(goal_var)

        return problem
