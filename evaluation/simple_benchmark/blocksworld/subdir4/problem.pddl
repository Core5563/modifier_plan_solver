(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   blocka blockb blockc blockd blocke blockf blockg blockh blocki blockj - block
 )
 (:init (hand_free) (on_ground blocka) (top_free blocka) (on_ground blockb) (top_free blockb) (on_ground blockc) (top_free blockc) (on_ground blockd) (top_free blockd) (on_ground blocke) (top_free blocke) (on_ground blockf) (top_free blockf) (on_ground blockg) (top_free blockg) (on_ground blockh) (top_free blockh) (on_ground blocki) (top_free blocki) (on_ground blockj) (top_free blockj))
 (:goal (and (on_top blocka blockb) (on_top blockb blockc) (on_top blockc blockd) (on_top blockd blocke) (on_top blocke blockf) (on_top blockf blockg) (on_top blockg blockh) (on_top blockh blocki) (on_top blocki blockj) (top_free blocka) (on_ground blockj)))
)
