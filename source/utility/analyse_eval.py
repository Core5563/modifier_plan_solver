"""module to analyze results"""
from unified_planning.shortcuts import Problem, InstantaneousAction
from unified_planning.io import PDDLReader, PDDLWriter
from source.utility.db_handler import DBHandler
from source.utility.transform_grounded import transform_grounded_problem_to_standard
from source.model.plan_modifiers.modifier_util import  cost_leaving_precondition

def analyse_all(csv_file_path: str, db_file_path: str) -> None:
    """analyse problems and write to a csv file"""
    db_handler = DBHandler(db_file_path)
    list_of_original_problems = db_handler.get_all_original_problems()
    db_handler.look_into()
    for (original_problem_id, domain_file_path, problem_file_path, plan_solvable_cost,solve_time_milliseconds, error_text, is_longer_30_min) in list_of_original_problems:
        if error_text is None or is_longer_30_min == 1:
            print("Error or longer to solve than 30 min. Aborting")
            continue
        destroyed_problem_tuple = db_handler.get_destroyed_problem_by_id(original_problem_id)
        if destroyed_problem_tuple is None:
            print("could not find original problem with id=" + str(original_problem_id) + ". Aborting")
            continue
        (_, path_domain, path_problem, content_domain, content_problem, error_text, grounded_problem_content, grounded_domain_content) = destroyed_problem_tuple
        if error_text is None:
            print("destroying the problem failed because of an error. Aborting")
            continue
        reader = PDDLReader()
        grounded_problem: Problem = transform_grounded_problem_to_standard(reader.parse_problem_string(grounded_domain_content, grounded_problem_content))
        destroyed_problem: Problem = transform_grounded_problem_to_standard(reader.parse_problem_string(content_domain, content_problem))
        
        amount_actions_grounded, amount_variables_grounded = count_action_and_variables(grounded_problem)
        amount_actions_destroyed, amount_variables_destroyed = count_action_and_variables(destroyed_problem)
        if  amount_actions_destroyed != amount_actions_grounded:
            print("amount of actions does not match grounded:"+ str(amount_actions_grounded)+ " and destroyed:" + str(amount_actions_destroyed))
        if  amount_variables_destroyed != amount_variables_grounded:
            print("amount of variables does not match grounded:" + str(amount_variables_grounded)+ " and destroyed:" + str(amount_variables_destroyed))
        
        used_cost_penalty = cost_leaving_precondition(destroyed_problem)
        
        

        
        






def count_action_and_variables(problem: Problem) -> tuple[int, int]:
    """returns (amount_of_actions, amount_of_variables)"""
    return (len(problem.actions), count_grounded_variables(Problem))


def count_grounded_variables(problem: Problem) -> int:
    """return the grounded variables"""
    list_of_variables: list[str] = []
    for init_val in problem.initial_values:
        if str(init_val) not in list_of_variables:
            list_of_variables.append(str(init_val))
    for action in problem.actions:
        current_action: InstantaneousAction = action
        if len(current_action.parameters) != 0:
            continue
        for precon in current_action.preconditions:
            if str(precon) not in list_of_variables:
                list_of_variables.append(str(precon))
        for effect in current_action.effects:
            if str(effect.fluent) not in list_of_variables:
                list_of_variables.append(str(effect.fluent))
    for goal in problem.goals:
        if str(goal) not in list_of_variables:
            list_of_variables.append(str(goal))
    return len(list_of_variables)