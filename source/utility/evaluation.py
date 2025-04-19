import traceback
from pathlib import Path
from multiprocessing import Process, Manager, Queue
from unified_planning.io import PDDLWriter, PDDLReader
from source.utility.db_handler import DBHandler
from source.utility.multiprocess_tasks import modifier_solve_with_time
from source.model.plan_modifiers.problem_modifier import ProblemModifier
from source.model.plan_modifiers.exp_modifier import ExpModifier
from source.model.plan_modifiers.lin_modifier import LinModifier

def write_out_problems(db_file: str, write_dir: str, remove_pre_path: str|None = None) -> None:
    """write out the problems"""
    db_handler: DBHandler = DBHandler(db_file)
    destroyed_problem_list: list[tuple[int, str, str]] = db_handler.get_working_destroyed_problems()
    for (destroyed_problem_id, domain_content, problem_content) in destroyed_problem_list:
        
        (_, path_domain, path_problem, content_domain, content_problem, error_text, grounded_problem_content, grounded_domain_content) = db_handler.get_destroyed_problem_by_id(destroyed_problem_id)
        added_path = path_domain.replace("/destroyed_domain.pddl", "")
        if remove_pre_path is not None:
            added_path = added_path.removeprefix(remove_pre_path)
        content_dir = write_dir + "/" + added_path
        #create unknown path
        Path(content_dir).mkdir(parents=True, exist_ok=True)

        reader = PDDLReader()
        #write grounded
        writer_grounded = PDDLWriter(reader.parse_problem_string(grounded_domain_content, grounded_problem_content))
        writer_grounded.write_domain(content_dir + "/grounded_domain.pddl")
        writer_grounded.write_problem(content_dir + "/grounded_problem.pddl")
        #write destroyed
        writer_destroyed = PDDLWriter(reader.parse_problem_string(content_domain, content_problem))
        writer_destroyed.write_domain(content_dir + "/destroyed_domain.pddl")
        writer_destroyed.write_problem(content_dir + "/destroyed_problem.pddl")
        #exp modifier
        try:
            dom_file = content_dir + "/" + "domainExp.pddl"
            prob_file = content_dir + "/" + "problemExp.pddl"
            modifier = ExpModifier.from_text_eval(domain_content, problem_content)
            writer = PDDLWriter(modifier.modified_problem_info.problem)
            writer.write_domain(dom_file)
            writer.write_problem(prob_file)
            #eval_single(modifier, exp_modifier_id, destroyed_problem_id, db_handler)
        except Exception:
            error_text = traceback.format_exc()
            print(error_text)
                #db_handler.insert_into_results(destroyed_problem_id, exp_modifier_id, None, error_text)
        #lin modifier
        
        try:
            dom_file = content_dir + "/" + "domainLin.pddl"
            prob_file = content_dir + "/" + "problemLin.pddl"
            modifier = LinModifier.from_text_eval(domain_content, problem_content)
            writer = PDDLWriter(modifier.modified_problem_info.problem)
            writer.write_domain(dom_file)
            writer.write_problem(prob_file)
            #eval_single(modifier, lin_modifier_id, destroyed_problem_id, db_handler)
        except Exception:
            error_text = traceback.format_exc()
            print(error_text)
            #db_handler.insert_into_results(destroyed_problem_id, lin_modifier_id, None, error_text)
    db_handler.close()


def eval_all(db_file: str, solve_optimally: bool = True) -> None:
    """evaluate all destroyed problems"""
    db_handler: DBHandler = DBHandler(db_file)
    exp_modifier_id = 1
    lin_modifier_id = 2
    destroyed_problem_list: list[tuple[int, str, str]] = db_handler.get_working_destroyed_problems()
    for (destroyed_problem_id, domain_content, problem_content) in destroyed_problem_list:
        #exp modifier
        if not db_handler.is_result_already_in_database(destroyed_problem_id, exp_modifier_id):
            try:
                modifier = ExpModifier.from_text_eval(domain_content, problem_content)
                eval_single(modifier, exp_modifier_id, destroyed_problem_id, db_handler, solve_optimally)
            except Exception:
                error_text = traceback.format_exc()
                print(error_text)
                db_handler.insert_into_results(destroyed_problem_id, exp_modifier_id, None, error_text)
    
        #lin modifier
        if not db_handler.is_result_already_in_database(destroyed_problem_id, lin_modifier_id):
            try:
                modifier = LinModifier.from_text_eval(domain_content, problem_content)
                eval_single(modifier, lin_modifier_id, destroyed_problem_id, db_handler, solve_optimally)
            except Exception:
                error_text = traceback.format_exc()
                print(error_text)
                db_handler.insert_into_results(destroyed_problem_id, lin_modifier_id, None, error_text)
    db_handler.close()


def eval_single(modifier:ProblemModifier, modifier_id: int, destroyed_problem_id: int, db_handler: DBHandler, solve_optimally: bool = True) -> None:
    """evaluate one single destroyed_problem for exponential problem modifier"""
    manager_time: Manager = Manager()
    manager_error: Manager = Manager()

    queue_modifier: Queue = Queue()
    queue_modifier.put(modifier)
    return_time_dict: dict[int, int] = manager_time.dict()
    return_error_dict: dict[int, str] = manager_error.dict()
    process = Process(target=modifier_solve_with_time, name="try_solving", args=(queue_modifier, return_time_dict, return_error_dict, solve_optimally))
    process.start()
    print("starting trying to solve problem")
    time_to_wait_in_minutes = 120

    process.join(time_to_wait_in_minutes * 60)
    
    #if still running break up
    if process.is_alive():
        process.terminate()
        process.join()
        print("solving exceeded " + str(time_to_wait_in_minutes) + "minutes: aborting.")
        db_handler.insert_into_results(destroyed_problem_id,modifier_id, None, error_text=("Solving exceeded " + str(time_to_wait_in_minutes) + " minutes"))
        return
    
    #if error occurred handle it
    did_error_occur_while_problem_solving = 0 in return_error_dict
    if did_error_occur_while_problem_solving:
        error_text = return_error_dict[0]
        print("found error while solving")
        print(error_text)
        db_handler.insert_into_results(destroyed_problem_id, modifier_id, None, error_text)
        return

    start = return_time_dict[0]
    end = return_time_dict[1]
    time_in_milliseconds: int = int((end  - start) // 10 ** 6)
    
    modifier: ProblemModifier = queue_modifier.get()

    db_handler.insert_into_results(destroyed_problem_id, modifier_id, time_in_milliseconds, None)
    result_id: int = db_handler.find_corresponding_result_id(destroyed_problem_id, modifier_id)

    for action_name, precon_fnode_list  in modifier.plan_info.left_preconditions.items():
        for precon in precon_fnode_list:
            db_handler.insert_into_left_preconditions_results(result_id, action_name, str(precon))
