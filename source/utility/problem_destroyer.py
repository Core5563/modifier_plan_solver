"""Destroy Problems from ICP2014 to be unsolvable"""
from source.model.plan_modifiers.modifier_util import read_problem_from_file
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
        loaded_problem = read_problem_from_file(pre_path + current_problem.domain_dir, pre_path + current_problem.problem_dir)
        print(loaded_problem)
