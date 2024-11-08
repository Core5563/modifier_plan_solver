from unified_planning.shortcuts import InstantaneousAction, Fluent, BoolType
from test.utility.assert_utility import precondition_in_action, effect_in_action


def test_precondition_in_problem():
    """check if precondition in problem"""
    action = InstantaneousAction("action")
    precon1 = Fluent("fluent_1")
    precon2 = Fluent("fluent_2")
    action.add_precondition(precon1)
    action.add_precondition(precon2)
    assert precondition_in_action(["fluent_1", "fluent_2"], action)


def test_precondition_not_in_problem():
    """check if precondition not in problem"""
    action = InstantaneousAction("action")
    precon1 = Fluent("fluent_1", BoolType())
    precon2 = Fluent("fluent_2", BoolType())
    action.add_precondition(precon1)
    action.add_precondition(precon2)
    assert not precondition_in_action(["fluent_1", "fluent_2", "wrong_fluent"], action)


def test_effect_in_problem():
    action = InstantaneousAction("action")
    new_effect_1 = Fluent("e1", BoolType())
    new_effect_2 = Fluent("e2", BoolType())
    action.add_effect(new_effect_1, True)
    action.add_effect(new_effect_2, False)
    assert effect_in_action([("e1", True), ("e2", False)], action), "effects matching, should be correct"
    assert not effect_in_action([("e1", True), ("e2", True)], action), "e2 effect is not right"
    assert not effect_in_action([("e1", False), ("e2", False)], action), "e1 effect is not right"
    assert not effect_in_action([("e1", True)], action), "e2 missing"
    assert not effect_in_action([("e1", True), ("e2", False), ("wrong_effect", True)], action), "additional effect"
