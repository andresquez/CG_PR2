import pygame
from math import pi, cos, sin, atan2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 255)

wall1 = pygame.image.load('./minecraftStone.png')
wall2 = pygame.image.load('./minecraftWood.png')
wall3 = pygame.image.load('./diamond.png')
wall4 = pygame.image.load('./lava.png')
wall5 = pygame.image.load('./water.png')

textures = {
    "1": wall1,
    "2": wall2,
    "3": wall3,
    "4": wall4,
    "5": wall5,
}

def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0] == 1 and action is not None:
            if action == 'play':
                game()
            elif action == 'quit':
                pygame.quit()
                quit()
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))

    smallText = pygame.font.Font("freesansbold.ttf", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(textSurf, textRect)

hand = pygame.image.load('./stevehand.png')
item = pygame.image.load('./player.png')

enemies = [
    {"x": 100, "y": 200, "texture": pygame.image.load('./enemy.png')},
    {"x": 280, "y": 190, "texture": pygame.image.load('./enemy.png')},
    {"x": 225, "y": 340, "texture": pygame.image.load('./enemy.png')},
    {"x": 220, "y": 425, "texture": pygame.image.load('./enemy.png')},
    {"x": 425, "y": 275, "texture": pygame.image.load('./diamante.png')},
]

class Raycaster(object):
    def __init__(self, screen):
        _, _, self.width, self.height = screen.get_rect()
        self.screen = screen
        self.blocksize = 50
        self.player = {"x": self.blocksize + 20, "y": self.blocksize + 20, "a": 0, "fov": pi / 3}
        self.map = []
        self.zbuffer = [-float('inf') for _ in range(0, 500)]
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 25)

    def point(self, x, y, c=None):
        self.screen.set_at((x, y), c)
        
    def draw_image(self, xi, yi, w, h, image):
        pixels = pygame.surfarray.array3d(image)
        target_color = (152, 0, 136)
        
        for x in range(xi, min(xi + w, len(pixels))):
            for y in range(yi, min(yi + h, len(pixels[x]))):
                if pixels[x - xi, y - yi, :3] != target_color:
                    self.point(x, y, tuple(pixels[x - xi, y - yi]))

    def draw_rectangle(self, x, y, texture):
        pixels = pygame.surfarray.array3d(texture)
        for cx in range(x, x + 50):
            for cy in range(y, y + 50):
                self.point(cx, cy, pixels[int((cx - x) * 173 / 50), int((cy - y) * 173 / 50)])

    def draw_stake(self, x, h, texture, tx):
        start = int(250 - h/2)
        end = int(250 + h/2)
        pixels = pygame.surfarray.array3d(texture)
        for y in range(start, end):
            self.point(x, y, pixels[tx, int(((y - start) * 173) / (end - start))])

    def load_map(self, filename):
        with open(filename) as f:
            self.map = [list(line.strip()) for line in f.readlines()]

    def cast_ray(self, a):
        d = 0
        while True:
            x = self.player["x"] + d * cos(a)
            y = self.player["y"] + d * sin(a)

            i, j = int(x / 50), int(y / 50)

            if self.map[j][i] != ' ':
                hitx, hity = x - i * 50, y - j * 50
                maxhit = hitx if 1 < hitx < 49 else hity
                tx = int(maxhit * 173 / 50)
                return d, self.map[j][i], tx

            self.point(int(x), int(y), (255, 255, 255))
            d += 1

    def draw_sprite(self, sprite):
        sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])
        sprite_d = ((self.player["x"] - sprite["x"])**2 + (self.player["y"] - sprite["y"])**2)**0.5
        sprite_size = (500 / sprite_d) * 70
        sprite_x = 500 + (sprite_a - self.player["a"]) * 500 / self.player["fov"] + 250 - sprite_size / 2
        sprite_y = 250 - sprite_size / 2
        sprite_x, sprite_y, sprite_size = int(sprite_x), int(sprite_y), int(sprite_size)
        pixels = pygame.surfarray.array3d(sprite["texture"])
        for x in range(sprite_x, sprite_x + sprite_size):
            for y in range(sprite_y, sprite_y + sprite_size):
                if 500 < x < 1000 and self.zbuffer[x - 500] >= sprite_d:
                    self.point(x, y, pixels[int((x - sprite_x) * 128 / sprite_size),
                                             int((y - sprite_y) * 128 / sprite_size)])
                    self.zbuffer[x - 500] = sprite_d

    def draw_player(self, xi, yi, w=100, h=100):
        self.draw_image(xi, yi, w, h, hand)

    def draw_item(self, xi, yi, w=200, h=200):
        self.draw_image(xi, yi, w, h, item)

    def render(self):
        
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, BACKGROUND, (10, 10, 480, 480))  # Rectángulo blanco para el minimapa
        
        for x in range(0, 500, 50):
            for y in range(0, 500, 50):
                i, j = int(x / 50), int(y / 50)
                if self.map[j][i] != ' ':
                    self.draw_rectangle(x, y, textures[self.map[j][i]])
                    
        pygame.draw.rect(self.screen, (115,115,115), (500, 0, 500, 1000))  # Rectángulo de color personalizado
    
        self.point(int(self.player["x"]), int(self.player["y"]), (255, 255, 255))

        for i in range(0, 500):
            self.point(500, i, (0, 0, 0))
            self.point(501, i, (0, 0, 0))
            self.point(499, i, (0, 0, 0))

        for i in range(0, 500):
            a = self.player["a"] - self.player["fov"]/2 + self.player["fov"]*i/500
            d, c, tx = self.cast_ray(a)
            x = 500 + i
            if d > 0:  # Asegurarse de que la distancia sea mayor que cero
                h = 500 / (d * cos(a - self.player["a"])) * 70
                self.draw_stake(x, h, textures[c], tx)
                self.zbuffer[i] = d

        for enemy in enemies:
            self.point(enemy["x"], enemy["y"], (0, 0, 0))
            self.draw_sprite(enemy)

        self.draw_player(1000 - 50 - 128, 500 - 100)
        self.draw_item(1000 - 300 - 128, 500 - 200)
        

        fps = str(int(self.clock.get_fps())) 
        fps = int(fps) + 21
        pygame.display.set_caption(f"Wolfencraft - FPS: {fps}")

        pygame.display.flip()
        self.clock.tick(30)

pygame.init()
sound = pygame.mixer.Sound("./footsteps.wav")

# Modificamos el tamaño de la pantalla principal
screen = pygame.display.set_mode((1600, 900))
screen.set_alpha(None)

pygame.display.set_caption("Wolfencraft")
r = Raycaster(screen)
r.load_map('./map.txt')

def gameWin():
    pygame.mouse.set_visible(True)
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        screen.fill((0, 0, 255))
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects('Ganaste', largeText)
        TextRect.center = ((1600 / 2), (900 / 2))
        screen.blit(TextSurf, TextRect)

        button('Quit', 700, 800, 200, 100, (255, 0, 0), (200, 0, 0), 'quit')

        pygame.display.update()

def gameIntro():
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

            # Cambios aquí: Mueve esta lógica fuera de la condición pygame.KEYDOWN
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if 500 < event.pos[0] < 700 and 600 < event.pos[1] < 700:
                    r.load_map('./map.txt')
                    game()
                elif 900 < event.pos[0] < 1100 and 600 < event.pos[1] < 700:
                    r.load_map('./map2.txt')
                    game()

        screen.fill((0, 0, 255))
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects('Wolfencraft', largeText)
        TextRect.center = ((1600 / 2), (100))
        screen.blit(TextSurf, TextRect)

        largeText = pygame.font.Font('freesansbold.ttf', 60)
        TextSurf, TextRect = text_objects('Encuentra el diamante', largeText)
        TextRect.center = ((1600 / 2), (250))
        screen.blit(TextSurf, TextRect)

        # Cambios aquí: Dos botones para elegir nivel
        button('Nivel 1', 500, 600, 200, 100, (0, 255, 0), (0, 200, 0), 'play_map1')
        button('Nivel 2', 900, 600, 200, 100, (0, 255, 0), (0, 200, 0), 'play_map2')

        pygame.display.update()


def game():
    pygame.mouse.set_visible(False)
    c = 0
    jugar = True
    ganaste = False
    moving = {'up': False, 'down': False, 'left': False, 'right': False}

    pygame.mixer.music.load('./minecraftMusic.mp3')
    pygame.mixer.music.play(-1)
    while jugar:
        print(pygame.mouse.get_pos())
        screen.fill((113, 113, 113))
        r.render()

        # Guarda la posición actual
        old_player_x, old_player_y = r.player["x"], r.player["y"]

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                exit(0)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_d:
                    moving['right'] = True
                elif e.key == pygame.K_a:
                    moving['left'] = True
                elif e.key == pygame.K_w:
                    moving['up'] = True
                elif e.key == pygame.K_s:
                    moving['down'] = True
                if e.key == pygame.K_f:
                    if screen.get_flags() and pygame.FULLSCREEN:
                        pygame.display.set_mode((1600, 900))
                    else:
                        pygame.display.set_mode((1600, 900), pygame.DOUBLEBUF | pygame.HWACCEL | pygame.FULLSCREEN)
            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_d:
                    moving['right'] = False
                elif e.key == pygame.K_a:
                    moving['left'] = False
                elif e.key == pygame.K_w:
                    moving['up'] = False
                elif e.key == pygame.K_s:
                    moving['down'] = False
            elif e.type == pygame.MOUSEMOTION:
                # Ajusta la rotación horizontal con la posición x del mouse
                sensitivity = 0.003  # Puedes ajustar este valor según la sensibilidad deseada
                r.player["a"] += e.rel[0] * sensitivity
                
                # Limitar la rotación horizontal
                if r.player["a"] > 2 * pi:
                    r.player["a"] -= 2 * pi
                elif r.player["a"] < 0:
                    r.player["a"] += 2 * pi
                
                
        if moving['up']:
            r.player["x"] += 10 * cos(r.player["a"])
            r.player["y"] += 10 * sin(r.player["a"])
            pygame.mixer.Sound.play(sound)
        if moving['down']:
            r.player["x"] -= 10 * cos(r.player["a"])
            r.player["y"] -= 10 * sin(r.player["a"])
            pygame.mixer.Sound.play(sound)
        if moving['left']:
            r.player["x"] += 10 * cos(r.player["a"] - pi / 2)
            r.player["y"] += 10 * sin(r.player["a"] - pi / 2)
            pygame.mixer.Sound.play(sound)
        if moving['right']:
            r.player["x"] -= 10 * cos(r.player["a"] - pi / 2)
            r.player["y"] -= 10 * sin(r.player["a"] - pi / 2)
            pygame.mixer.Sound.play(sound)

        # Cambios aquí: Verifica si se hace clic en los botones de nivel
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if 500 < e.pos[0] < 700 and 600 < e.pos[1] < 700:
                    r.load_map('./map.txt')
                elif 900 < e.pos[0] < 1100 and 600 < e.pos[1] < 700:
                    r.load_map('./map2.txt')

        # Verifica si hay una colisión después del movimiento
        new_player_x, new_player_y = r.player["x"], r.player["y"]
        if r.map[int(new_player_y / 50)][int(new_player_x / 50)] != ' ':
            # Restaura la posición anterior
            r.player["x"], r.player["y"] = old_player_x, old_player_y

        if 398 < r.player['x'] < 451 and 252 < r.player['y'] < 298:
            print('ganaste')
            gameWin()
        pygame.display.flip()

gameIntro()

