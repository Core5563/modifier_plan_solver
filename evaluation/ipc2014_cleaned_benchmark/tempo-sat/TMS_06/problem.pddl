(define (problem prob3)
 (:domain domain-tms-2-3-light)
 (:objects 
 kiln0 - kiln8
 kiln0 - kiln20
 pone0 pone1 pone2 pone3 pone4 pone5 pone6 pone7 pone8 pone9 pone10 pone11 pone12 pone13 pone14 pone15 pone16 pone17 pone18 pone19 pone20 pone21 pone22 pone23 - piecetype1
 ptwo0 ptwo1 ptwo2 ptwo3 ptwo4 ptwo5 ptwo6 ptwo7 ptwo8 ptwo9 ptwo10 ptwo11 ptwo12 ptwo13 ptwo14 ptwo15 ptwo16 ptwo17 ptwo18 ptwo19 ptwo20 ptwo21 ptwo22 ptwo23 ptwo24 ptwo25 ptwo26 ptwo27 ptwo28 ptwo29 ptwo30 ptwo31 ptwo32 ptwo33 ptwo34 ptwo35 - piecetype2
 pthree0 pthree1 pthree2 pthree3 pthree4 pthree5 pthree6 pthree7 pthree8 pthree9 pthree10 pthree11 pthree12 pthree13 pthree14 pthree15 pthree16 pthree17 pthree18 pthree19 pthree20 pthree21 pthree22 pthree23 pthree24 pthree25 pthree26 pthree27 pthree28 pthree29 pthree30 pthree31 pthree32 pthree33 pthree34 pthree35 pthree36 pthree37 pthree38 pthree39 pthree40 pthree41 pthree42 pthree43 pthree44 pthree45 pthree46 pthree47 pthree48 pthree49 pthree50 pthree51 pthree52 pthree53 pthree54 pthree55 pthree56 pthree57 pthree58 pthree59 - piecetype3
)
 (:init 
  (energy)
)
 (:goal
  (and
     (baked-structure pthree30 pone10)
     (baked-structure pthree23 pthree49)
     (baked-structure ptwo28 pthree48)
     (baked-structure ptwo34 ptwo16)
     (baked-structure pthree52 pone17)
     (baked-structure pone23 ptwo25)
     (baked-structure pthree51 ptwo11)
     (baked-structure pone7 ptwo13)
     (baked-structure pthree34 ptwo22)
     (baked-structure ptwo3 ptwo30)
     (baked-structure pone2 ptwo6)
     (baked-structure pthree18 pthree25)
     (baked-structure ptwo15 pthree31)
     (baked-structure pthree9 pthree53)
     (baked-structure pone4 pthree16)
     (baked-structure pthree20 ptwo21)
     (baked-structure pthree43 pthree5)
     (baked-structure ptwo31 pthree24)
     (baked-structure ptwo10 ptwo8)
     (baked-structure pthree1 pone18)
     (baked-structure ptwo2 pthree41)
     (baked-structure pone19 pone15)
     (baked-structure pone14 pthree21)
     (baked-structure pone1 pone5)
     (baked-structure pthree45 pone3)
     (baked-structure pone21 ptwo9)
     (baked-structure pthree13 pthree36)
     (baked-structure pthree2 pthree39)
     (baked-structure pthree46 pthree6)
     (baked-structure pone16 pthree22)
     (baked-structure pthree10 ptwo26)
     (baked-structure ptwo24 ptwo5)
     (baked-structure pthree4 pthree26)
     (baked-structure pone20 ptwo17)
     (baked-structure ptwo32 pone8)
     (baked-structure pone22 pthree55)
     (baked-structure pone0 pthree44)
     (baked-structure pthree40 pthree42)
     (baked-structure pthree59 pthree56)
     (baked-structure ptwo12 ptwo14)
     (baked-structure pthree37 pone12)
     (baked-structure pone9 ptwo7)
     (baked-structure pthree28 ptwo4)
     (baked-structure pthree54 ptwo27)
     (baked-structure pthree19 pthree35)
     (baked-structure pone13 pthree12)
     (baked-structure ptwo0 pthree57)
     (baked-structure ptwo29 pthree50)
     (baked-structure pthree8 pthree32)
     (baked-structure ptwo23 pthree58)
     (baked-structure pthree47 pthree3)
     (baked-structure pone11 ptwo19)
     (baked-structure pthree0 pthree38)
     (baked-structure ptwo20 pthree27)
     (baked-structure pthree17 ptwo18)
     (baked-structure pthree7 ptwo33)
     (baked-structure pthree29 pthree33)
     (baked-structure pthree15 ptwo1)
     (baked-structure ptwo35 pthree14)
     (baked-structure pthree11 pone6)
))
 (:metric minimize (total-time))
)
