(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc - block
 )
 (:init (hand_free) (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb) (on_ground blockc) (top_free blockc))
 (:goal (and (on_top blocka blockb) (on_top blockb blockc) (top_free blocka) (on_ground blockc)))
)
