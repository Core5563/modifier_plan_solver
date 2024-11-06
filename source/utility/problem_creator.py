from unified_planning.model import Problem, Fluent
from unified_planning.shortcuts import BoolType, InstantaneousAction


class ProblemCreator:
    """ creates basic problems from string names"""
    def __init__(self, variables:list[tuple[str, bool]], actions:list[tuple[str, list[str], list[tuple[str, bool]]]], goal: list[str]):
        self.problem: Problem = self.create_problem(variables, actions, goal)

    @staticmethod
    def create_problem(
            variables:list[tuple[str, bool]],
            actions:list[tuple[str, list[str], list[tuple[str, bool]]]],
            goal: list[str]) -> Problem:
        # create Problem to work with
        problem: Problem = Problem()

        # remember defined names
        name_to_fluent: dict[str, Fluent] = dict[str, Fluent]()

        # add variables to problem
        for var_name, initial_value in variables:
            # raise error on same variable Name
            if var_name in name_to_fluent:
                raise ValueError("Variable Names must be unique")
            new_fluent = Fluent(var_name, BoolType())
            name_to_fluent[var_name] = new_fluent
            problem.add_fluent(new_fluent, default_initial_value=initial_value)

        # remember defined actions
        name_to_action: dict[str, InstantaneousAction] = dict[str, InstantaneousAction]()

        for action_name, precondition_list, effect_list in actions:
            # raise error if name for action used more than one time
            if action_name in name_to_action:
                raise ValueError("Actions names must be unique")
            new_action = InstantaneousAction(action_name)

            # add preconditions
            for precondition_name in precondition_list:
                if precondition_name not in name_to_fluent:
                    raise ValueError("unknown Precondition. Preconditions must be in variable list")
                precondition_fluent = name_to_fluent[precondition_name]
                new_action.add_precondition(precondition_fluent)

            # add effects
            for effect_name, effect_result in effect_list:
                if effect_name not in name_to_fluent:
                    raise ValueError("unknown Effect. Effect Variables must be in variable list")
                effect_fluent = name_to_fluent[effect_name]
                new_action.add_effect(effect_fluent, effect_result)

        # add goal
        for goal_var_name in goal:
            if goal_var_name not in name_to_fluent:
                raise ValueError("unknown Goal Variable. Goal Variables must be in Variable list")
            goal_var = name_to_fluent[goal_var_name]
            problem.add_goal(goal_var)

        return problem
