"""imports for tests"""
import pytest
from unified_planning.shortcuts import Problem
from source.model.plan_modifiers.problem_modifier import ProblemModifier


def test_problem_modifier():
    """test the Problem Modifier cannot be instantiated"""
    problem = Problem()
    with pytest.raises(TypeError):
        x = ProblemModifier(problem)