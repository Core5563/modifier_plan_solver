""" do eval for 2016 ipc"""
import traceback
from multiprocessing import Manager, Process
from unified_planning.engines.results import CompilerResult
from unified_planning.shortcuts import Problem
from unified_planning.io import PDDLWriter
from source.utility.multiprocess_tasks import ground_unsolvable_problem_multithread
from source.utility.directory_scanner import DirectoryScanner
from source.utility.db_handler import DBHandler
from source.model.plan_modifiers.modifier_util import read_problem_from_file
from source.utility.transform_grounded import transform_grounded_problem_to_standard

def load_ipc206_problems_into_database(db_file: str) -> None:
    """load all problems into db"""
    db_handler = DBHandler(db_file)
    scanner = DirectoryScanner()
    pre_path = "evaluation/ipc2016_benchmark"
    scanner_result = scanner.scan_benchmark_IPC2016(pre_path)
    for relative_domain_problem_path in scanner_result:
        problem_path = pre_path + relative_domain_problem_path.problem_dir
        domain_path = pre_path + relative_domain_problem_path.domain_dir
        print("d: " + domain_path + " p: " + problem_path)
        is_already_in_db: bool = db_handler.is_original_problem_in_database(problem_path, domain_path)
        if is_already_in_db:
            print("already in db")
            continue
        
        db_handler.insert_into_original_problems(
            problem_path,
            domain_path,
            0,
            0
        )
        problem_id = db_handler.find_corresponding_original_problem_id(problem_path, domain_path)
        try:
            load_and_ground_problem(problem_id, domain_path, problem_path, db_handler)
        except Exception:
            error_text = traceback.format_exc()
            print(error_text)
            db_handler.insert_into_original_problems(
                problem_path,
                domain_path,
                0,
                0,
                error_text
            )


def load_and_ground_problem(original_problem_id: int, domain_path: str, problem_path: str, db_handler: DBHandler) -> None:
    """load and ground the problem"""

    #load problem fro file
    loaded_problem = read_problem_from_file(domain_path, problem_path)
    
    #ground the problem
    manager_error = Manager()
    manager_result_ground = Manager()

    return_grounding_dict: dict[int, CompilerResult] = manager_result_ground.dict()
    return_error_dict: dict[int, str] = manager_error.dict()

    #ground problem
    time_to_wait_in_minutes_grounding = 30
    process_grounding = Process(target=ground_unsolvable_problem_multithread, name="grounding", args=(loaded_problem, return_grounding_dict, return_error_dict))
    print("start grounding problem")
    process_grounding.start()
    
    #disregard process if it takes longer than the original process
    process_grounding.join(time_to_wait_in_minutes_grounding * 60)
    if process_grounding.is_alive():
        process_grounding.terminate()
        process_grounding.join()
        print("grounding exceeded " + str(time_to_wait_in_minutes_grounding) + "minutes aborting.")
        db_handler.insert_destroy_problems(
            original_problem_id,
            "",
            "",
            "",
            "",
            "grounding exceeded " + str(time_to_wait_in_minutes_grounding) + "minutes aborting.")
        return
    
    #if error occurred handle it
    did_error_occuring_while_problem_grounding = 0 in return_error_dict
    if did_error_occuring_while_problem_grounding:
        print("error while grounding")
        error_text = return_error_dict[0]
        return_error_dict.pop(0)
        print(error_text)
        db_handler.insert_destroy_problems(
            original_problem_id,
            "",
            "",
            "",
            "",
            error_text
        )
        return

    print("grounding succeeded")
    grounded_information = return_grounding_dict[0]

    #initialize problem to destroy
    grounded_standardized_problem: Problem = transform_grounded_problem_to_standard(grounded_information.problem.clone())
    writer = PDDLWriter(grounded_standardized_problem)
    problem_content: str = writer.get_problem()
    domain_content: str = writer.get_domain()
    print("insert contents into db")
    db_handler.insert_destroy_problems(
        original_problem_id,
        "",
        "",
        problem_content,
        domain_content)
