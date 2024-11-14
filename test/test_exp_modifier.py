"""test exp_modifier component"""
from test.utility.assert_utility import exp_modifier_actions_correct
from source.model.plan_modifiers.exp_modifier import ExpModifier
from source.utility.problem_creator import ProblemCreator


def test_exp_modifier_actions() -> None:
    """check if actions are correct"""
    problem = ProblemCreator.create_problem(
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
    pm = ExpModifier(problem)
    assert exp_modifier_actions_correct(pm)
