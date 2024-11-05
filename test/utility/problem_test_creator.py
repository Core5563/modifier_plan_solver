from source.utility.problem_creator import ProblemCreator
from unified_planning.shortcuts import Problem


class TestProblemCreator:
    """ create Test Problems quickly"""

    def __init__(self):
        pass

    @staticmethod
    def solvable_basic() -> Problem:
        return ProblemCreator.create_problem(
            [("x", True), ("y", True), ("z", True), ("p", False), ("q", False)],
            [("action1", ["x", "y"], [("z", True)])],
            ["p", "q"]
        )

    @staticmethod
    def unsolvable_basic() -> Problem:
        return ProblemCreator.create_problem(
            [("x", True), ("y", False), ("z", True), ("p", False), ("q", False)],
            [("action1", ["x", "y"], [("z", True)])],
            ["p", "q"]
        )