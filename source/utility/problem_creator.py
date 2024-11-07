from unified_planning.model import Problem, Fluent
from unified_planning.shortcuts import BoolType, InstantaneousAction, MinimizeActionCosts


class ProblemCreator:
    """ creates basic problems from string names"""

    # error messages
    VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE = "Variable Names must be unique"
    ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE = "Actions names must be unique"
    PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE = "unknown Precondition. Preconditions must be in variable list"
    EFFECT_IS_UNKNOWN_ERROR_MESSAGE = "unknown Effect. Effect Variables must be in variable list"
    COST_UNKNOWN_ACTION_ERROR_MESSAGE = "cost for unknown action specified"
    GOAL_UNKNOWN_ERROR_MESSAGE = "unknown Goal Variable. Goal Variables must be in Variable list"

    def __init__(
            self,
            variables: list[tuple[str, bool]],
            actions: list[tuple[str, list[str],list[tuple[str, bool]]]],
            goal: list[str]):
        self.problem: Problem = self.create_problem(variables, actions, goal)

    @staticmethod
    def create_problem(
            variables:list[tuple[str, bool]],
            actions:list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str],
            cost_dict: dict[str, int] | None = None,
            default_cost: int = 1) -> Problem:
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
                raise ValueError(ProblemCreator.VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE)
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
                raise ValueError(ProblemCreator.ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE)
            new_action = InstantaneousAction(action_name)

            # add preconditions
            for precondition_name in precondition_list:
                if precondition_name not in name_to_fluent:
                    raise ValueError(ProblemCreator.PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE)
                precondition_fluent = name_to_fluent[precondition_name]
                new_action.add_precondition(precondition_fluent)

            # add effects
            for effect_name, effect_result in effect_list:
                if effect_name not in name_to_fluent:
                    raise ValueError(ProblemCreator.EFFECT_IS_UNKNOWN_ERROR_MESSAGE)
                effect_fluent = name_to_fluent[effect_name]
                new_action.add_effect(effect_fluent, effect_result)

            # add cost metric
            cost_metric_dict[new_action] = cost_dict[action_name] if action_name in cost_dict else default_cost

            # add to mapping
            name_to_action[action_name] = new_action

            # add action
            problem.add_action(new_action)

        # add cost metric
        for action_name, action_cost in cost_dict.items():
            if action_name not in name_to_action:
                raise ValueError(ProblemCreator.COST_UNKNOWN_ACTION_ERROR_MESSAGE)
        problem.add_quality_metric(MinimizeActionCosts(cost_metric_dict, default=default_cost))

        # add goal
        for goal_var_name in goal:
            if goal_var_name not in name_to_fluent:
                raise ValueError(ProblemCreator.GOAL_UNKNOWN_ERROR_MESSAGE)
            goal_var = name_to_fluent[goal_var_name]
            problem.add_goal(goal_var)

        return problem
