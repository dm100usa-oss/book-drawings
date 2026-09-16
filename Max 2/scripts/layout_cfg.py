import texts
T = texts.S
def fr(p, gi=0):
    return T[p][gi][1]
FW = (None, None)   # полная ширина
def Z(y0, y1, frags, x0=None, x1=None, align='auto', es_x=None):
    return dict(y0=y0, y1=y1, x0=x0, x1=x1, frags=frags, align=align, es_x=es_x)

P26A = [('p', ["Also, for some reason, everyone loves to lie in the sun on the beach. I also lay down, but for just a bit. Sitting in one spot was boring."],
              ["En la playa, por alguna razón, a todos les gusta tomar el sol. Yo también me acosté, pero solo un poquito. Estar en un solo lugar era aburrido."])]
P27B = [('p', ["I ran off to play with the waves! The waves were catching up with me, and I was running away from them. It was fun!"],
              ["¡Corrí rápido a jugar con las olas! Las olas me perseguían y yo me escapaba de ellas. ¡Fue divertido!"])]
P41A = [('p', ["There was also a real orchestra there. Musicians were wearing cool hats and had different instruments."],
              ["También había una verdadera banda. Eran músicos con sombreros bonitos y diferentes instrumentos."])]
P41B = [('p', ["They played various melodies, and they also allowed me to play their largest instrument. It’s called a drum. It is so loud that you can hear it from far, far away!"],
              ["Tocaban melodías y también me dejaron tocar el instrumento más grande. Se llama tambor. ¡Es tan ruidoso que se escucha desde muy, muy lejos!"])]
P46A = [('p', ["The park is so beautiful! There are lots of different trees, flowers and birds. There are even squirrels there! They are very curious animals!"],
              ["¡El parque es tan bonito! Hay muchos árboles diferentes, flores y pájaros. ¡Incluso hay ardillas! ¡Son muy curiosas!"])]
P47B1 = [('p', ["The squirrels sat in the tree and watched me blow bubbles. They really liked the bubbles!"],
               ["Las ardillas estaban sentadas en un árbol y miraban cómo yo hacía burbujas de jabón. ¡Les encantaron!"])]
P47B2 = [('p', ["I wanted to treat the squirrels to some cookies, but they ran away. The next time I see them, we will definitely become friends!"],
               ["Quería ofrecerles galletas, pero por alguna razón se fueron corriendo. La próxima vez que las vea, ¡seguro que nos haremos amigos!"])]
P30 = fr(30)
P28A = [('p', ["There are beautiful shells and pebbles on the beach. You can collect them and take them home. I collected a whole lot."],
              ["En la playa hay conchas y piedrecitas bonitas. Se pueden recoger y llevártelas a casa. Recogí muchas, muchas."])]
P29B = [('p', ["You know, if you put a shell to your ear, you can hear the sound of the ocean. It’s true! I keep the shells and pebbles in my room now, so I can play with them and remember what a great time I had at the beach!"],
              ["Sabes, si acercas una concha a tu oído, puedes escuchar cómo suena el océano. ¡De verdad! ¡Ahora las conchas y piedrecitas están en mi habitación, juego con ellas y recuerdo lo genial que fue ir a la playa!"])]
P12A = [('p', ["I saw Monkeys. They can climb trees and jump from branch to branch."],
              ["¡Vi a los Monos! Pueden trepar por los árboles y saltar de rama en rama."])]
P13B = [('p', ["They are also very funny and love to play with each other. I waved to them and they waved back."],
              ["Y además son muy divertidos y les encanta jugar entre ellos. Los saludé con la mano y ellos me saludaron de vuelta."])]
P40A = [('p', ["There was also a real orchestra there. Musicians were wearing cool hats and had different instruments. They played various melodies, and they also allowed me to play their largest instrument."],
              ["También había una verdadera banda. Eran músicos con sombreros bonitos y diferentes instrumentos. Tocaban melodías y también me dejaron tocar el instrumento más grande."])]
P41B = [('p', ["It’s called a drum. It is so loud that you can hear it from far, far away!"],
              ["Se llama tambor. ¡Es tan ruidoso que se escucha desde muy, muy lejos!"])]

CFG = {
 4:  [Z(200, 2350, fr(4)[:-1], x1=2250)],
 5:  [Z(200, 880, fr(4)[-1:], align='center')],
 6:  [Z(200, 2150, fr(6), x1=2080)],
 9:  [Z(2300, 3190, fr(9), x1=2100, align='center')],
 10: [Z(200, 1650, fr(10))],
 12: [Z(190, 735, P12A, align='center')],
 13: [Z(190, 735, P13B, align='center')],
 14: [Z(190, 1330, fr(14), x1=1600, align='top0')],
 16: [Z(200, 1850, fr(16), x1=2150)],
 18: [Z(175, 1000, fr(19)[:3], x0=650, x1=2100, align='center')],
 19: [Z(153, 580, fr(19)[3:5], align='center'), Z(585, 1745, fr(19)[5:], x0=198, x1=1820, es_x=(520, 1820), align='top0')],
 20: [Z(200, 1450, fr(20))],
 22: [Z(200, 1600, fr(22))],
 23: [Z(200, 1500, fr(23))],
 24: [Z(200, 1650, fr(24))],
 25: [Z(170, 830, fr(25), align='center')],
 26: [Z(200, 730, P26A, align='center')],
 27: [Z(200, 800, P27B, align='center')],
 28: [Z(185, 740, P28A, align='center')],
 29: [Z(190, 1740, P29B + fr(29, 1))],
 30: [Z(170, 770, P30[:2], align='center'), Z(1480, 2600, P30[2:4], x0=350, x1=2150, align='center')],
 31: [Z(158, 800, P30[4:], align='center')],
 32: [Z(2290, 3258, [('p', fr(32)[0][1][:2], fr(32)[0][2][:2])], x0=300, align='center')],
 33: [Z(175, 745, [('p', fr(32)[0][1][2:], fr(32)[0][2][2:])], align='center')],
 35: [Z(200, 950, fr(35), align='center')],
 36: [Z(200, 960, fr(36), align='center')],
 39: [Z(200, 1600, fr(39))],
 40: [Z(165, 860, P40A, align='center')],
 41: [Z(190, 760, P41B, align='center')],
 42: [Z(200, 1400, fr(42))],
 44: [Z(180, 820, fr(45)[:2], align='center')],
 45: [Z(200, 2550, fr(45)[2:])],
 46: [Z(200, 730, P46A, align='center')],
 47: [Z(200, 740, P47B1, align='center'), Z(820, 1900, P47B2, x0=1150, align='center')],
 48: [Z(200, 820, fr(48), align='center')],
 50: [Z(200, 2000, fr(50))],
}
