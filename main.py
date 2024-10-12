import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center

pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)    #loading imaged
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.7)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.7)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_image(pygame.image.load("imgs/finish.png"), 0.7)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (100, 200)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.45)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.45)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height() #Getting window heightas much as image
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = [(117, 73), (117, 73), (117, 73), (117, 73), (40, 93), (40, 93), (38, 336), (229, 565), (229, 565), (316, 516), (316, 403), (316, 403), (316, 403), (316, 403), (316, 403), (316, 403), (410, 369), (410, 369), (410, 369), (410, 369), (410, 369), (410, 369), (410, 369), (466, 433), (466, 433), (478, 544), (478, 544), (478, 544), (543, 555), (543, 555), (576, 481), (576, 481), (576, 481), (573, 321), (573, 321), (523, 280), (523, 280), (523, 280), (422, 277), (422, 277), (321, 271), (321, 271), (321, 271), (321, 271), (332, 212), (332, 212), (332, 212), (452, 200), (452, 200), (452, 200), (452, 200), (558, 183), (558, 183), (558, 83), (558, 83), (446, 62), (241, 60), (214, 188), (214, 188), (208, 274), (208, 274), (208, 274), (208, 274), (173, 315), (140, 260), (140, 260), (140, 260), (143, 205), 
(143, 205), (143, 205)]

class GameInfo:
    LEVELS = 5

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS
    
    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return  round(time.time() - self.level_start_time)
    

class AbstractCar: #car fuctions
    IMG = RED_CAR

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel =rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.accelaration = 1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.accelaration, self.max_vel)
        self.move()

    def move_backword(self):
        self.vel = max(self.vel - self.accelaration, -self.max_vel/2)
        self.move()


    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x  -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0 


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (140, 150)

    def reduce_speed(self):
        self.vel = max(self.vel - self.accelaration / 0.1, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (115, 150)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)  #displays path points on display

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0



def draw(win, images, player_car, computer_car, game_info):    #function for drawing images on windows
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(f"level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))


    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backword()

    if not moved:
        player_car.reduce_speed()


def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        blit_text_center(WIN, MAIN_FONT,"You Lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()


    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)



run = True
clock = pygame.time.Clock() #getting clock
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(2, 6, PATH)
game_info = GameInfo()

while run: #Running the window loop
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()
                                
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        # if event.type == pygame.MOUSEBUTTONDOWN:  #taking the path location
        #     pos = pygame.mouse.get_pos()
        #     computer_car.path.append(pos)


    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT,"You Won!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

# print(computer_car.path)   prints the path
pygame.quit()