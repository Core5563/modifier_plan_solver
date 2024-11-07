import pytest
from unified_planning.shortcuts import MinimizeActionCosts
from source.utility.problem_creator import ProblemCreator


def test_problem_creator_errors():
    # duplicate var name
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True), ("x", True)], [], [])
    assert ProblemCreator.VARIABLE_NAME_NOT_UNIQUE_ERROR_MESSAGE in str(exception_info.value)

    # duplicate action name
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([], [("action1", [], []), ("action1", [], [])], [])
    assert ProblemCreator.ACTION_NAME_NOT_UNIQUE_ERROR_MESSAGE in str(exception_info.value)

    # unknown precondition
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", ["y"], [])], [])
    assert ProblemCreator.PRECONDITION_IS_UNKNOWN_ERROR_MESSAGE in str(exception_info.value)

    # unknown effect
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", [], [("y", True)])], [])
    assert ProblemCreator.EFFECT_IS_UNKNOWN_ERROR_MESSAGE in str(exception_info.value)

    # unknown goal
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem([("x", True)], [("action1", ["x"], [("x", False)])], ["x", "y"])
    assert ProblemCreator.GOAL_UNKNOWN_ERROR_MESSAGE in str(exception_info.value)

    # cost for undefined action
    with pytest.raises(ValueError) as exception_info:
        ProblemCreator.create_problem(
            [("x", True)],
            [("action1", ["x"], [("x", False)])],
            ["x"], {"action2": 4})
    assert ProblemCreator.COST_UNKNOWN_ACTION_ERROR_MESSAGE in str(exception_info.value)


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
    #todo finish
