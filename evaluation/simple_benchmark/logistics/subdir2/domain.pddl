(define (domain logistic_problem-domain)
 (:requirements :strips :typing)
 (:types transport location goods land)
 (:predicates (at_location ?transport - transport ?location - location) (road_from_to ?road_from - location ?road_to - location) (sea_access ?location - location) (goods_in_location ?goods - goods ?location - location) (goods_in_transport ?goods - goods ?transport - transport) (location_in_land ?location - location ?land - land) (is_ship ?transport - transport) (is_truck ?transport - transport))
 (:action load
  :parameters ( ?goods - goods ?transport - transport ?location - location)
  :precondition (and (goods_in_location ?goods ?location) (at_location ?transport ?location))
  :effect (and (not (goods_in_location ?goods ?location)) (goods_in_transport ?goods ?transport)))
 (:action unload
  :parameters ( ?goods - goods ?transport - transport ?location - location)
  :precondition (and (goods_in_transport ?goods ?transport) (at_location ?transport ?location))
  :effect (and (goods_in_location ?goods ?location) (not (goods_in_transport ?goods ?transport))))
 (:action move_truck
  :parameters ( ?transport - transport ?move_from - location ?move_to - location)
  :precondition (and (is_truck ?transport) (at_location ?transport ?move_from) (road_from_to ?move_from ?move_to))
  :effect (and (not (at_location ?transport ?move_from)) (at_location ?transport ?move_to)))
 (:action move_ship
  :parameters ( ?transport - transport ?move_from - location ?move_to - location)
  :precondition (and (is_ship ?transport) (sea_access ?move_from) (sea_access ?move_to) (at_location ?transport ?move_from))
  :effect (and (not (at_location ?transport ?move_from)) (at_location ?transport ?move_to)))
)
