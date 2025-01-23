"""Destroy Problems from ICP2014 to be unsolvable"""
import timeit, time, traceback, random
from unified_planning.shortcuts import OneshotPlanner, OptimalityGuarantee, Problem, Fluent, InstantaneousAction
from source.model.plan_modifiers.modifier_util import read_problem_from_file, ground_problem, ground_solvable_problem
from source.utility.directory_scanner import DirectoryScanner, ProblemDomainSet
from source.utility.db_handler import DBHandler
from source.utility.plan_analyser import PlanAnalyser

class ProblemDestroyer:
    """Destroy Problems"""

    def __init__(self):
        #evaluation/easy_benchmark/subfolder1/subfolder2
        self.directory_scanner = DirectoryScanner()
        self.problem_list: list[ProblemDomainSet] = self.directory_scanner.scan_benchmark("./evaluation/easy_benchmark")
        #self.directory_scanner.scan_benchmark("./evaluation/ipc2014_cleaned_benchmark")
        self.db_handler = DBHandler("evaluation/database/eval.db")
        self.plan_analyser = PlanAnalyser()

    def load_all_problems(self):
        """load all original problems into the database with time to solve and solution length"""
        #pre_path = "evaluation/ipc2014_cleaned_benchmark/"
        pre_path = "evaluation/easy_benchmark/"
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
                planner = OneshotPlanner(problem_kind=grounded_information.problem.kind, optimality_guarantee=OptimalityGuarantee.SATISFICING)
                
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
            self.destroy_problem(original_problem_id)
    
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

        print(grounded_information.problem)

        #initalize problem to destroy
        problem_to_destroy: Problem = grounded_information.problem.clone()

        is_problem_solvable: bool = True

        while is_problem_solvable:
            #for random initialization
            weight_dict: dict[str, int]= {}
            name_to_fluent: dict[str, Fluent] = {}
            for current_fluent in problem_to_destroy.fluents:
                weight_dict[current_fluent.name] = 1
                name_to_fluent[current_fluent.name] = current_fluent
            
            total_actions_count = len(problem_to_destroy.actions)

            #if fluent not in initial set then increase probability
            for initial_value_key, value in problem_to_destroy.initial_values.items():
                if not value:
                    weight_dict[initial_value_key.fluent().name] += total_actions_count

            
            #if fluent not in precondition and not in positive effects
            #increase probability
            for action in problem_to_destroy.actions:
                current_action: InstantaneousAction = action
                precon_names: list[str] = [precon.fluent().name for precon in current_action.preconditions]
                negative_effects: list[str] = [effect.fluent.fluent().name for effect in current_action.effects if not effect.value]
                positive_effects: list[str] = [effect.fluent.fluent().name for effect in current_action.effects if effect.value]
                for fluent_name in weight_dict:
                    #if not precondition increase probability
                    if fluent_name not in precon_names:
                        weight_dict[fluent_name] += 1
                    #if a negative effect increase probability
                    if fluent_name in negative_effects:
                        weight_dict[fluent_name] += 2
                    #if not a positive effect increase probability
                    elif fluent_name not in positive_effects:
                        weight_dict[fluent_name] += 1
            
            for goal in problem_to_destroy.goals:
                weight_dict[goal.fluent().name] = total_actions_count
        
            fluent_name_list = list(weight_dict.keys())
            fluent_weights = list(weight_dict.values())
            print(fluent_name_list)
            print(fluent_weights)

            [random_chosen_name] = random.choices(fluent_name_list, weights=fluent_weights, k=1)
            print(random_chosen_name)
            is_problem_solvable = False
