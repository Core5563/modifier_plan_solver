import pytest
from operator import xor
from unified_planning.shortcuts import MinimizeActionCosts, InstantaneousAction
from source.utility.problem_creator import ProblemCreator
from test.utility.assert_utility import precondition_in_action, effect_in_action


def test_problem_creator_errors():
    # duplicate var name
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True), ("x", True)], [], [])
    assert (ProblemCreator.VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE + " name: x") in str(exception_info.value)

    # duplicate action name
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([], [("action1", [], []), ("action1", [], [])], [])
    assert (ProblemCreator.ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE + " name: action1") in str(exception_info.value)

    # unknown precondition
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", ["y"], [])], [])
    assert (ProblemCreator.PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE + " name: y") in str(exception_info.value)

    # unknown effect
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", [], [("y", True)])], [])
    assert (ProblemCreator.EFFECT_IS_UNKNOWN_ERROR_MESSAGE + " name: y") in str(exception_info.value)

    # unknown goal
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", ["x"], [("x", False)])], ["x", "y"])
    assert (ProblemCreator.GOAL_UNKNOWN_ERROR_MESSAGE + " name: y") in str(exception_info.value)

    # cost for undefined action
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem(
            [("x", True)],
            [("action1", ["x"], [("x", False)])],
            ["x"], {"action2": 4})
    assert (ProblemCreator.COST_UNKNOWN_ACTION_ERROR_MESSAGE + " name: action2") in str(exception_info.value)


def test_cost_parameters():
    # test cost specification
    problem = ProblemCreator.create_problem(
        [],
        [("a1", [], []), ("a2", [], [])],
        [],
        {"a1": 3}
    )
    assert problem.quality_metrics[0].is_minimize_action_costs()
    quality_metric: MinimizeActionCosts = problem.quality_metrics[0]
    a1_action = problem.action("a1")
    assert quality_metric.costs[a1_action].constant_value() == 3
    a2_action = problem.action("a2")
    assert quality_metric.costs[a2_action].constant_value() == 1
    second_problem = ProblemCreator.create_problem(
        [],
        [("a1", [], []), ("a2", [], [])],
        [],
        {"a1": 3}, default_cost=2
    )
    second_quality_metric: MinimizeActionCosts = second_problem.quality_metrics[0]
    a1_action = second_problem.action("a1")
    assert second_quality_metric.costs[a1_action].constant_value() == 3
    a2_action = second_problem.action("a2")
    assert second_quality_metric.costs[a2_action].constant_value() == 2


def test_variables_actions():
    problem = ProblemCreator.create_problem(
        [("x", True), ("y", True), ("z", True), ("u", False), ("v", False), ("w", False), ("q", False), ("p", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("q", True)]),
            ("a2", ["z"], [("u", True), ("p", True)]),
            ("a3", ["x", "y", "z", "u"], [("z", False), ("v", True), ("w", True)])

         ],
        ["p", "q", "v", "w"]
    )
    # has variables
    assert problem.has_fluent("x")
    assert problem.initial_value(problem.fluent("x")).bool_constant_value()
    assert problem.has_fluent("y")
    assert problem.initial_value(problem.fluent("y")).bool_constant_value()
    assert problem.has_fluent("z")
    assert problem.initial_value(problem.fluent("z")).bool_constant_value()
    assert problem.has_fluent("u")
    assert not problem.initial_value(problem.fluent("u")).bool_constant_value()
    assert problem.has_fluent("v")
    assert not problem.initial_value(problem.fluent("v")).bool_constant_value()
    assert problem.has_fluent("w")
    assert not  problem.initial_value(problem.fluent("w")).bool_constant_value()
    assert problem.has_fluent("p")
    assert not problem.initial_value(problem.fluent("p")).bool_constant_value()
    assert problem.has_fluent("q")
    assert not problem.initial_value(problem.fluent("q")).bool_constant_value()

    # has actions with correct preconditions and effects
    assert problem.has_action("a1")
    action_a1 = problem.action("a1")
    assert isinstance(action_a1, InstantaneousAction)
    action_a1: InstantaneousAction = problem.action("a1")
    assert precondition_in_action(["x", "y"], action_a1)
    assert effect_in_action([("z", True), ("q", True)], action_a1)

    assert problem.has_action("a2")
    action_a2 = problem.action("a2")
    assert isinstance(action_a2, InstantaneousAction)
    action_a2: InstantaneousAction = problem.action("a2")
    assert precondition_in_action(["z"], action_a2)
    assert effect_in_action([("u", True), ("p", True)], action_a2)

    assert problem.has_action("a3")
    action_a3 = problem.action("a3")
    assert isinstance(action_a3, InstantaneousAction)
    action_a3: InstantaneousAction = problem.action("a3")
    assert precondition_in_action(["x", "y", "z", "u"], action_a3)
    assert effect_in_action([("z", False), ("v", True), ("w", True)], action_a3)

