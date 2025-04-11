(define (domain pseudo_strips-domain)
 (:requirements :strips :typing)
 (:types obj)
 (:predicates (x ?o - obj) (y ?o - obj) (z ?o - obj) (p ?o - obj) (q ?o - obj))
 (:action a1
  :parameters ( ?o - obj)
  :precondition (and (x ?o) (y ?o))
  :effect (and (p ?o) (z ?o)))
 (:action a2
  :parameters ( ?o - obj)
  :precondition (and (z ?o))
  :effect (and (q ?o)))
)
