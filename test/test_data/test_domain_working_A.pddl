(define (domain simple_solvableA)
    (:predicates (TRUEX ?x) (TRUEZ ?x) (TRUEP ?x) (TRUEQ ?x))
    (:action a1
        :parameters (?s)
        :precondition (and (TRUEX ?s)) 
        :effect (TRUEZ ?s)
    )
    (:action a2
        :parameters (?x)
        :precondition (TRUEZ ?x)
        :effect (and (TRUEP ?x) (TRUEQ ?x))
    )
)