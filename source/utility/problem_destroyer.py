"""Destroy Problems from ICP2014 to be unsolvable"""
import time
import traceback
import random
from multiprocessing import Process, Manager
from unified_planning.io import PDDLWriter
from unified_planning.engines.results import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner, Problem, InstantaneousAction
from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_solvable_problem
from source.utility.directory_scanner import DirectoryScanner, ProblemDomainSet
from source.utility.db_handler import DBHandler
from source.utility.plan_analyser import PlanAnalyser

class ProblemDestroyer:
    """Destroy Problems"""

    def __init__(self, database_file_name: str):
        #evaluation/easy_benchmark/subfolder1/subfolder2
        self.directory_scanner = DirectoryScanner()
        self.problem_list: list[ProblemDomainSet] = self.directory_scanner.scan_benchmark("./evaluation/easy_benchmark")
        #self.directory_scanner.scan_benchmark("./evaluation/ipc2014_cleaned_benchmark")
        self.db_handler = DBHandler(database_file_name)
        self.plan_analyser = PlanAnalyser()

    def load_all_problems(self):
        """load all original problems into the database with time to solve and solution length"""
        pre_path = "evaluation/ipc2014_cleaned_benchmark/"
        #pre_path = "evaluation/easy_benchmark/"
        #current_problem = self.problem_list[0]
        for current_problem in self.problem_list:
            #load problem
            domain_path: str = pre_path + current_problem.domain_dir
            problem_path: str = pre_path + current_problem.problem_dir
            try:
                loaded_problem = read_problem_from_file(domain_path, problem_path)
                
                #ground problem
                #grounded_information = ground_solvable_problem(loaded_problem)
                grounded_information = ground_solvable_problem(loaded_problem)
                #solve problem
                #planner = OneshotPlanner(name="fast-downward")
                planner = OneshotPlanner(name="fast-downward")
                
                #measure the time it takes to solve the problem
                start = time.perf_counter_ns()
                solution = planner.solve(grounded_information.problem)
                end = time.perf_counter_ns()

                analyzer = PlanAnalyser()
                
                plan_cost: int = analyzer.calculate_plan_cost(grounded_information.problem, solution.plan)
                time_in_milliseconds: int = int((end  - start) // 10 ** 6)
                self.db_handler.insert_into_original_problems(
                    problem_path,
                    domain_path,
                    plan_cost,
                    time_in_milliseconds
                )
            except Exception:
                error_text = traceback.format_exc()
                print(problem_path + "\n" + error_text)
                self.db_handler.insert_into_original_problems(
                    problem_path,
                    domain_path,
                    0,
                    0,
                    error_text
                )
    def destroy_problems(self):
        list_of_unused_problems = self.db_handler.get_not_used_original_problem_ids()
        for problem_tuple in list_of_unused_problems:
            original_problem_id = problem_tuple[0]
            try:
                self.destroy_problem(original_problem_id)
            except Exception:
                error_text = traceback.format_exc()
                print(error_text)
                self.db_handler.insert_destroy_problems(
                    original_problem_id,
                    "",
                    "",
                    "",
                    "",
                    error_text
                    )
    
    def destroy_problem(self, original_problem_id):
        #load problem
        domain_path, problem_path, cost, time_in_milliseconds = self.db_handler.get_original_problem_from_id(original_problem_id)
            
        #if it took longer than 30 seconds to solve the problem then skip
        if time_in_milliseconds / 10**3 > 30:
            return
        
        #load problem fro file
        loaded_problem = read_problem_from_file(domain_path, problem_path)
        
        #ground the problem
        grounded_information = ground_solvable_problem(loaded_problem)

        #initalize problem to destroy
        problem_to_destroy: Problem = grounded_information.problem.clone()

        is_problem_solvable: bool = True

        #remember which preconditions where introduced to which actions
        added_precon_dict: dict[str, list[str]] = {}

        while is_problem_solvable:
            #for random initialization
            fluent_weights: dict[str, int]= {}

            #choose fluents according to probability
            for current_fluent in problem_to_destroy.fluents:
                fluent_weights[current_fluent.name] = 1
            
            total_actions_count = len(problem_to_destroy.actions)

            #if fluent not in initial set then increase probability
            for initial_value_key, value in problem_to_destroy.initial_values.items():
                if value.is_false():
                    fluent_weights[initial_value_key.fluent().name] += total_actions_count
            #if fluent not in precondition and not in positive effects
            #increase probability
            action_weights: dict[str, int] = {}
            for action in problem_to_destroy.actions:
                current_action: InstantaneousAction = action
                precon_names: list[str] = [precon.fluent().name for precon in current_action.preconditions]
                negative_effects: list[str] = [effect.fluent.fluent().name for effect in current_action.effects if not effect.value]
                positive_effects: list[str] = [effect.fluent.fluent().name for effect in current_action.effects if effect.value]
                
                #remember weights
                action_weights[current_action.name] = len(precon_names)
                for fluent_name in fluent_weights:
                    #if not precondition increase probability
                    if fluent_name not in precon_names:
                        fluent_weights[fluent_name] += 1
                    #if a negative effect increase probability
                    if fluent_name in negative_effects:
                        fluent_weights[fluent_name] += 2
                    #if not a positive effect increase probability
                    elif fluent_name not in positive_effects:
                        fluent_weights[fluent_name] += 1
            #if in goal state increase value
            for goal in problem_to_destroy.goals:
                fluent_weights[goal.fluent().name] += total_actions_count
            #prepare choosing value randomly
            fluent_name_list = list(fluent_weights.keys())
            fluent_weight_list = list(fluent_weights.values())
            action_name_list = list(action_weights.keys())
            action_weight_list = list(action_weights.values())
            is_new_precon_added = False
            while not is_new_precon_added:
                #choose action and fluent randomly
                [random_chosen_fluent_name] = random.choices(fluent_name_list, weights=fluent_weight_list, k=1)
                [random_chosen_action_name] = random.choices(action_name_list, weights=action_weight_list, k=1)
                current_action: InstantaneousAction = problem_to_destroy.action(random_chosen_action_name)
                #check if precondition already exists
                if random_chosen_fluent_name in [precon.fluent().name for precon in current_action.preconditions]:
                    continue

                current_action.add_precondition(problem_to_destroy.fluent(random_chosen_fluent_name))
                if random_chosen_action_name not in added_precon_dict:
                    added_precon_dict[random_chosen_action_name] = []
                added_precon_dict[random_chosen_action_name].append(random_chosen_fluent_name)
                is_new_precon_added = True

            #check if problem is solvable
            manager = Manager()
            return_dict = manager.dict()
            process = Process(target=solve_problem_with_multithreading, name="", args=(problem_to_destroy, return_dict))
           
            time_to_wait_in_minutes = 1
            process.start()
            process.join(time_to_wait_in_minutes * 60)
            
            is_completed = True
            if process.is_alive():
                process.terminate()
                process.join()
                is_completed = False
            
            if is_completed:
                solution: PlanGenerationResult = return_dict[0]
                print(solution.status)
                if solution.status in [PlanGenerationResultStatus.UNSOLVABLE_PROVEN, PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY]:
                    is_problem_solvable = False
            else:
                is_problem_solvable = False

        #save results
        destroyed_domain_path = domain_path.replace("domain.pddl", "destroyed_domain.pddl")
        destroyed_problem_path = problem_path.replace("problem.pddl", "problem_domain.pddl")
        writer = PDDLWriter(problem_to_destroy)
        writer.write_domain(destroyed_domain_path)
        writer.write_problem(destroyed_problem_path)
        file = open(destroyed_domain_path, mode="r", encoding="utf-8")
        domain_content = file.read().rstrip()
        try:
            file.close()
        except Exception:
            pass
        file = open(destroyed_problem_path, mode="r", encoding="utf-8")
        problem_content = file.read().rstrip()
        try:
            file.close()
        except Exception:
            pass
        self.db_handler.insert_destroy_problems(
            original_problem_id,
            destroyed_problem_path,
            destroyed_domain_path,
            problem_content,
            domain_content)
        for action_name, list_fluent_names in added_precon_dict.items():
            for fluent_name in list_fluent_names:
                self.db_handler.insert_into_added_preconditions(original_problem_id, action_name, fluent_name)
        print(problem_to_destroy)
        print(added_precon_dict)
        print(self.db_handler.get_all_destroyed_problems())
        print(self.db_handler.get_all_add_preconditions())
    
    def close(self):
        """close the problem destroyer"""
        self.db_handler.close()


def solve_problem_with_multithreading(problem: Problem, return_dict: dict[int, PlanGenerationResult]) -> None:
    """solve with fast-downward planner"""
    planner = OneshotPlanner(name="fast-downward")
    solution = planner.solve(problem)
    return_dict[0] = solution
