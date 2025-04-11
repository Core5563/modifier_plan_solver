(define (domain blocksworld-domain)
 (:requirements :strips :typing)
 (:types block)
 (:predicates (top_free ?b - block) (on_ground ?b - block) (on_top ?top - block ?buttom - block) (in_hand ?b - block) (hand_free))
 (:action take_from_ground
  :parameters ( ?b - block)
  :precondition (and (hand_free) (top_free ?b) (on_ground ?b))
  :effect (and (not (hand_free)) (not (top_free ?b)) (not (on_ground ?b)) (in_hand ?b)))
 (:action take_from_blocktower
  :parameters ( ?top - block ?under_top - block)
  :precondition (and (hand_free) (top_free ?top) (on_top ?top ?under_top))
  :effect (and (not (hand_free)) (not (top_free ?top)) (top_free ?under_top) (not (on_top ?top ?under_top)) (in_hand ?top)))
 (:action put_on_ground
  :parameters ( ?b - block)
  :precondition (and (in_hand ?b))
  :effect (and (hand_free) (on_ground ?b) (top_free ?b) (not (in_hand ?b))))
 (:action put_on_block
  :parameters ( ?to_put_on - block ?hand_block - block)
  :precondition (and (in_hand ?hand_block) (top_free ?to_put_on))
  :effect (and (hand_free) (not (in_hand ?hand_block)) (not (top_free ?to_put_on)) (on_top ?hand_block ?to_put_on) (top_free ?hand_block)))
)
