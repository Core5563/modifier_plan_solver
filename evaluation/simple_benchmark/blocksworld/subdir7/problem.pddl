(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb - block
 )
 (:init (hand_free) (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb))
 (:goal (and (on_top blocka blockb) (top_free blocka) (on_ground blockb)))
)
