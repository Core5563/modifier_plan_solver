"""an Plan validator"""
from unified_planning.shortcuts import Problem, InstantaneousAction, Fluent, PlanValidator #type: ignore
from unified_planning.plans import ActionInstance, SequentialPlan #type: ignore
from unified_planning.engines import ValidationResult #type: ignore
from source.model.plan_modifiers.modified_plan import ModifiedPlanInformation, ModifiedProblemInfo


class ModifiedPlanValidator:
    """Component to validate if modified Problem is actually solved by the plan"""
    def __init__(self, modified_plan: ModifiedPlanInformation, grounded_problem: Problem, modified_problem: ModifiedProblemInfo):
        
        #alter the verification problem according to the left preconditions
        verification_problem = grounded_problem.clone()

        left_precon_mapping: dict[str, tuple[InstantaneousAction, list[Fluent]]] = modified_problem.action_to_left_precondition_mapping
        for _ , (action, list_of_left_precon_fluents) in left_precon_mapping.items():
            current_action: InstantaneousAction = action

            #get corresponding action in verify problem
            to_modify_action: InstantaneousAction = verification_problem.action(action.name)

            #clear preconditions
            to_modify_action.clear_preconditions()

            list_of_left_precon_names = [precon.name for precon in list_of_left_precon_fluents]

            #no name into all of that
            for precondition in current_action.preconditions:
                #add precondition if not in the left preconditions list
                if not (precondition.fluent().name in list_of_left_precon_names):
                    to_modify_action.add_precondition(verification_problem.fluent(precondition.fluent().name))

        #make a sequential plan to verify
        action_instance_list: list[ActionInstance] = []
        
        for action in modified_plan.backtracked_grounded_plan_result:
            action_instance_list.append(ActionInstance(verification_problem.action(action.name)))
        
        to_verify_plan: SequentialPlan = SequentialPlan(action_instance_list)

        self.verification_problem = verification_problem
        self.to_verify_plan = to_verify_plan
        self.validation_result: ValidationResult | None = None

    def verify_plan(self) -> ValidationResult:
        """verify the modified Problem"""
        validator = PlanValidator(problem_kind=self.verification_problem.kind, plan_kind=self.to_verify_plan.kind)
        validation_result: ValidationResult = validator.validate(self.verification_problem, self.to_verify_plan)
        self.validation_result = validation_result
        return validation_result