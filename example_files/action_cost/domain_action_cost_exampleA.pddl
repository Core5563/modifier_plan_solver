(define (domain action_cost_simple_domain)
    (:requirements :strips :action-costs)
    (:predicates (TRUEX ?x) (TRUEZ ?x) (TRUEP ?x) (TRUEQ ?x))
    (:functions (total-cost) - number)
    (:action a1
        :parameters (?s)
        :precondition (and (TRUEX ?s)) 
        :effect (and (TRUEZ ?s) 
                     (increase (total-cost) 1)
                )
    )
    (:action a2
        :parameters (?x)
        :precondition (TRUEZ ?x)
        :effect (and (TRUEP ?x) (TRUEQ ?x)
                     (increase (total-cost) 2)
                )
    )
)