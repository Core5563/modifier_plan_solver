"""general imports"""
import itertools
from unified_planning.shortcuts import InstantaneousAction, Problem #type: ignore
from source.model.plan_modifiers.exp_modifier import ExpModifier
from source.model.plan_modifiers.lin_modifier import LinModifier

def precondition_in_action(precondition_names: list[str], action: InstantaneousAction) -> bool:
    """check if the name of a precondition is in a problem"""
    for precondition_name in precondition_names:
        # if not inside the precon list return false
        if precondition_name not in [precon.fluent().name for precon in action.preconditions]:
            return False

    for current_precon in action.preconditions:
        # if not inside the given name list
        if current_precon.fluent().name not in precondition_names:
            return False

    # if everything fine return true
    return True


def effect_in_action(effects: list[tuple[str, bool]], action: InstantaneousAction) -> bool:
    """return if the list of the effects are in the given action"""
    for effect_name, _ in effects:
        if effect_name not in [str(effect.fluent) for effect in action.effects]:
            return False

    for effect in action.effects:
        expected_bool_value: bool
        if str(effect.fluent) not in [effect_name for effect_name, _ in effects]:
            return False
        else:
            _, expected_bool_value = next(filter(lambda x: x[0] == str(effect.fluent), effects))

        # check if actual is expected
        actual_bool_value = effect.value.bool_constant_value()
        if not (
                (actual_bool_value and expected_bool_value)
                or (not actual_bool_value and not expected_bool_value)):
            return False
    return True


def exp_modifier_actions_correct(modifier: ExpModifier) -> bool:
    """check if all actions are created correctly"""
    grounded_problem: Problem = modifier.grounded_information.problem #type: ignore
    for original_action in grounded_problem.actions:
        #check if actions for the original actions
        assert exp_action_in_problem(modifier.modified_problem_info.problem, original_action), original_action.name + "not in problem"
    return True


def exp_action_in_problem(
        problem_to_asses: Problem,
        original_action: InstantaneousAction) -> bool:
    """returns True if all permutations to a given action exists and False otherwise"""
    #skip actions with no preconditions
    if len(original_action.preconditions) == 0:
        return True

    #create effect list
    effect_list: list[tuple[str, bool]] = [
        (str(effect.fluent), bool(effect.value.bool_constant_value()))
        for effect in original_action.effects]

    #create precondition list
    precon_list: list[str] = [precon.fluent().name for precon in original_action.preconditions]

    #go through all the permutations
    for index in range(len(original_action.preconditions) + 1):
        for permutation in itertools.combinations(precon_list, index):
            (found_exit_action, entry_exit_fluent_name) = (
                exp_exit_action_in_problem(
                    problem_to_asses,
                    original_action.name,
                    list(permutation),
                    effect_list))

            #every permutation needs to be covered
            assert found_exit_action, (
                "exit action was not found for: " + original_action.name
            )
            if not found_exit_action:
                return False

            #correct initial between entry and exit action
            assert not problem_to_asses.fluents_defaults[
                problem_to_asses.fluent(entry_exit_fluent_name)].bool_constant_value()

            #check if corresponding entry action with correct parameters exists
            found_entry_action, choose_fluent_name = exp_entry_action_in_problem(
                entry_exit_fluent_name,
                problem_to_asses,
                original_action.name)

            #entry action needs to exist
            assert found_entry_action, (
                "entry action wasn't found action name: " + original_action.name)
            if not found_entry_action:
                return False

            #choose fluent needs to be initialized with true
            assert problem_to_asses.fluents_defaults[problem_to_asses.fluent(choose_fluent_name)].bool_constant_value()

            return True
    return False


def exp_exit_action_in_problem(
        problem_to_asses: Problem,
        name_part: str,
        permutation: list[str],
        expected_effects: list[tuple[str, bool]]) -> tuple[bool, str]:
    """check if the exit action is contained in the problem"""
    entry_exit_fluent_name: str = ""

    for action in problem_to_asses.actions:
        if not name_part in action.name or not effect_in_action(expected_effects, action):
            continue

        found_action, entry_exit_fluent_name = exp_precondition_in_exit_action(permutation, action)

        if found_action:
            return (found_action, entry_exit_fluent_name)

    return (False, entry_exit_fluent_name)


def exp_precondition_in_exit_action(
        expected_preconditions: list[str],
        assessed_action: InstantaneousAction) -> tuple[bool, str]:
    """check if the name of a precondition is in a problem"""
    amount_of_unknown_preconditions: int = 0
    entry_exit_fluent: str = ""
    for precondition in assessed_action.preconditions:

        # if not inside the precon list return false
        if precondition.fluent().name not in expected_preconditions:

            #one unknown precondition is expected
            if amount_of_unknown_preconditions == 0:
                amount_of_unknown_preconditions += 1
                entry_exit_fluent = precondition.fluent().name
            else:
                return (False, entry_exit_fluent)

    for current_precon in expected_preconditions:
        # if not inside the given name list
        if (current_precon not in
                [precondition.fluent().name for precondition in assessed_action.preconditions]
                and current_precon != entry_exit_fluent):
            return (False, entry_exit_fluent)

    # if everything fine return true
    return (True, entry_exit_fluent)

def exp_entry_action_in_problem(
        entry_exit_fluent_name: str,
        problem_to_asses: Problem,
        name_part: str) -> tuple[bool, str]:
    """check if entry action is in problem"""
    choose_fluent_name: str = ""
    for action in problem_to_asses.actions:
        #name doesn't match move along
        if name_part not in action.name:
            continue

        #make sure action is of correct type
        if not isinstance(action, InstantaneousAction):
            raise ValueError
        current_action: InstantaneousAction = action

        #check if action by looking through the effects and checking if it is true
        found_action: bool = False
        for effect in current_action.effects:
            if str(effect.fluent) == entry_exit_fluent_name:
                found_action = True
                #check if it has correct effect value (needs to be true)
                if not effect.value.bool_constant_value():
                    return (False, choose_fluent_name)
                break

        #if the effect is not in this action keep searching
        if not found_action:
            continue

        #check if all other effects are set to correct value:
        for effect in current_action.effects:
            if str(effect.fluent) == entry_exit_fluent_name:
                continue
            #all other effects need to assign False Value
            if effect.value.bool_constant_value():
                return (False, choose_fluent_name)

        #check if only one precondition
        if len(current_action.preconditions) != 1:
            return (False, choose_fluent_name)

        choose_fluent_name = current_action.preconditions[0].fluent().name
        return (True, choose_fluent_name)
    return (False, choose_fluent_name)

def lin_action_in_problem(original_action: InstantaneousAction, problem_to_asses: Problem) -> bool:
    """check if action is correctly created"""

    #find exit action
    exit_action_found, exit_action = lin_exit_action_in_problem(
        original_action.name, problem_to_asses)

    assert exit_action_found

    current_exit_action: InstantaneousAction = exit_action

    #check if all actions that should be created are there
    for precondition in current_exit_action.preconditions:
        assert lin_take_precon_action(precondition.fluent().name, problem_to_asses)
        found_leave_precon, connection_precon_name = lin_leave_precon_action(
            precondition.fluent().name, problem_to_asses)
        assert found_leave_precon
        assert lin_one_time_leave_precon_action(connection_precon_name, problem_to_asses)
    return False


def lin_exit_action_in_problem(
        original_action_name:str,
        problem_to_asses: Problem) -> tuple[bool, InstantaneousAction]:
    """returns if exit action was found and the action if it was found"""
    for action in problem_to_asses.actions:
        if LinModifier.EXIT_ACTION_PREFIX + original_action_name in action.name:
            return (True, action)

    return (False, InstantaneousAction(""))


def lin_take_precon_action(precon_name: str, problem_to_asses: Problem) -> bool:
    """find the action to the precondition"""


    #find action
    for action in problem_to_asses.actions:
        if not isinstance(action, InstantaneousAction):
            raise ValueError("action is not of right type")

        #set correct type
        current_action: InstantaneousAction = action

        #see if action is correct
        if LinModifier.TAKE_PRECON_ACTION_PREFIX in action.name:
            for effect in current_action.effects:
                if effect.fluent == precon_name and effect.value.bool_constant_value():
                    return True

    return False

def lin_leave_precon_action(precon_name: str, problem_to_asses: Problem) -> tuple[bool, str]:
    """find the action to the precondition"""

    #find action
    for action in problem_to_asses.actions:
        if not isinstance(action, InstantaneousAction):
            raise ValueError("action is not of right type")

        #set correct type
        current_action: InstantaneousAction = action

        #see if action is correct
        if LinModifier.LEAVE_PRECON_ACTION_PREFIX in action.name:
            for effect in current_action.effects:
                if effect.fluent == precon_name and effect.value.bool_constant_value():
                    precon_name = current_action.preconditions[0].fluent().name
                    return (True, precon_name)

    return (False, "")

def lin_one_time_leave_precon_action(precon_name: str, problem_to_asses: Problem) -> bool:
    """find the action to the precondition"""


    #find action
    for action in problem_to_asses.actions:
        if not isinstance(action, InstantaneousAction):
            raise ValueError("action is not of right type")

        #set correct type
        current_action: InstantaneousAction = action

        #see if action is correct
        if LinModifier.LEAVE_ONE_TIME_PRECON_ACTION_PREFIX in action.name:
            for effect in current_action.effects:
                if effect.fluent == precon_name and effect.value.bool_constant_value():
                    return True

    return False

def lin_actions_in_modifier_correct(modifier: LinModifier) -> bool:
    """check modifier actions"""
    grounded_problem: Problem = modifier.grounded_information.problem

    for action in grounded_problem.actions:
        assert lin_action_in_problem(action, modifier.modified_problem_info.problem)
