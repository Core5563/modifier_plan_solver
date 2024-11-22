"""import for testing"""
from unified_planning.shortcuts import Problem #type: ignore
from source.utility.problem_creator import ProblemCreator
from source.model.plan_modifiers.lin_modifier import LinModifier
from test.utility.assert_utility import lin_actions_in_modifier_correct

def test_lin_modifier_actions() -> None:
    """check if actions are correct"""
    problem: Problem = ProblemCreator.create_problem(
        [
            ("x", True),
            ("y", True),
            ("z", True),
            ("u", False),
            ("v", False),
            ("w", False),
            ("q", False),
            ("p", False),
            ("d", False)
        ],
        [
            ("a1", ["x", "y"], [("z", True), ("q", True)]),
            ("a2", ["z"], [("u", True), ("p", True)]),
            ("a3", ["x", "y", "z", "u"], [("z", False), ("v", True), ("w", True)]),
            ("a4", [], [("z", True)]),
            ("a5", ["x", "y"], [("z", True)])

         ],
        ["p", "q", "v", "w"]
    )
    pm = LinModifier(problem)
    assert lin_actions_in_modifier_correct(pm)
