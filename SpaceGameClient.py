import socket
import pygame
import pickle
import random

###Server
#Constants
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = input("Enter IP adress of the server you want to connect to (local or public):")
ADDR = (SERVER, PORT)

#Create client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

###Game
pygame.init()

#Constants
WIDTH, HEIGHT = 500, 800
BACKGROUND = (20, 20, 40)
TIME_FONT = pygame.font.SysFont("Arial", 40, True, False)
Hit_shade = 0
HIT_EFFECT = 80
HIT_SHADE_DECREASE = 50

#Game settings
TICKS_SEC = 60

lives_list = list()
effect_list = list()

###Functions        
def sendKeys():
    #The keypresses will be send as string, up-down-left-right
    #1 = key is pressed, 0 = key is not pressed, 1001 means up and right are pressed
    msg = ""
    for key in moveKeys:
        if keys[key]:
            msg = msg + "1 "
        else:
            msg = msg + "0 "

    client.send(msg.encode(FORMAT))

def recvGameData():
    return pickle.loads(client.recv(2048))

def drawFrame(gamedata):
    global lives_list, Hit_shade
    new_lives_list = list()
    
    if Hit_shade > 0:
        screen.fill((int(BACKGROUND[0] + Hit_shade), int(BACKGROUND[1] + Hit_shade), int(BACKGROUND[2] + Hit_shade)))
        Hit_shade = Hit_shade - ((1 / TICKS_SEC) * HIT_SHADE_DECREASE)
    else:
        Hit_shade = 0
        screen.fill(BACKGROUND)

    for meteor_tuple in gamedata.meteorData: #size, position, colour
        pygame.draw.circle(screen, meteor_tuple[2], meteor_tuple[1], meteor_tuple[0], 0)

    for player_tuple in gamedata.playerData: #lives, size, position, colour
        new_lives_list.append(player_tuple[0])

        if player_tuple[0] > 0:
            size, x, y = player_tuple[1], player_tuple[2][0], player_tuple[2][1]
            points = ((x, y - (size / 1.2)), (x - (size / 2), y + (size / 3)), (x, y), (x + (size / 2), y + (size / 3)))
            pygame.draw.polygon(screen, player_tuple[3], points)

    for i, lives in enumerate(new_lives_list):
        pygame.draw.rect(screen, gamedata.playerData[i][3], ((10, 10 + 15 * i),(20*lives, 10)))
        if lives_list:
            if lives < lives_list[i]:
                if lives == 0:
                    effect_list.append(Circle_effect((gamedata.playerData[i][2][0], gamedata.playerData[i][2][1]), HEIGHT + 100, 0.6, gamedata.playerData[i][3], 30, False, 1.7))
                else:
                    if i == client_id:
                        Hit_shade = Hit_shade + HIT_EFFECT
                    else:
                        effect_list.append(Circle_effect((gamedata.playerData[i][2][0] + random.randint(-20, 20), gamedata.playerData[i][2][1] + random.randint(-25, 0)), 30, 0.2, gamedata.playerData[i][3], 10, True, 0))

    for i in range(len(effect_list) -1, -1, -1):
        if effect_list[i].internalTime > effect_list[i].duration:
            del effect_list[i]
        else:
            effect_list[i].draw()
    
    lives_list = new_lives_list.copy()
                
            
        
    time_text = TIME_FONT.render(str(gamedata.time), 1, (250, 250, 250))
    time_text_rect = time_text.get_rect()
    time_text_rect.topright = (WIDTH - 10, 10)
    screen.blit(time_text, time_text_rect)
    
    pygame.display.flip()
    
###Classes
class Circle_effect():
    def __init__(self, pos, max_size, duration, colour, thickness, thickness_change=False, white_space=0):
        self.pos = pos
        self.max_size = max_size
        self.duration = duration * TICKS_SEC
        self.internalTime = 1
        self.colour = colour
        self.thickness = thickness
        self.thickness_change = thickness_change        
        self.white_space = white_space
        
    def draw(self):
        if self.thickness_change:
            thick = int(self.thickness - (self.thickness - 1) * self.internalTime/self.duration)
        else:
            thick = self.thickness
        pygame.draw.circle(screen, self.colour, self.pos, self.max_size * self.internalTime/self.duration, thick)
        if self.white_space > 0:
            pygame.draw.circle(screen, (255,255,255), self.pos, self.max_size * self.internalTime/self.duration - thick, int(thick*self.white_space))
        self.internalTime = self.internalTime + 1
            
        
class GameState():
    def __init__(self):
        self.playerData = [None for _ in range(clientCount)]
        self.meteorData = list()
        self.time = 0
        
    def update_state(self):
        for i, player in enumerate(Player_list):
            self.playerData[i] = (player.lives, player.size, (player.x, player.y), player.colour)
        self.meteorData.clear()
        for meteor in Meteor_list:
            self.meteorData.append((meteor.size, (meteor.x, meteor.y), meteor.colour))
        self.time = int(Time)
        
###Main
#Setup
client_id = int(client.recv(32).decode(FORMAT))

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

moveKeys = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]

while True:
    clock.tick(TICKS_SEC)
    pygame.event.pump()
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            client.send(DISCONNECT_MESSAGE.encode(FORMAT))
            pygame.quit()
            exit()
    
    sendKeys()
    gamedata = recvGameData()
    drawFrame(gamedata)



