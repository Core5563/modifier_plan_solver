"""Destroy Problems from ICP2014 to be unsolvable"""
import timeit, time
from unified_planning.shortcuts import OneshotPlanner, OptimalityGuarantee
from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem
from source.utility.directory_scanner import DirectoryScanner, ProblemDomainSet
from source.utility.db_handler import DBHandler
from source.utility.plan_analyser import PlanAnalyser

class ProblemDestroyer:
    """Destroy Problems"""

    def __init__(self):
        self.directory_scanner = DirectoryScanner()
        self.problem_list: list[ProblemDomainSet] = \
            self.directory_scanner.scan_benchmark("./evaluation/ipc2014_cleaned_benchmark")
        self.db_handler = DBHandler("evaluation/database/eval.db")
        self.plan_analyser = PlanAnalyser()

    def load_all_problems(self):
        """TODO: finish"""
        pre_path = "evaluation/ipc2014_cleaned_benchmark/"
        current_problem = self.problem_list[0]
        #for current_problem in self.problem_list:

            #load problem
        domain_path = pre_path + current_problem.domain_dir
        problem_path = pre_path + current_problem.problem_dir
        loaded_problem = read_problem_from_file(domain_path, problem_path)
            
            #ground problem
        print(loaded_problem)
        print("start grounding")
        grounded_information = ground_problem(loaded_problem)
        print("stop grounding")

            #solve problem
        planner = OneshotPlanner(name="Fast-Downward")
        start = timeit.default_timer()
        solution = planner.solve(grounded_information.problem, optimality_guarantee=OptimalityGuarantee.SATISFICING)
        end = timeit.default_timer()

        print(solution)
        print(end - start)