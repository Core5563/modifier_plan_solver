"""module for getting back files"""
import os

class ProblemDomainSet:
    """set for problem and directory"""
    def __init__(self, domain_dir: str, problem_dir: str):
        self.domain_dir = domain_dir
        self.problem_dir = problem_dir

class DirectoryScanner:
    """scan files in directory and subdirectories"""
    def __init__(self):
        pass

    def scan_benchmark(self, dir_path: str) -> list[ProblemDomainSet]:
        """scan files"""
        content_list: list[ProblemDomainSet] = []
        for root, _ , files in os.walk(dir_path):
            domain_dir = ""
            problem_dir = ""
            is_content_directory: bool = (len(files) != 0)
            for f in files:
                if is_content_directory and f == "domain.pddl":
                    domain_dir = root.replace(dir_path, "", 1)
                if is_content_directory and f == "problem.pddl":
                    problem_dir = root.replace(dir_path, "", 1)
            if is_content_directory:
                content_list.append(ProblemDomainSet(
                    domain_dir + os.sep + "domain.pddl",
                    problem_dir + os.sep + "problem.pddl"))
        return content_list
