from source.utility.problem_creator import ProblemCreator
from unified_planning.shortcuts import Problem #type:ignore


class TestProblemCreator:
    """ create Test Problems quickly"""

    def __init__(self):
        pass

    @staticmethod
    def solvable_basic() -> Problem:
        return ProblemCreator.create_problem(
            [("x", True), ("y", True), ("z", False), ("p", False), ("q", False)],
            [
                ("action1", ["x", "y"], [("z", True), ("p", True)]),
                ("action2", ["z"], [("q", True)])
            ],
            ["p", "q"]
        )

    @staticmethod
    def unsolvable_basic() -> Problem:
        return ProblemCreator.create_problem(
            [("x", True), ("y", False), ("z", False), ("p", False), ("q", False)],
            [
                ("action1", ["x", "y"], [("z", True), ("p", True)]),
                ("action2", ["z"], [("q", True)])
             ],
            ["p", "q"]
        )

    @staticmethod
    def unsolvable_absolute() -> Problem:
        return ProblemCreator.create_problem(
            [("x", True), ("y", False), ("z", False), ("p", False), ("q", False)],
            [
                ("action1", ["x", "y"], [("z", True), ("p", True), ("q", False)]),
                ("action2", ["z"], [("q", True), ("p", False)])
            ],
            ["p", "q"]
        )