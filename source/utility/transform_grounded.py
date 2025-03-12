from unified_planning.shortcuts import Problem, FNode, InstantaneousAction

def transform_grounded_problem_to_standard(problem: Problem) -> Problem:
    """standardize the input"""

    return_problem: Problem = problem.clone()
    goal_expressions: list[FNode] = []
    #find goal expressions
    for precon in return_problem.goals:
        if precon.is_and():
            and_expression: FNode = return_problem.goals[0]
            for fnode_expression in and_expression.args:
                goal_expressions.append(fnode_expression)
        else:
            goal_expressions.append(precon)

    #remove goals
    return_problem.clear_goals()

    #add goals them back in standardized way
    for precon in goal_expressions:
        return_problem.add_goal(precon)

    for action in return_problem.actions:
        inst_action: InstantaneousAction = action
        precon_expressions: list[FNode] = []
        
        #find preconditions
        for precon in inst_action.preconditions:
            if precon.is_and():
                and_expression: FNode = precon
                for fnode_expression in and_expression.args:
                    precon_expressions.append(fnode_expression)
            else:
                precon_expressions.append(precon)

        #remove preconditions
        inst_action.clear_preconditions()

        #add preconditions back in standardized way
        for precon in precon_expressions:
            inst_action.add_precondition(precon)

    return return_problem