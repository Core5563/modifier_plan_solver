(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc - block
 )
 (:init (hand_free) (top_free blockc) (on_top blockc blockb) (on_top blockb blocka) (on_ground blocka))
 (:goal (and (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb) (on_ground blockc) (top_free blockc)))
)
