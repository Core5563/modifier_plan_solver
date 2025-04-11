(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc blockd blocke blockf blockg blockh blocki blockj - block
 )
 (:init (hand_free) (on_top blockb blocka) (on_top blockc blockb) (on_top blockd blockc) (on_top blocke blockd) (on_top blockf blocke) (on_top blockg blockf) (on_top blockh blockg) (on_top blocki blockh) (on_top blockj blocki) (top_free blockj) (on_ground blocka))
 (:goal (and (on_top blocka blockb) (on_top blockb blockc) (on_top blockc blockd) (on_top blockd blocke) (on_top blocke blockf) (on_top blockf blockg) (on_top blockg blockh) (on_top blockh blocki) (on_top blocki blockj) (top_free blocka) (on_ground blockj)))
)
