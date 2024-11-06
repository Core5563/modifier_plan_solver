"""import for unittest"""
import pytest
from unified_planning.shortcuts import Problem
from source.model.plan_modifiers.modifier_util import read_problem_from_file


class TestPlanUtils:
    """Test the modifier utility functions """
    def test_load_from_file(self):
        """test loading from file"""
        assert isinstance(read_problem_from_file(
            "./test/test_data/test_domain_working_A.pddl",
            "./test/test_data/test_problem_working_A.pddl"), Problem)
