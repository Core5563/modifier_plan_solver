"""unified planning imports"""
from unified_planning.shortcuts import InstantaneousAction #type:ignore

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
        if not ((actual_bool_value and expected_bool_value) or (not actual_bool_value and not expected_bool_value)):
            return False
    return True
