(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb - block
 )
 (:init (hand_free) (on_top blockb blocka) (top_free blockb) (on_ground blocka))
 (:goal (and (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb)))
)
