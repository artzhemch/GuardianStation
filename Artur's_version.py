import numpy as np
import cv2 as cv
import math as mh
import time as ti
import random as rm
import copy

# region Глобальные переменные
wname = 'Body and photons'  # Название окна
shipsize = 4                
shcnt = 3                   
fcnt = 200                  # Количество фотонов в пучке
fv = 10                     # Скорость фотонов
bvel = 5                   # Скорость кораблей
fr = 1                      # Радиус фотонов
wth = 1*1280                # Ширина окна
lth = 1*720                 # Высота
x0 = int(wth/2)             # Начало координат
y0 = int(lth/2)             #
stR = 30                    # Радиус установки
stTh = 20                   # Толщина контура установки
pr = 1                      # Радиус точки

#<A>
turretR = 22 #размер турели
bulletSpeed = 21#скорость снаряда
bulletR = 7# радиус снаряда
#</A>
# endregion

#<A>
class Turret():#класс турели
    def __init__(self, coordinates):#при создании новой турели задаём её координаты
        self.x, self.y = coordinates
    def draw(self, color):#рисуем турель
        cv.circle(img, (self.x,self.y), turretR, color, -1)
    def get_target_location(self, coordinates):
        #Получаем точку, в которую надо стрелять следующим образом: находим t, при котором r(t) - vt = min, где v - скорость снаряда,
        #при достаточном размере снаряда (или при большом массиве точек траектории), гарантированно попадаем
        tmin = 0
        range_min = 10000
        for t in range(len(coordinates)):
            if ((self.x - coordinates[t][0]) ** 2 + (self.y - coordinates[t][1]) ** 2) ** 0.5 - bulletSpeed * t < range_min:
                tmin = t
                range_min = ((self.x - coordinates[t][0]) ** 2 + (self.y - coordinates[t][1]) ** 2) ** 0.5 - bulletSpeed * t
        print(coordinates[tmin])
        return(coordinates[tmin])
    def fire(self, coordinates): #Стреляем по координатам корабля, возвращаем объект типа bullet
        return Bullet((self.x, self.y), self.get_target_location(coordinates))


class Bullet():
    def __init__(self, start, target):#инициализируем снаряд, задавая начальную точку и точку прилёта снаряда, находим проекцию скоростей
        r = ((start[0] - target[0]) ** 2 + (start[1] - target[1]) ** 2) ** 0.5
        self.x_speed = int((target[0] - start[0]) * bulletSpeed / r)
        self.y_speed = int((target[1] - start[1]) * bulletSpeed / r)
        self.x = start[0]
        self.y = start[1]
    def draw(self, color):#рисуем снаряд
        cv.circle(img, (self.x,self.y), bulletR, color, -1)
    def move(self):#сдвигаем снаряд, соответственно его времени
        self.x += self.x_speed
        self.y += self.y_speed
#</A>
# region Функции физики

# функция сообщает координаты столкновений фотонов с установкой
def photCollid(fmass, pmass):
    for b in range(len(fmass)):
        bunch = fmass[b]
        f = 0
        while f < len(bunch):
            foton = bunch[f]
            lx = int(foton[0]) - x0
            ly = int(foton[1]) - y0
            l = mh.sqrt(lx**2+ly**2)
            if l <= stR + stTh*0.5 and l > stR - stTh*0.5:
                pmass.append([ foton[0], foton[1], foton[2] ]) 
                del bunch[f]
                f -= 1
            f += 1

# функция удаляет из массива точек все элементы, кроме тех, что с углом 10.
def clearPmass(pmass):
    i = 0
    while i < len(pmass):
        if not pmass[i][2] == 10:
            del pmass[i]
            i -= 1
        i += 1

# Cоздание пучка фотонов
def createBunch(x, y, fmass):                      
    fmass.append([[0,0,0] for c in range(fcnt)])    # добавляем следующий пучок в список пучков, пока присваиваем нули
    bunch = fmass[len(fmass)-1]                     # bunch это пучок который мы создаем
    for i in range(fcnt):                           # для каждого фонона из пучка...
        foton = bunch[i]                            # foton это фотон которому мы присваиваем начальные координаты
        foton[0] = x                                # присваиваем координаты из аргументов
        foton[1] = y                                #
        foton[2] = 2*3.14*(i/fcnt)                  # присваиваем угол, деля круг на равные части по количеству фотонов.


# функция возвращает угол между вектором с началом в точке (x, y) концом в точке (x1, y1) и вектором, направленным вдоль оси x
def setAngle(x,y,x1,y1):  
    # условие нужно, чтобы устранить неопределенность в знаке при вычислении из скалярного произведения 
    if (y1-y) < 0:  # если точка имеет большую, чем точка 1, координату по y, то есть на картинке она НИЖЕ
        return 2*mh.pi-mh.acos((x1-x)/(mh.sqrt(mh.pow(x1-x,2)+mh.pow(y1-y,2)))) 
    else:           # если точка на картинке находится ВЫШЕ
        return mh.acos((x1-x)/(mh.sqrt(mh.pow(x1-x,2)+mh.pow(y1-y,2))))

# функция возвращает угол между вектором с началом в точке (x, y) концом в точке (x1, y1) и вектором, направленным вдоль оси x
# с разбросом в +/- 45 градусов
def setAngleRand(x,y,x1,y1):  
    # условие нужно, чтобы устранить неопределенность в знаке при вычислении из скалярного произведения 
    if (y1-y) < 0:  # если точка имеет большую, чем точка 1, координату по y, то есть на картинке она НИЖЕ
        return 2*mh.pi-mh.acos((x1-x)/(mh.sqrt(mh.pow(x1-x,2)+mh.pow(y1-y,2)))) + rm.random()*mh.pi*0.5 - mh.pi*0.25
    else:           # если точка на картинке находится ВЫШЕ
        return mh.acos((x1-x)/(mh.sqrt(mh.pow(x1-x,2)+mh.pow(y1-y,2)))) + rm.random()*mh.pi*0.5 - mh.pi*0.25

# функция добавляет еще один корабль в shmass. присваивает ему заданные координаты, и если угол не задан, корабль летит в центр.
def createShip(shmass, x, y, afa = 10):             # функция для создания корабля, принимает массив кораблей, координаты, направление (опц.)
    if afa == 10:                                   # если афа не задана, то она принимает десятку как знак того, что корабль
        afa = setAngleRand(x,y,x0,y0)                   # должен лететь в точку x0, y0. 
    shmass.append([x,y,afa]) 

# функция даёт приращение координате каждого корабля вдоль его направления и создаёт в этой точке пучок фотонов.
def moveShip(shmass, fmass):
    for i in range(len(shmass)):
        ship = shmass[i]                                # ship это корабль которому мы даём приращение
        ship[0] = (ship[0] + (bvel*mh.cos(ship[2])))   # даём приращение вдоль x
        ship[1] = (ship[1] + bvel*mh.sin(ship[2]))   # и вдоль y
        createBunch(ship[0],ship[1], fmass)             # создаем пучок фотонов в этой точке

# функция даёт приращение координате каждого фотона вдоль его направления.
def movePhot(fmass):
    for b in range (len(fmass)):                    # для каждого пучка...
        f = 0
        while f < len(fmass[b]):             # для каждого фотона из пучка...
            f_afa = fmass[b][f][2]                  # работаем с углом поворота фотона относительно горизонтальной оси, по часовой стрелке!
            x = fmass[b][f][0] + fv*mh.cos(f_afa)
            y = fmass[b][f][1] + fv*mh.sin(f_afa)
            if (x <= wth and x >= 0 and y <= lth and y >= 0):
                fmass[b][f][0] = (fmass[b][f][0] + fv*mh.cos(f_afa)) # приращение координат фотона в направлении этого угла
                fmass[b][f][1] = (fmass[b][f][1] + fv*mh.sin(f_afa)) #
            else: 
                del fmass[b][f]
                f -= 1
            f += 1
 # endregion

# region Функции графики
# функция рисует точку, 
def drawPoints(pmass, color):
    for i in range(len(pmass)):
        point = pmass[i]
        cv.circle(img, (int(point[0]), int(point[1])), pr, color, -1)

# функция рисует установку
def drawStation(color):
    cv.circle(img, (x0,y0), stR, color, stTh)

# функция рисует корабли, то есть кружки, центры кружков хранятся в shmass, радиус - в глобальной переменной shipsize
def drawShip(shmass, color):       
    for i in range(len(shmass)):
        ship = shmass[i]
        cv.circle(img, (int(ship[0]), int(ship[1])), shipsize, color, -1)

# функция рисует фотоны, то есть кружки, центры кружков хранятся в fmass, радиус - в глобальной переменной fr
def drawPhot(fmass, color):
    for b in range(len(fmass)):
        bunch = fmass[b]
        for f in range(len(bunch)):
            foton = bunch[f]
            cv.circle(img, (int(foton[0]), int(foton[1])), fr, color, -1)
# endregion

# Обработка физики
def phys(fmass, shmass, pmass, bullets): #Обработка всей физики #<A>
    #Движение тела и испускание им фотонов
    moveShip(shmass, fmass)
    movePhot(fmass)
    for bullet in bullets:#<A>
        bullet.move()
# Обработка графики
def graph(draw, img, fmass, shmass, pmass, bullets, turret):    # draw: если 1, то закрашиваем, если 0 - то стираем, то есть рисуем черным#<A>
    # цвет закрашивания
    if draw == 1:
        color, color1, color2, color3 = (255,255,255), (0,255,255), (0, 0, 255), (255, 0, 0) #белый и желтый#<A>
    else:
        color, color1, color2, color3 = (0,0,0), (0,0,0), (0,0,0), (0,0,0) # черный (стираем)#<A>



    clearPmass(pmass)           # стираем старые точки из pmass, кроме тех, что с углом 10
    photCollid(fmass, pmass)    # ищем новые столкновения фотонов, заносим в pmass


    drawStation(color)
    drawShip(shmass, color)
    drawPhot(fmass, color1)
    drawPoints(pmass, color2)
    turret.draw((255,255,0))#отрисовываем турель #<А>
    for bullet in bullets:#<A>
        bullet.draw(color3)

# Главная функция
def main():
    fmass = [[]]                        # создаём трёхмерный массив, хранящий все пучки, каждый пучок хранит все фотоны, фотоны - 
                                        # свои координаты и угол относительно направления оси x по часовой стрелке.
    shmass = []                         # массив кораблей, хранящий каждый корабль, корабль хранит свои координаты и угол.
    pmass = []                          # массив точек, в него заносится координаты и угол фотонов, проходящих через установку.
    bullets = []
    createShip(shmass, 500, 300)
    turret1 = Turret((turretR + 5, turretR + 5)) # создаём турель в верхнем левом углу <A>
    bullets.append(turret1.fire([(100, 30), (100, 60), (100, 90), (100, 120), (100, 150), (100, 180), (100, 210), (100, 240), (100, 270), (100, 300), (100, 330)]))#тестовый выстрел, для примера <A>
    bullets.append(turret1.fire([(200, 30), (200, 60), (200, 90), (200, 120), (200, 150), (200, 180), (200, 210), (200, 240), (200, 270), (200, 300), (200, 330)]))
    bullets.append(turret1.fire([(300, 30), (300, 60), (300, 90), (300, 120), (300, 150), (300, 180), (300, 210), (300, 240), (300, 270), (300, 300), (300, 330)]))
    bullets.append(turret1.fire([(400, 30), (400, 60), (400, 90), (400, 120), (400, 150), (400, 180), (400, 210), (400, 240), (400, 270), (400, 300), (400, 330)]))
    for t in range(100): # выполняем программу в течение стольких итераций
        graph(0, img, fmass, shmass, pmass, bullets, turret1)    # стираем старое
        phys(fmass, shmass, pmass, bullets)             # изменяем координаты в соответствии со скоростями #<А>
        graph(1, img, fmass, shmass, pmass, bullets,turret1)    # рисуем новое
        cv.imshow(wname, img)           
        cv.waitKey(1)
cv.namedWindow(wname, cv.WINDOW_NORMAL) # создаём окно размером 1280 на 720
cv.resizeWindow(wname, 1280, 720)       #
img = np.zeros((lth, wth, 3))           # Массив для самой картинки, с кораблями и фотонами и установкой

main() 