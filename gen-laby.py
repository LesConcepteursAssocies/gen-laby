#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Générateur de labyrinthe
#
# 01/2018 PG (pguillaumaud@april.org)
# (inspire de https://fr.wikipedia.org/wiki/Mod%C3%A9lisation_math%C3%A9matique_d'un_labyrinthe)
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
#
import sys, os
import time
import pickle
import random
import tkinter as TK
import tkinter.messagebox as TKM
import tkinter.filedialog as TKF
import tkinter.colorchooser as TKC

# --------------------------------------------------------------------------------
# on ajuste la pile de récursion
sys.setrecursionlimit(100000)

# Valeurs par defaut du canvas
screenWidth, screenHeight = (1024, 864)
# Taille des cases
c_sz = 8

# nombre de lignes/colonnes
maxli = int(screenHeight/c_sz)
maxco = int(screenWidth/c_sz)

# les vecteurs de direction
vDir = { "Down": (0, +1), "Up": (0, -1), "Left": (-1, 0), "Right": (+1, 0) }

# couleur du chemin (blanc par défaut)
path_color = "#ffffff"

# Le labyrinthe, initialisé avec des murs
Maze = []

# case de départ
start_cell = (random.randrange(maxco), random.randrange(maxli))
# case de fin, pour les recherches de solution
end_cell   = None

# le nom du programme (sans l'extension)
name_app = os.path.splitext(os.path.basename(sys.argv[0]))[0]
# le répertoire
path_app = os.path.dirname(sys.argv[0])

# --------------------------------------------------------------------------------
# Fin du programme
def OnExit():
    fen.destroy()

# --------------------------------------------------------------------------------
# RaZ du labyrinthe
def RazMaze():
    global Maze

    Maze = []
    Maze = [[False for l in range(maxli)] for c in range(maxco)]

# --------------------------------------------------------------------------------
# Met la case de fin aux coordonnées cliquées
def SetEndCell(event):
    global end_cell

    x = event.x - (event.x%c_sz)
    y = event.y - (event.y%c_sz)
    c = int(x/c_sz)
    l = int(y/c_sz)
    if Maze[c][l]:
        # pas un mur
        end_cell = (c, l)
        DrawCell(end_cell, 'green')

# --------------------------------------------------------------------------------
# affichage de la case donnée
def DrawCell(c, ccolor=path_color):
    x = c[0]*c_sz
    y = c[1]*c_sz
    canvas.create_rectangle(x, y, x+c_sz, y+c_sz, fill=ccolor, outline=ccolor)
    # on raffraichis l'écran
    fen.update()
    fen.update_idletasks()

# --------------------------------------------------------------------------------
# Renvoi la liste des voisins non visités de la case donnée
def FindNeighbors(c):
    neigh = []

    for d,vd in vDir.items():
        x, y = c
        x += vd[0]
        y += vd[1]
        if (0 <= x < maxco) and (0 <= y < maxli):
            if not Maze[x][y]:
                # un mur, on regarde si le voisin est libre
                xv, yv = (x,y)
                xv += vd[0]
                yv += vd[1]
                if (0 <= xv < maxco) and (0 <= yv < maxli):
                    if not Maze[xv][yv]:
                        # le voisin est libre, on l'ajoute, avec le mur a ouvrir
                        neigh.append(((x, y), (xv, yv)))
    return neigh

# --------------------------------------------------------------------------------
# DFS: Dijkstra Find Shortest
# recherche du plus court chemin
def DFS(curr_path):
    c, l = curr_path[-1]
    if (c,l) == end_cell:
        return True

    # on essaye dans toutes les directions
    for d,vd in vDir.items():
        cv, lv = (c,l)
        cv += vd[0]
        lv += vd[1]
        if (0 <= cv < maxco) and (0 <= lv < maxli) and ((cv,lv) not in curr_path):
            # pas encore vu
            if Maze[cv][lv]:
                # pas un mur, on ajoute au chemin
                curr_path.append((cv,lv))
                # appel récursif
                if DFS(curr_path):
                    return True
                else:
                    # backtrack
                    curr_path.pop()

    return False

# --------------------------------------------------------------------------------
# Recherche par DFS
def ResolveByDFS():
    if end_cell is not None:
        info.configure(text = "Recherche DFS en cours...")
        # on part avec la case de départ
        result = [start_cell]
        if DFS(result):
            info.configure(text = "Chemin trouvé")
            # on affiche le chemin
            for cpath in result:
                DrawCell(cpath, 'yellow')
            DrawCell(start_cell, 'red')
            DrawCell(end_cell, 'green')
        else:
            info.configure(text = "Pas de chemin!!")

# --------------------------------------------------------------------------------
# Génération / affichage
# Exploration exhaustive, on explore tous les chemins
def Gen():
    global Maze

    canvas.delete(TK.ALL)
    # la pile
    pc = []
    # on part de la case de départ
    pc.append(start_cell)

    info.configure(text = "Génération en cours...")

    while True:
        curr_c = pc.pop()
        DrawCell(curr_c)
        # la case courante est visitée
        Maze[curr_c[0]][curr_c[1]] = True
        # on empile la case courante
        pc.append(curr_c)
        v = FindNeighbors(curr_c)
        if len(v) > 0:
            idx = random.randrange(len(v))
            m, vo = v.pop(idx)
            # on ouvre le mur
            Maze[m[0]][m[1]] = True
            DrawCell(m)
            # on empile le voisin pour la suite
            pc.append(vo)
        else:
            # plus de voisin à explorer pour cette case, on la dépile
            curr_c = pc.pop()
            if curr_c == start_cell:
                # on est revenu au départ, c'est terminé
                break
        # suivant?
        if len(pc) <= 0:
            break
        # une petite tempo
        # time.sleep(0.05)

    info.configure(text = "Labyrinthe généré")
    # on montre la case de départ
    DrawCell(start_cell, 'red')

# --------------------------------------------------------------------------------
# le reset
def Reset():
    global start_cell, end_cell

    canvas.delete(TK.ALL)
    RazMaze()
    start_cell = (random.randrange(maxco), random.randrange(maxli))
    end_cell   = None

# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # la fenêtre et le reste
    fen = TK.Tk()
    fen.title("Générateur de labyrinthes ({0}x{1} - {2}x{3})".format(screenWidth, screenHeight, maxco, maxli))
    fen.protocol("WM_DELETE_WINDOW",OnExit)
    fen.resizable(False, False)

    canvas = TK.Canvas(fen, width = screenWidth, height = screenHeight, bg ='black')
    # les clic souris sur la grille
    canvas.bind("<Button-1>", SetEndCell)
    canvas.grid(row = 0, column = 1, rowspan = 8, columnspan = 2, pady = 5)

    # les bouttons
    # avec icones
    wb = 90
    img_start = TK.PhotoImage(file = 'icons/media-playback-start.png')
    b1 = TK.Button(fen, text ='Générer', image = img_start, compound="left", width = wb, command = Gen)

    img_mpf = TK.PhotoImage(file = 'icons/maze-pathfinder.png')
    b2 = TK.Button(fen, text ='DFS', image = img_mpf, compound="left", width = wb, command = ResolveByDFS)

    img_raz = TK.PhotoImage(file = 'icons/draw-eraser.png')
    b5 = TK.Button(fen, text ='RàZ', image = img_raz, compound="left", width = wb, command = Reset)

    b1.grid(row = 0, column = 0)
    b2.grid(row = 1, column = 0)
    b5.grid(row = 4, column = 0)

    img_quit = TK.PhotoImage(file = 'icons/system-log-out.png')
    bQ = TK.Button(fen, text ='Quitter', image = img_quit, compound="left", width = wb, command = OnExit)
    bQ.grid(row = 7, column = 0)

    # pour les infos
    info = TK.Label(fen, anchor = TK.W, justify = TK.LEFT)
    info.configure(text = "")
    info.grid(row = 8, column = 1, sticky = "W")

    RazMaze()

    fen.mainloop()
# eof
