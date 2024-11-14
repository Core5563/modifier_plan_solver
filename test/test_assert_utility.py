"""test the assertion utility"""
import pytest
from unified_planning.shortcuts import InstantaneousAction, Fluent, BoolType, Problem #type: ignore
from test.utility.assert_utility import precondition_in_action, effect_in_action, exp_precondition_in_exit_action


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
    """test if effects are in the problem"""
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

def test_exp_precondition_in_exit_action():
    """test precondition finding"""
    action = InstantaneousAction("exit_action_a1")
    f1 = Fluent("x1", BoolType())
    f2 = Fluent("x2", BoolType())
    f3 = Fluent("x3", BoolType())
    action.add_effect(f1, True)
    action.add_precondition(f1)
    action.add_precondition(f2)
    action.add_precondition(f3)
    f_list = [f1.name, f2.name]
    
    precondition_in_action, expected_fluent = exp_precondition_in_exit_action(f_list, action)

    assert precondition_in_action
    assert f3.name == expected_fluent

    action2 = InstantaneousAction("exit_action_a2")
    action2.add_effect(f1, True)
    action2.add_precondition(f1)
    action2.add_precondition(f2)
    action2.add_precondition(f3)
    f4 = Fluent("x4", BoolType())
    action2.add_precondition(f4)
    f_list2 = [f1.name, f2.name]
    precondition_in_action, expected_fluent = exp_precondition_in_exit_action(f_list2, action2)

    assert not precondition_in_action


@pytest.mark.skip(reason="not necessary?")
def test_exp_exit_action_in_problem():
    """test if correctly working"""

    problem = Problem()
    f1 = Fluent("x1")
    f2 = Fluent("x2")
    f3 = Fluent("x3")
    entry_exit_fluent = Fluent("entry_exit")

    action = InstantaneousAction("action1")

def test_exp_entry_action_in_problem():
    pass