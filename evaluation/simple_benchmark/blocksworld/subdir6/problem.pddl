(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc blockd blocke blockf blockg blockh blocki blockj - block
 )
 (:init (hand_free) (on_top blockb blocka) (on_top blockc blockb) (on_top blockd blockc) (on_top blocke blockd) (on_top blockf blocke) (on_top blockg blockf) (on_top blockh blockg) (on_top blocki blockh) (on_top blockj blocki) (top_free blockj) (on_ground blocka))
 (:goal (and (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb) (on_ground blockc) (top_free blockc) (on_ground blockd) (top_free blockd) (on_ground blocke) (top_free blocke) (on_ground blockf) (top_free blockf) (on_ground blockg) (top_free blockg) (on_ground blockh) (top_free blockh) (on_ground blocki) (top_free blocki) (on_ground blockj) (top_free blockj)))
)
