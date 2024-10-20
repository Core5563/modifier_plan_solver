"""Import for abstract classes """
from abc import ABC, abstractmethod
from unified_planning.model import Problem
from unified_planning.engines.results import CompilerResult
from .modifier_util import read_problem_from_file, ground_problem, calculate_total_action_cost_metric
from .altered_plan import AlteredPlanInfo


class PlanModifier(ABC):
    """abstract base class for modification of a Problem"""
    def __init__(self, problem: Problem):
        #remember original problem
        self.original_problem: Problem = problem
        #ground the problem
        self.grounded_information: CompilerResult = ground_problem(problem)
        #calculate cost information
        total_cost, mapping = calculate_total_action_cost_metric(self.grounded_information.problem)
        #assign cost information
        self.total_action_cost: int = total_cost
        self.cost_mapping: dict[str, int] = mapping
        #create altered plan
        self.altered_plan = self._transform_grounded_plan()

    @classmethod
    def from_file(cls, domain_filepath: str, problem_filepath: str):
        """create object from domain and problem files"""
        problem = read_problem_from_file(domain_filepath, problem_filepath)
        return cls(problem)

    @abstractmethod
    def _transform_grounded_plan(self) -> AlteredPlanInfo:
        """create substitute plan from original plan """
