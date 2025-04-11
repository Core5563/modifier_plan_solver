(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc - block
 )
 (:init (hand_free) (top_free blockc) (on_top blockc blockb) (on_top blockb blocka) (on_ground blocka))
 (:goal (and (on_top blocka blockb) (on_top blockb blockc) (top_free blocka) (on_ground blockc)))
)
