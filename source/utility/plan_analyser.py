"""Module to analyse different aspects of plans"""
from unified_planning.shortcuts import Problem #type: ignore
from unified_planning.plans import SequentialPlan #type: ignore
from source.model.plan_modifiers.modifier_util import calculate_total_action_cost_metric

class PlanAnalyser:
    """to analyse different Aspects of plans"""

    def calculate_plan_cost(self, problem: Problem, plan: SequentialPlan) -> int:
        """calculate the cost of the problem"""
        #plan cost
        cost = 0

        #extract cost per action
        _ , action_metric = calculate_total_action_cost_metric(problem)

        #sum cost of plan
        for action in plan.actions:
            cost += action_metric[action.name]

        return cost