(define (domain grounder_none_problem-domain)
 (:requirements :strips)
 (:predicates (x) (y) (z) (p) (q))
 (:action a1
  :parameters ()
  :effect (and (z) (p)))
 (:action a2
  :parameters ()
  :precondition (and (z) (y))
  :effect (and (q)))
)
