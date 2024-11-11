"""import for unittest"""
from unified_planning.shortcuts import Problem
from source.model.plan_modifiers.modifier_util import read_problem_from_file, calculate_total_action_cost_metric, cost_leaving_precondition
from source.utility.problem_creator import ProblemCreator


class TestPlanUtils:
    """Test the modifier utility functions """
    def test_load_from_file(self):
        """test loading from file"""
        assert isinstance(read_problem_from_file(
            "./test/test_data/test_domain_working_A.pddl",
            "./test/test_data/test_problem_working_A.pddl"), Problem)


def test_calculate_total_action_cost_metric():
    "test calculate total action cost"
    problem = ProblemCreator.create_problem(
        [("x", True), ("y", True), ("z", False), ("p", False), ("q", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True)]),
            ("a2", ["z"], [("q", True)]),
            ("a3", ["z", "x"], [("q", True), ("y", False)])
        ],
        ["p", "q"],
        {
            "a1": 3,
            "a2": 2
        },
        0
    )
    total_action_cost, cost_mapping = calculate_total_action_cost_metric(problem)
    assert 5 == total_action_cost
    assert 3 == cost_mapping["a1"]
    assert 2 == cost_mapping["a2"]
    assert 0 == cost_mapping["a3"]

    #no predefined cost values
    problem2 = ProblemCreator.create_problem(
        [("x", True), ("y", True), ("z", False), ("p", False), ("q", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True)]),
            ("a2", ["z"], [("q", True)]),
            ("a3", ["z", "x"], [("q", True), ("y", False)])
        ],
        ["p", "q"]
    )
    total_action_cost2, cost_mapping2 = calculate_total_action_cost_metric(problem2)
    assert 3 == total_action_cost2
    assert 1 == cost_mapping2["a1"]
    assert 1 == cost_mapping2["a2"]
    assert 1 == cost_mapping2["a3"]

def test_cost_leaving_precondition():
    "test calc leaving precondition"
    problem = ProblemCreator.create_problem(
        [("x", True), ("y", True), ("z", False), ("p", False), ("q", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True)]),
            ("a2", ["z"], [("q", True)]),
            ("a3", ["z", "x"], [("q", True), ("y", False)])
        ],
        ["p", "q"],
        {
            "a1": 3,
            "a2": 2
        },
        0
    )
    leave_precon_cost = cost_leaving_precondition(problem)
    assert 5 * 3 == leave_precon_cost

    #no predefined cost values
    problem2 = ProblemCreator.create_problem(
        [("x", True), ("y", True), ("z", False), ("p", False), ("q", False)],
        [
            ("a1", ["x", "y"], [("z", True), ("p", True)]),
            ("a2", ["z"], [("q", True)]),
            ("a3", ["z", "x"], [("q", True), ("y", False)])
        ],
        ["p", "q"]
    )
    leave_precon_cost = cost_leaving_precondition(problem2)
    assert 3 * 3 == leave_precon_cost
