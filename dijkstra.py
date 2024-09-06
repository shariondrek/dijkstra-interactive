import pygame
import sys
import heapq


# Author: shariondrek
# Date: 06-july-2023

# Left Mouse = Draw
# Right Mouse = Eraser
# Numbers 1-3 = Color Selection
# 1 = Black(obstacles)
# 2 = Green(Starting point)
# 3 = Red(Ending point)

# "ENTER" = Run Algorithm

MAX = sys.maxsize
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
RECT_SIZE = 10
FPS = 999
COR_DEFAULT = (200,200,200) 
COR_OBSTACULO = (0,0,0) 
COR_DESTINO = (255,0,0) 
COR_INICIO = (0,255,0) 
COR_BORRACHA = (150,150,150) 
COR_HEAP = (230,230,0) 
COR_VISITADO = (170,170,200)


class Quadrado:
    def __init__(self, posx, posy, color):
        self.posx = posx
        self.posy = posy
        self.color = color
        self.rect = pygame.Rect(self.posx, self.posy, RECT_SIZE, RECT_SIZE)
        self.distancia = MAX
        self.visitado = False
        self.anterior = None
        self.adjacentes = []

    def __lt__(self, other):
        return self.distancia < other.distancia


class Grid:
    def __init__(self):
        self.matriz = []
        self.need_update = []
        self.need_draw = []
        self.inicio = None
        self.destino = None
        self.len_row = int(SCREEN_WIDTH/RECT_SIZE)
        self.len_col = int(SCREEN_HEIGHT/RECT_SIZE)
        self.__iniciar_matriz()
        self.dijkstra_init = False
        self.fila_prioridade = []

    def __iniciar_matriz(self):
        for i in range(self.len_col):
            row = []
            for b in range(self.len_row):
                row.append(Quadrado(b*RECT_SIZE, i*RECT_SIZE, COR_DEFAULT))
            self.matriz.append(row)

        for linha in self.matriz:
            for quadrado in linha:
                self.need_draw.append(quadrado)

    def iniciar_adjacentes(self):
        for y in range(self.len_col):
            for x in range(self.len_row):
                for i in range(2):
                    col = (x - 1) + (i * 2)
                    if col > -1 and col < self.len_row:
                        if self.matriz[y][col].color != (0,0,0):
                            self.matriz[y][x].adjacentes.append(self.matriz[y][col])
                for i in range(2):
                    row = (y - 1) + (i * 2)
                    if row > -1 and row < self.len_col:
                        if self.matriz[row][x].color != (0,0,0):
                            self.matriz[y][x].adjacentes.append(self.matriz[row][x])
        print("Adjacentes iniciados com base nas cores!")

    def update(self):
        if len(self.need_update):
            pygame.display.update(self.need_update)
            self.need_update.clear()

    def draw(self, screen):
        if len(self.need_draw):
            for i in reversed(range(len(self.need_draw))):
                pygame.draw.rect(screen, self.need_draw[i].color, self.need_draw[i].rect)
                self.need_update.append(self.need_draw[i].rect)
                self.need_draw.pop(i)

    def imprimir_caminho(self, rect):
        while rect.anterior != None:
            if rect != self.destino and rect != self.inicio:
                rect.color = (0,0,255)
                self.need_draw.append(rect)
            rect = rect.anterior

        print(f"Distancia do menor caminho encontrado = {self.destino.distancia}!")   
    
    def logic(self):
        if self.dijkstra_init:
            self.dijkstra()

    def dijkstra(self):
        if not self.dijkstra_init:
            self.iniciar_adjacentes()
            self.dijkstra_init = True
            self.inicio.distancia = 0
            for linha in self.matriz:
                for rect in linha:
                    self.fila_prioridade.append((rect.distancia, rect)) 

        heapq.heapify(self.fila_prioridade)

        atual = heapq.heappop(self.fila_prioridade)
        atual = atual[1]
        if atual.distancia == MAX:
            self.dijkstra_init = False
            print("Caminho impossivel!")
            return
        atual.visitado = True
        if atual != self.destino and atual != self.inicio:
            atual.color = COR_VISITADO
            self.need_draw.append(atual)

        for proximo in atual.adjacentes:
            if proximo.visitado:
                continue
            nova_dist = atual.distancia + 1
            if nova_dist < proximo.distancia:
                proximo.distancia = nova_dist
                if proximo != self.destino:
                    proximo.color = COR_HEAP
                    self.need_draw.append(proximo)
                proximo.anterior = atual

        if self.destino.anterior:
            self.dijkstra_init = False
            self.imprimir_caminho(self.destino)


class Ponteiro_Mouse:
    def __init__(self, grid:Grid):
        self.pode_desenhar = True
        self.grid = grid
        self.color = (0,0,0)
        self.cor_anterior = COR_DEFAULT
        self.grid_pos = (0,0)
        self.left_click = False
        self.right_click = False
        self.k1 = True
        self.k2 = False
        self.k3 = False

    def mouse_moveu(self, pos):
        if self.pode_desenhar:
            new_grid_pos = self.__transforma_pos_to_grid(pos)
            if new_grid_pos != self.grid_pos:
                if not self.left_click:
                    self.pinta_quadrado(self.grid_pos, self.cor_anterior)
                    self.cor_anterior = self.grid.matriz[new_grid_pos[1]][new_grid_pos[0]].color
                    if self.k1:
                        self.pinta_quadrado(new_grid_pos, COR_OBSTACULO)
                    elif self.k2:
                        self.pinta_quadrado(new_grid_pos, COR_INICIO)
                    elif self.k3:
                        self.pinta_quadrado(new_grid_pos, COR_DESTINO)

            self.grid_pos = new_grid_pos

            if self.left_click:
                if self.k1:
                    self.pinta_quadrado(new_grid_pos, COR_OBSTACULO)
                    self.cor_anterior = COR_OBSTACULO
                elif self.k2:
                    self.seta_inicio_fim("inicio")
                    self.pinta_quadrado(new_grid_pos, COR_INICIO)
                    self.cor_anterior = COR_INICIO

                elif self.k3:
                    self.seta_inicio_fim("destino")
                    self.pinta_quadrado(new_grid_pos, COR_DESTINO)                
                    self.cor_anterior = COR_DESTINO

            elif self.right_click:
                self.pinta_quadrado(self.grid_pos, COR_BORRACHA)
                self.cor_anterior = COR_DEFAULT        

    def mouse_btn_down(self, btn):
        if self.pode_desenhar:
            if btn == 1:
                self.left_click = True
                if self.k1:
                    self.pinta_quadrado(self.grid_pos, COR_OBSTACULO)
                    self.cor_anterior = COR_OBSTACULO
                elif self.k2:
                    self.seta_inicio_fim("inicio")
                    self.pinta_quadrado(self.grid_pos, COR_INICIO)
                    self.cor_anterior = COR_INICIO                
                elif self.k3:
                    self.seta_inicio_fim("destino")
                    self.pinta_quadrado(self.grid_pos, COR_DESTINO)
                    self.cor_anterior = COR_DESTINO                    

            if btn == 3 and not self.left_click:
                self.right_click = True
                self.pinta_quadrado(self.grid_pos, COR_BORRACHA)
                self.cor_anterior = COR_DEFAULT

    def mouse_btn_up(self, btn):
        if btn == 1:
            self.left_click = False
        if btn == 3:
            self.right_click = False

    def kb_key_down(self, key):
        if self.pode_desenhar:
            if key == "K_1":
                self.k1 = True
                self.k2 = False
                self.k3 = False
                self.pinta_quadrado(self.grid_pos, COR_OBSTACULO)
                return
            if key == "K_2":
                self.k1 = False
                self.k2 = True
                self.k3 = False
                self.pinta_quadrado(self.grid_pos, COR_INICIO)
                return
            if key == "K_3":
                self.k1 = False
                self.k2 = False
                self.k3 = True
                self.pinta_quadrado(self.grid_pos, COR_DESTINO)
                return
            if key == "K_RETURN" and not grid.dijkstra_init:
                if self.grid.destino:
                    if self.grid.inicio:
                        self.pode_desenhar = False
                        self.limpa_ponteiro()
                        self.grid.dijkstra()

    def pinta_quadrado(self, grid_pos, color):
        self.grid.matriz[grid_pos[1]][grid_pos[0]].color = color
        self.grid.need_draw.append(self.grid.matriz[grid_pos[1]][grid_pos[0]])

    def seta_inicio_fim(self, ponto):
        if ponto == "inicio":
            if self.grid.destino == self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]:
                    self.grid.destino = None

            if self.grid.inicio == None:
                self.grid.inicio = self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]
                return
            else:
                self.grid.inicio.color = COR_DEFAULT
                self.grid.need_draw.append(self.grid.inicio)
                self.grid.inicio = self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]

        elif ponto == "destino":
            if self.grid.inicio == self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]:
                self.grid.inicio = None

            if self.grid.destino == None:
                self.grid.destino = self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]
                return
            else:
                self.grid.destino.color = COR_DEFAULT
                self.grid.need_draw.append(self.grid.destino)
                self.grid.destino = self.grid.matriz[self.grid_pos[1]][self.grid_pos[0]]

    def __transforma_pos_to_grid(self,pos):
        x,y = int(pos[0]/RECT_SIZE),int(pos[1]/RECT_SIZE)
        if x < 0:
            x = 0
        if x >= self.grid.len_row:
            x = self.grid.len_row-1
        if y < 0:
            y = 0
        if y >= self.grid.len_col:
            y = self.grid.len_col-1
        return x,y
    
    def limpa_ponteiro(self):
        self.pinta_quadrado(self.grid_pos, self.cor_anterior)         
                

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test Dijkstra")
clock = pygame.time.Clock()

grid = Grid()
mouse = Ponteiro_Mouse(grid)

screen.fill((0,0,0))
pygame.display.flip()


while True:
    clock.tick(FPS)
    #print(clock.get_fps())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

        if event.type == pygame.MOUSEMOTION:
            mouse.mouse_moveu(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse.mouse_btn_down(1)
            if event.button == 3:
                mouse.mouse_btn_down(3)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse.mouse_btn_up(1)
            if event.button == 3:
                mouse.mouse_btn_up(3)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mouse.kb_key_down("K_1")
            if event.key == pygame.K_2:
                mouse.kb_key_down("K_2")
            if event.key == pygame.K_3:
                mouse.kb_key_down("K_3")

            if event.key == pygame.K_RETURN:
                mouse.kb_key_down("K_RETURN")

    ## DRAWING ##
    grid.logic()
    grid.draw(screen)
    grid.update()

