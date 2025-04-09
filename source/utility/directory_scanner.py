"""module for getting back files"""
import os
import re
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

    def scan_for_directory(self, dir_path: str):
        """scan specific directory"""
        for root, something , files in os.walk(dir_path):
            print(root)
            print(files)

    def scan_benchmark_IPC2016(self, dir_path: str) -> list[ProblemDomainSet]:
        """scan files for IPC2016"""
        content_list: list[ProblemDomainSet] = []
        for root, _ , files in os.walk(dir_path):
            domain_dir = ""
            problem_dir = ""
            is_content_directory: bool = (len(files) != 0)

            if not is_content_directory:
                continue

            #get domains
            domains: list[str] = []
            if "domain.pddl" in files:
                domains.append("domain.pddl")
            else:
                domains= [filename for filename in files if re.search("^dom[0-9]*.pddl$", filename) is not None]

            #get problems                
            if len(domains) == 0:
                continue

            problems: str = [filename for filename in files if re.search("^.*prob[0-9]*.pddl$", filename) is not None]

            if len(problems) == 0:
                continue

            #if only one domain file -> pack all problems to the single domain
            elif len(domains) == 1:
                for domain_file_name in domains:
                    for problem_file_name in problems:
                        domain_file_path = root.replace(dir_path, "", 1)
                        problem_file_path = root.replace(dir_path, "", 1)
                        domain_full_path = domain_file_path + os.sep + domain_file_name
                        problem_full_path = problem_file_path + os.sep + problem_file_name
                        content_list.append(ProblemDomainSet(domain_full_path, problem_full_path))
                continue
            
            #find corresponding domain files to problem files
            for problem_file_name in problems:
                dom_file = "dom" + (problem_file_name.replace("satprob", "")).replace("prob", "")
                if dom_file not in domains:
                    continue
                domain_file_path = root.replace(dir_path, "", 1)
                problem_file_path = root.replace(dir_path, "", 1)
                domain_full_path = domain_file_path + os.sep + dom_file
                problem_full_path = problem_file_path + os.sep + problem_file_name
                content_list.append(ProblemDomainSet(domain_full_path, problem_full_path))


                
        return content_list