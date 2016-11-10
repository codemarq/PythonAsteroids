# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
rock_group = set([])
missile_group = set([])
explostion_group = set([])

ship_thrust_image = (135, 45)
ship_no_thrust_image = (45, 45)
friction_constant = 0.99
missile_accel_constant = 5


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_brown.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_brown.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot1.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated asteroid
asteroid_anim_info = ImageInfo([64, 64], [128, 128], 64, True)
asteroid_anim_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/asteroid1.opengameart.warspawn.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
 
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# helper functions for processing sets of sprites
def process_sprite_group(sprite_group, canvas):
    sprites = set(sprite_group)
    for each_sprite in sprites:
        each_sprite.update()
        each_sprite.draw(canvas)
        if each_sprite.update() == True:
            sprite_group.remove(each_sprite)

#helper function for group collisions with single object (ship with rock)
def group_collide(set_group, other_object):
    group = set(set_group)
    for each_sprite in group:
        if Sprite.collide(each_sprite, other_object) == True:
            rock_group.discard(each_sprite)
            missile_group.discard(each_sprite)
            return True
        
# helper function for collisions between sprite sets (missile to rock)
def group_group_collide(set_group1, set_group2):
    group1 = set(set_group1)
    group2 = set(set_group2)
    num_collisions = 0
    for each_sprite1 in group1:
        if group_collide(group2, each_sprite1) == True:
            num_collisions +=1
            set_group1.discard(each_sprite1)
            return num_collisions

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def thrusters_on(self, thrust):
        self.thrust = thrust
        if self.thrust == True:
            self.image_center = ship_thrust_image    
            ship_thrust_sound.play()
        else:
            self.thrust = False
            self.image_center = ship_no_thrust_image
            ship_thrust_sound.rewind()
        
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, 
                          self.pos, self.image_size, self.angle)

    def update(self):
        # orientation update
        self.angle += self.angle_vel
        
        # position update
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # thrust update
        forward = angle_to_vector(self.angle)
        if self.thrust == True:
            self.vel[0] += forward[0] * 0.1
            self.vel[1] += forward[1] * 0.1
        
        self.vel[0] *= friction_constant
        self.vel[1] *= friction_constant

    def turn_right(self):
        self.angle_vel += 0.05 
        
    def turn_left(self):
        self.angle_vel -= 0.05
    
    def stop_turn(self):
        self.angle_vel = 0
    
    def shoot(self):
        global missile_group
        forward = angle_to_vector(self.angle)
        c = missile_accel_constant
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + c * forward[0], self.vel[1] + c * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, self.angle_vel, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)       
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def collide(self, other_object):
        if dist(self.pos, other_object.pos) <= (self.radius + other_object.radius - 3):
            return True
        else:
            return False
    
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, 
                          self.pos, self.image_size, self.angle)
        
    def update(self):
        # rotation update
        self.angle += self.angle_vel
        
        # position update
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # sprite age update
        self.age += 1
        if self.age < self.lifespan:
            return False
        else:
            return True
        
        
# Draw Handler                    
def draw(canvas):
    global time, started, lives, score, rock_group
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    soundtrack.play()
    
    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
         
    # update ship and sprites
    my_ship.update()

    # Collisions
    if group_collide(rock_group, my_ship) == True:
        lives -= 1
    if group_group_collide(rock_group, missile_group):
        score += 1
          
    # Draw Score and lives remaining
    canvas.draw_text("Lives", [50, 50], 25, "white")
    canvas.draw_text(str(lives), [50, 75], 25, "white")
    canvas.draw_text("Score", [WIDTH - 100, 50], 25, "white")
    canvas.draw_text(str(score), [WIDTH - 100, 75], 25, "white")

    # game restart conditions
    if lives == 0:
        started = False
        soundtrack.rewind()
        
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        score = 0
        lives = 3
        rock_group = set([])
    
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, started, score
    rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    rock_vel = [random.random() * .6 - .3 * (score * 0.1), random.random() * .6 - .3 * (score * 0.1)]
    rock_angle_vel = random.random() * .2 - .1
    if (len(rock_group) < 12) and (started == True) and dist(rock_pos, my_ship.pos) > (my_ship.radius * 3):
        a_rock = Sprite(rock_pos, rock_vel, 0, rock_angle_vel, asteroid_image, asteroid_info)
        rock_group.add(a_rock)

    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# key handlers
def thrust_on():
    my_ship.thrusters_on(True)
def thrust_off():
    my_ship.thrusters_on(False)    
keydowns = {"up": thrust_on, "left": my_ship.turn_left, "right": my_ship.turn_right, "space": my_ship.shoot}
keyups = {"up": thrust_off, "left": my_ship.stop_turn, "right": my_ship.stop_turn}

def keydown(key):
    for k in keydowns:
        if key == simplegui.KEY_MAP[k]:
            keydowns[k]()
    
def keyup(key):
    # insert keyup code here
    for k in keyups:
        if key == simplegui.KEY_MAP[k]:
            keyups[k]()

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
                        
           
# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()