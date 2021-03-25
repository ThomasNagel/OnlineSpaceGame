import socket 
import threading
import pickle
import time
import random


###Server
#Constants
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
MAXCLIENTS = 4

#Create server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clientCount = 0

###Game
#Constants
WIDTH, HEIGHT = 500, 800
RED = (220, 10, 10)
GREEN = (0, 190, 20)
BLUE = (40, 40, 240)
YELLOW = (255, 190, 00)
GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BACKROUND = (20, 20, 40)

TICKS_SEC = 60

#Player settings
FORCE = 210
SLOW = 6
BOOST = 150
BOOST_LIMIT = 9
BORDER = 20 #distance from the border player can be
PLAYER_SIZE = 30
MAXLIVES = 5
Hit_shade = 0
HIT_EFFECT = 80
HIT_SHADE_DECREASE = 50
DEATH_ANIMATION = 3 

#Meteor settings
SPAWN_LOCATION = -30
SPAWN_CYCLE = 0.065
SPAWN_CHANCE = 11
M_X_SPEED = 30 #random value between X_SPEED and - X_SPEED
BASE_Y_SPEED = 210
M_MIN_SIZE = 25
M_MAX_SIZE = 40

#Data storage
Player_list = list()
Meteor_list = list()
keyList = list()
last_cycle_time = 0


###Classes
class GameState():
    def __init__(self):
        self.playerData = list()
        self.meteorData = list()
        self.time = 0
        
    def update_state(self):
        self.playerData.clear()
        for player in Player_list:
            self.playerData.append((player.lives, player.size, (player.x, player.y), player.colour))
        self.meteorData.clear()
        for meteor in Meteor_list:
            self.meteorData.append((meteor.size, (meteor.x, meteor.y), meteor.colour))
        self.time = int(Time)
        
class Player():
    x = WIDTH // 2
    y = HEIGHT - 30
    x_speed = 0
    y_speed = 0
    size = PLAYER_SIZE
    lives = MAXLIVES

    def __init__(self, colour, client_id):
        self.colour = colour
        self.client_id = client_id

    def move(self):
        if keyList[self.client_id][0] == "1": #up
            self.y_speed = self.y_speed - (FORCE * loop_time)
            if self.y_speed > -BOOST_LIMIT:
                self.y_speed = self.y_speed - (BOOST * loop_time)
        if keyList[self.client_id][1] == "1": #down
            self.y_speed = self.y_speed + (FORCE * loop_time)
            if self.y_speed < BOOST_LIMIT:
                self.y_speed = self.y_speed + (BOOST * loop_time)
        if keyList[self.client_id][2] == "1": #left
            self.x_speed = self.x_speed - (FORCE * loop_time)
            if self.x_speed > -BOOST_LIMIT:
                self.x_speed = self.x_speed - (BOOST * loop_time)
        if keyList[self.client_id][3] == "1": #right
            self.x_speed = self.x_speed + (FORCE * loop_time)
            if self.x_speed < BOOST_LIMIT:
                self.x_speed = self.x_speed + (BOOST * loop_time)

        self.y_speed = self.y_speed - self.y_speed * SLOW * loop_time
        self.x_speed = self.x_speed - self.x_speed * SLOW * loop_time
        self.y = self.y + self.y_speed
        self.x = self.x + self.x_speed
        
        if self.y < BORDER:
            self.y = BORDER
            self.y_speed = 0
        elif self.y > HEIGHT - BORDER:
            self.y = HEIGHT - BORDER
            self.y_speed = 0
        if self.x < BORDER:
            self.x = BORDER
            self.x_speed = 0
        elif self.x > WIDTH - BORDER:
            self.x = WIDTH - BORDER
            self.x_speed = 0
        
    def collision(self):
        slim = PLAYER_SIZE / 2 + 5 #makes the x len of the hitbox smaller
        for i in range(len(Meteor_list) -1, -1, -1):
            if Meteor_list[i].x > self.x:
                distance = (self.x - Meteor_list[i].x - slim)**2 + (self.y - Meteor_list[i].y)**2
            else:
                distance = (self.x - Meteor_list[i].x + slim)**2 + (self.y - Meteor_list[i].y)**2
            if (self.size + Meteor_list[i].size)**2 > distance:
                self.lives = self.lives - 1
                del Meteor_list[i]

class Meteor():
    def __init__(self):
        self.x = random.randint(10, WIDTH - 10)
        self.y = SPAWN_LOCATION
        self.x_speed = random.randint(-M_X_SPEED, M_X_SPEED)
        self.y_speed = BASE_Y_SPEED + (((Time)**(4/5)) * 15)
        self.size = random.randint(M_MIN_SIZE, M_MAX_SIZE)
        shade = random.randint(-20, 25)
        self.colour = (GREY[0] + shade, GREY[1] + shade, GREY[2] + shade)

    def move(self):
        self.x = self.x + (self.x_speed * loop_time)
        self.y = self.y + (self.y_speed * loop_time)
        

###Functions
#Server functions
def handle_client(conn, addr, client_id):
    global clientCount
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        if start_signal:
            conn.send(str(client_id).encode(FORMAT))
            break
    
    connected = True
    while connected:
        msg = conn.recv(32).decode(FORMAT)
        if msg:
            if msg == DISCONNECT_MESSAGE:
                connected = False
                clientCount = clientCount - 1
            else:
                keyList[client_id] = msg.split()
                conn.send(pickle.dumps(gamedata))
            
    conn.close()

def start():
    global clientCount, start_signal
    start_signal = False

    total_clients = int(input("Enter total amount of connecting clients:")) #semi temp
    
    server.listen(MAXCLIENTS)
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        conn, addr = server.accept() #Wait for new client to connect
        thread = threading.Thread(target=handle_client, args=(conn, addr, clientCount))
        thread.start()
        clientCount = clientCount + 1
        keyList.append("0000")
        
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        if clientCount >= total_clients:#semi temp
            start_signal = True
            break
        
    game()

#Game functions
def spawn_meteor():
    global last_cycle_time

    if Time > last_cycle_time + SPAWN_CYCLE:
        last_cycle_time = Time
        extra = int((Time)**(1/2))
        if extra >= SPAWN_CHANCE:
            extra = SPAWN_CHANCE - 1
        if random.randint(0, SPAWN_CHANCE - extra) == 0:
            Meteor_list.append(Meteor())
    
    for i in range(len(Meteor_list) -1, -1, -1):
        if Meteor_list[i].y > HEIGHT - SPAWN_LOCATION:
            del Meteor_list[i]
    
def game():
    global gamedata, loop_time, Time, can_spawn_meteor
    can_spawn_meteor = True
    gamedata = GameState() #This object contains all the game data that will be send to the client

    for i in range(clientCount):
        Player_list.append(Player([RED, BLUE, YELLOW, GREEN][i], i))

    start_loop_time = time.time()
    Start_time = time.time()
    while True:
        loop_time = time.time() - start_loop_time
        start_loop_time = time.time()
        Time = time.time() - Start_time
        
        
        spawn_meteor()
    
        for meteor in Meteor_list:
            meteor.move()

        for player in Player_list:
            if player.lives > 0:
                player.move()
                player.collision()
        
        gamedata.update_state()
        
        sleeptime = (1 / TICKS_SEC) - (time.time() - start_loop_time) - 0.0005
        if sleeptime > 0: 
            time.sleep(sleeptime)
        
print("[STARTING] server is starting...")
start()


