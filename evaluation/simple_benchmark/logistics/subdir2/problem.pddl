(define (problem logistic_problem-problem)
 (:domain logistic_problem-domain)
 (:objects
   truck_land_1 truck_land_2 ship - transport
   warehouse_land_1 warehouse_land_2 harbor_land_1 harbor_land_2 - location
   valuable_goods - goods
 )
 (:init (is_truck truck_land_1) (at_location truck_land_1 warehouse_land_1) (at_location truck_land_2 warehouse_land_2) (is_truck truck_land_2) (is_ship ship) (at_location ship harbor_land_1) (road_from_to harbor_land_1 warehouse_land_1) (road_from_to warehouse_land_1 harbor_land_1) (road_from_to harbor_land_2 warehouse_land_2) (road_from_to warehouse_land_2 harbor_land_2) (sea_access harbor_land_1) (sea_access harbor_land_2) (goods_in_location valuable_goods warehouse_land_1))
 (:goal (and (goods_in_location valuable_goods harbor_land_1)))
)
