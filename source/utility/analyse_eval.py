"""module to analyze results"""
import csv
from unified_planning.shortcuts import Problem, InstantaneousAction
from unified_planning.io import PDDLReader, PDDLWriter
from source.utility.db_handler import DBHandler
from source.utility.transform_grounded import transform_grounded_problem_to_standard
from source.model.plan_modifiers.modifier_util import  cost_leaving_precondition
from source.model.plan_modifiers.lin_modifier import LinModifier
from source.model.plan_modifiers.exp_modifier import ExpModifier

def analyse_all(csv_file_path: str, db_file_path: str) -> None:
    """analyse problems and write to a csv file"""
    db_handler = DBHandler(db_file_path)
    list_of_original_problems = db_handler.get_all_original_problems()
    data = []
    headers = (
            "amount_actions_grounded",
            "amount_variables_grounded",
            "plan_solvable_cost",
            "used_cost_penalty",
            "is_solvable_exp, is_solvable_lin",
            "amount_action_exp_variant",
            "amount_variables_exp_variant",
            "amount_action_lin_variant",
            "amount_variables_lin_variant",
            "total_amount_added_precons",
            "total_amount_removed_precons_exp",
            "total_amount_removed_precons_lin",
            "amount_same_removed_lin_exp"
    )
    data.append(headers)
    db_handler.look_into()
    for (original_problem_id, domain_file_path, problem_file_path, plan_solvable_cost,solve_time_milliseconds, error_text_original, is_longer_30_min) in list_of_original_problems:
        if error_text_original is None or is_longer_30_min == 1:
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
        
        # (action, added precondition)
        list_of_added_precons: list[tuple[str,str]] = db_handler.get_added_preconditions_by_id(original_problem_id)
        if list_of_added_precons is None:
            list_of_added_precons = []
            print("no added preconditions found")
        
        exp_modifier = ExpModifier(destroyed_problem, is_grounded=True)
        lin_modifier = LinModifier(destroyed_problem, is_grounded=True)

        amount_action_exp_variant, amount_variables_exp_variant = count_action_and_variables(exp_modifier.modified_problem_info.problem)
        amount_action_lin_variant, amount_variables_lin_variant = count_action_and_variables(lin_modifier.modified_problem_info.problem)

        exp_version_id = 1
        lin_version_id = 2

        result_id_exp: int = db_handler.find_corresponding_result_id(original_problem_id, exp_version_id)
        result_id_lin: int = db_handler.find_corresponding_result_id(original_problem_id, lin_version_id)

        (_,expected_prob_id_exp, modifier_id_exp, time_millisec_exp, error_text_exp) = db_handler.get_result_by_id(result_id_exp)
        (_,expected_prob_id_lin, modifier_id_lin, time_millisec_lin, error_text_lin) = db_handler.get_result_by_id(result_id_lin)

        if expected_prob_id_exp != original_problem_id:
            print("error problem id should be:" + str(original_problem_id) + "but is:" + str(expected_prob_id_exp))
        if modifier_id_exp != exp_version_id:
            print("error exp version id should be:" + str(modifier_id_exp) + "but is:" + str(exp_version_id))
        if expected_prob_id_lin != original_problem_id:
            print("error problem id should be:" + str(original_problem_id) + "but is:" + str(expected_prob_id_lin))
        if modifier_id_lin != lin_version_id:
            print("error lin version id should be:" + str(modifier_id_lin) + "but is:" + str(lin_version_id))
        
        total_amount_added_precons = len(list_of_added_precons)

        is_solvable_exp = error_text_exp is None
        is_solvable_lin = error_text_lin is None

        list_of_removed_precons_exp: list[tuple[str, str]] = []
        total_amount_removed_precons_exp: int = 0
        amount_added_and_removed_exp: int = 0


        if is_solvable_exp:
            list_of_removed_precons_exp: list[tuple[str, str]] = db_handler.get_left_preconditions_by_id(result_id_exp)
            total_amount_removed_precons_exp = len(list_of_removed_precons_exp)
            amount_added_and_removed_exp = 0
            
            for (action_name_added, precon_name_added) in list_of_added_precons:
                if is_in_removed_precon_list(action_name_added, precon_name_added, list_of_removed_precons_exp):
                    amount_added_and_removed_exp += 1
        

        list_of_removed_precons_lin: list[tuple[str, str]] = []
        total_amount_removed_precons_lin: int = 0
        amount_added_and_removed_lin: int = 0

        if is_solvable_lin:
            list_of_removed_precons_lin: list[tuple[str, str]] = db_handler.get_left_preconditions_by_id(result_id_lin)
            total_amount_removed_precons_lin = len(list_of_removed_precons_lin)
            amount_added_and_removed_lin = 0
            for (action_name_added, precon_name_added) in list_of_added_precons:
                if is_in_removed_precon_list(action_name_added, precon_name_added, list_of_removed_precons_lin):
                    amount_added_and_removed_lin += 1

        if is_solvable_exp and is_solvable_lin:
            amount_same_removed_lin_exp = 0
            for (action_exp, removed_precon_exp) in list_of_removed_precons_exp:
                for (action_lin, removed_precon_lin) in list_of_removed_precons_lin:
                    if action_exp == action_lin and removed_precon_exp == removed_precon_lin:
                        amount_same_removed_lin_exp += 1

        # grounded_action_amount, grounded_variables_amount, cost_grounded, cost_penalty, 
        # is_solvable_exp, is_solvable_lin,
        # exp_action_amount, exp_variable_amount, 
        # lin_action_amount, lin_variable_amount,
        # amount_addded_precons, 
        # amount_removed_precons_exp, amount_removed_precons_lin, 
        # same_removed_lin_exp
        
        data_tuple = (
            amount_actions_grounded,
            amount_variables_grounded,
            plan_solvable_cost,
            used_cost_penalty,
            is_solvable_exp, is_solvable_lin,
            amount_action_exp_variant if is_solvable_exp else None,
            amount_variables_exp_variant if is_solvable_exp else None,
            amount_action_lin_variant if is_solvable_exp else None,
            amount_variables_lin_variant if is_solvable_exp else None,
            total_amount_added_precons if is_solvable_exp else None,
            total_amount_removed_precons_exp if is_solvable_exp else None,
            total_amount_removed_precons_lin if is_solvable_exp else None,
            amount_same_removed_lin_exp if is_solvable_exp and is_solvable_lin else None
        )
        data.append(data_tuple)
    



        


    


        
        

        
        



def is_in_removed_precon_list(added_action: str, added_precon:str , removed_list: list[tuple[str, str]]) -> bool:
    """find if in list"""
    for (action_removed, precon_removed) in removed_list:
        if action_removed == added_action and added_precon == precon_removed:
            return True
    return False


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
    