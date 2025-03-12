import traceback
from multiprocessing import Process, Manager, Queue
from source.utility.db_handler import DBHandler
from source.utility.multiprocess_tasks import modifier_solve_with_time
from source.model.plan_modifiers.problem_modifier import ProblemModifier
from source.model.plan_modifiers.exp_modifier import ExpModifier
from source.model.plan_modifiers.lin_modifier import LinModifier

def eval_all(db_file: str) -> None:
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
                eval_single(modifier, exp_modifier_id, destroyed_problem_id, db_handler)
            except Exception:
                error_text = traceback.format_exc()
                print(error_text)
                db_handler.insert_into_results(destroyed_problem_id, exp_modifier_id, None, error_text)
    
        #lin modifier
        if not db_handler.is_result_already_in_database(destroyed_problem_id, lin_modifier_id):
            try:
                modifier = LinModifier.from_text_eval(domain_content, problem_content)
                eval_single(modifier, lin_modifier_id, destroyed_problem_id, db_handler)
            except Exception:
                error_text = traceback.format_exc()
                print(error_text)
                db_handler.insert_into_results(destroyed_problem_id, lin_modifier_id, None, error_text)
    db_handler.close()


def eval_single(modifier:ProblemModifier, modifier_id: int, destroyed_problem_id: int, db_handler: DBHandler) -> None:
    """evaluate one single destroyed_problem for exponential problem modifier"""
    manager_time = Manager()
    manager_error = Manager()

    queue_modifier = Queue()
    queue_modifier.put(modifier)
    return_time_dict: dict[int, int] = manager_time.dict()
    return_error_dict: dict[int, str] = manager_error.dict()
    process = Process(target=modifier_solve_with_time, name="try_solving", args=(queue_modifier, return_time_dict, return_error_dict))
    process.start()
    print("starting trying to solve problem")
    time_to_wait_in_minutes = 60

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
    #print(modifier.modified_problem_info.action_to_left_precondition_mapping)
    #print(modifier.plan_info.backtracked_grounded_plan_result)
    print(modifier.plan_info.plan_results)

    db_handler.insert_into_results(destroyed_problem_id, modifier_id, time_in_milliseconds, None)
    result_id: int = db_handler.find_corresponding_result_id(destroyed_problem_id, modifier_id)
    #print(modifier.plan_info.left_preconditions)
    for action_name, precon_fnode_list  in modifier.plan_info.left_preconditions.items():
        for precon in precon_fnode_list:
            db_handler.insert_into_left_preconditions_results(result_id, action_name, str(precon))
