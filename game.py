from email import message_from_string
from email.mime import message
from fnmatch import translate
from operator import truediv
from tkinter import CENTER
import pygame
import random

"""
10 x 20 square grid
fichas: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per blo ck
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height


# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

fichas = [S, Z, I, O, J, L, T]
colores_de_fichas = [(204, 0, 102), (255, 0, 0), (51, 0, 153 ), (255, 255, 0), (102, 255, 0 ), (0, 0, 255), (0, 204, 204)]
# index 0 - 6 represent shape


class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = colores_de_fichas[fichas.index(shape)]
        self.rotation = 0  # number from 0-3


def crear_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid


def convertir_formato_de_forma(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def validar_espacio(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convertir_formato_de_forma(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def chequeo_perdio(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    global fichas, colores_de_fichas

    return Piece(5, 0, random.choice(fichas))


def dibujar_texto_medio(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    font2 = pygame.font.SysFont('Verdana', 30, bold=True)
    label = font.render(text, 1, color)
    text2="Presione p para pausar y c para continuar"
    label2=font2.render(text2,1,(255, 195, 0))
    fondo=pygame.image.load("imagenes/img2.jpg").convert()
    fondo=pygame.transform.scale(fondo,(800,700))
    surface.blit(fondo,[0,0])
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))
    surface.blit(label2,(top_left_x + play_width/2 - (label.get_width() /2.1), top_left_y + play_height/4 - label.get_height()/2))

def dibujar_cuadrícula(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
        for j in range(col):
            pygame.draw.line(surface, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines


def borrar_filas(grid, locked):
    # necesita ver si la fila está despejada, el cambio cada dos filas arriba hacia abajo

    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            # agregar posiciones para eliminar de bloqueado
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)


def dibujar_siguiente_forma(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Siguiente',3,(250,250,250))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy- 30))

def pausa(ventana):
    negro=(0,0,0)
    reloj=pygame.time.Clock()
    pausado=True
    while pausado:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type ==pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    pausado= False     
                    pygame.init()
                    sonido= pygame.mixer.Sound("sonidos/pausar.mp3")
                    sonido.play()
                    pygame.mixer.music.play()
                elif event.key ==pygame.K_d:
                    pygame.quit()
                    quit() 
        ventana.fill((0,0,0))  
        dibujar_texto_medio2("Presione p para pausar y c para continuar", 30, (241, 79, 22), ventana)
        pygame.display.update()
        reloj.tick(5)
   
def dibujar_texto_medio2(text, size, color, ventana):
    ventana.fill((0,0,0))  
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    letra30 = pygame.font.SysFont("Arial", 30)
    imagenTextoPresent = letra30.render("PAUSADO",
    True, (200,200,200), (0,0,0) )
    ventana.blit(imagenTextoPresent,(350,290))
    ventana.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))
    





def dibujar_ventana(surface):
    
    fondo=pygame.image.load("imagenes/img5.jpg").convert()
    fondo=pygame.transform.scale(fondo,(800,700))
    surface.blit(fondo,[0,0])
   
    # Tetris Titulo
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255,255,255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)

    # dibujar cuadrícula y borde
    dibujar_cuadrícula(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    # pygame.display.update()


def main():
    global grid

    locked_positions = {}  # (x,y):(255,0,0)
    grid = crear_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
   
    
    while run:

       

        fall_speed = 0.27

        grid = crear_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # PIECE FALLING CODE
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (validar_espacio(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not validar_espacio(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not validar_espacio(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    # rotar la forma
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not validar_espacio(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    # mover la forma hacia abajo
                    current_piece.y += 1
                    if not validar_espacio(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_SPACE:
                    while validar_espacio(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    print(convertir_formato_de_forma(current_piece))  

                if event.key == pygame.K_p:
                    sonido= pygame.mixer.Sound("sonidos/despausar.mp3")
                    sonido.play()
                    pygame.mixer.music.stop()
                    pausa(ventana)      
                    
                    
        shape_pos = convertir_formato_de_forma(current_piece)

        # agregar pieza a la cuadrícula para dibujar
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        #SI LA PIEZA TOCA EL SUELO
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # llama cuatro veces para comprobar si hay varias filas despejadas
            borrar_filas(grid, locked_positions)

        dibujar_ventana(ventana)
        dibujar_siguiente_forma(next_piece, ventana)
        pygame.display.update()

        # Compruebe si la usuario perdió
        if chequeo_perdio(locked_positions):
            run = False

    dibujar_texto_medio("Game Over papu", 40, (255,255,255), ventana)
    pygame.display.update()
    pygame.time.delay(2000)


def menu_principal():
    run = True

    while run:
        pygame.mixer.init()
        pygame.mixer.music.load('sonidos/CancionTetris.mp3')
        pygame.mixer.music.play(-1)
        ventana.fill((0,0,0))
        dibujar_texto_medio('Presiona cualquier tecla para jugar.', 42, (113, 125, 126), ventana)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


ventana = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

menu_principal()  # start game