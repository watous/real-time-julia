

from math import *
from random import choice
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import sys
from sortedcontainers import SortedList
import pygame

try:
    from image_export import create_image
except ImportError:
    print("unable to import image_export")

def iteration(z, c):
    root = (z - c)**0.5
    return(root, -root)

def derivative(z):
    return 2*abs(z)

Tk().withdraw()

pygame.init()
pygame.key.set_repeat(200, 20)

#press ctrl+s to export the prisoner set of the current Julia set as a bitmap (PNG)
#click to set c, use arrows to change c by one pixel

class App:
    #!! y axis points down
    def __init__(self, width, height, scale=None,
                  c=0, #initial value of c in the equation z -> z^2+c
                  point_limit=200000, #maximum number of points drawn or -1 for unlimited, increase if Julia sets aren't drawn thoroughly enough even after the drawing stops
                  approach=30, #increase if you sometimes see points clearly out of the JS, decrease otherwise
                  center_x=0, center_y=0,
                  points_per_frame=1000, #number of points drawn at once, decrease if it lags, increase if Julia sets aren't drawn quickly enough
                  drag_point_size=1, point_size=0, #size of a point while dragging and otherwise, a single pixel will be drawn for sizes < 1
                  label_height=None, label_offset=None, label_font_size=None,
                  ):
                #parameter value of `None` means autodecide
        self.width = width
        self.height = height
        self.label_height = self.height//14 if label_height is None else label_height
        self.label_offset = self.width//30 if label_offset is None else label_offset
        self.label_font_size = min(self.label_height//2, self.width//22) if label_font_size is None else label_font_size
        self.screen = pygame.display.set_mode((self.width, self.height + self.label_height))
        self.label = self.screen.subsurface((0, 0, self.width, self.label_height))
        self.label_bg = (192,192,192)
        self.canvas = self.screen.subsurface((0, self.label_height, self.width, self.height))
        self.font = pygame.font.SysFont("consolas", self.label_font_size)
        self.scale = scale if scale is not None else min(self.width, self.height) // 4
        self.c = c
        self.num_points = 0
        self.to_draw = SortedList(key = lambda x:-x[1])
        self.point_limit = point_limit
        self.approach = approach
        self.center_x = center_x
        self.center_y = center_y
        self.points_per_frame = points_per_frame
        self.drag_point_size = int(drag_point_size)
        self.point_size = int(point_size)
        self.drag = None
        self.motion = None
        pygame.display.set_caption("Interactive Julia set generator")
        icon = pygame.image.load("icon.png")
        pygame.display.set_icon(icon)
        self.mandelbrot = pygame.image.load("mandelbrot.png") #image of mandelbrot set in the square {x+yi | max(abs(x),abs(y))<2}
        self.reset()
        
    def run(self):
        pygame.display.flip()
        while True:
            pygame.time.wait(20)
            if self.drag is not None:
                self.update_c(self.drag)
            self.drag = None
            self.motion = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    self.drag = event
                elif event.type == pygame.MOUSEMOTION:
                    self.motion = event
                elif event.type == pygame.WINDOWLEAVE:
                    self.leave(event)
                    self.motion = self.drag = None
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.update_c(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                        self.export_image()
                        pygame.event.clear()
                        break
                    elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        x,y = self.c.real, self.c.imag
                        x,y = self.to_canvas_coords(x,y)
                        dx,dy = {pygame.K_UP: (0,-1), pygame.K_DOWN: (0,1),
                                 pygame.K_LEFT: (-1,0), pygame.K_RIGHT: (1,0)}[event.key]
                        x,y = self.to_plane_coords(x+dx, y+dy, absolute=False)
                        self.c = x + y*1j
                        self.reset()
                        break
            if self.motion is not None:
                self.mousemotion(self.motion)
        
            if self.num_points < self.point_limit or self.point_limit == -1:
                for i in range(self.points_per_frame):
                    point = self.to_draw.pop()
                    self.add_point(point[0])
                    for new_z in iteration(point[0], self.c):
                        new_derivative = point[1] + log(derivative(new_z))
                        self.to_draw.add((new_z, new_derivative))
            pygame.display.flip()
                
    def export_image(self):
        print("exporting image... ", end="")
        c = self.c
        x,y = c.real, c.imag
        default_name = "prisoner_set_{:.2f}{:+.2f}i".format(x,y)
        name = asksaveasfilename(filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
                             defaultextension=".png",
                             initialfile=default_name)
        if name == "":
            print("canceled")
        else:
            img = create_image(c, iterations=100)
            img.save(name)
            print("finished")

    def to_canvas_coords(self, x,y):
        canvas_x = round(self.width / 2 + (x - self.center_x) * self.scale)
        canvas_y = round(self.height / 2 + (-y - self.center_y) * self.scale)
        return (canvas_x, canvas_y)

    def to_plane_coords(self, x,y, absolute=True):
        """absolute - whether the given coordinates are window coordinates (True)
        or canvas coordinates (False)"""
        dx = dy = 0
        if absolute:
            dx,dy = self.canvas.get_abs_offset()
        plane_x = (x - dx - self.width / 2) / self.scale + self.center_x
        plane_y = -((y - dy - self.height / 2) / self.scale + self.center_y)
        return (plane_x, plane_y)
    
    def add_point(self, z):
        x,y = z.real, z.imag
        x,y = self.to_canvas_coords(x,y)
        self.num_points += 1
        if self.drag is not None:
            pygame.draw.circle(self.canvas, (0,0,0), (x,y), self.drag_point_size)
        else:
            pygame.draw.circle(self.canvas, (0,0,0), (x,y), self.point_size)
        self.canvas.set_at((x,y), (0,0,0)) #a single pixel is drawn anyway

    def mousemotion(self, event):
        x,y = event.pos
        x,y = self.to_plane_coords(x,y)
        self.update_label("pointer: {: .2f}{:+.2f}i".format(x,y),"c = {: .2f}{:+.2f}i".format(self.c.real, self.c.imag))

    def update_c(self, event):
        x,y = event.pos
        x,y = self.to_plane_coords(x,y)
        self.c = x + y*1j
        self.reset()

    def reset(self):
        z = 50 + 1j
        self.num_points = 0
        for i in range(self.approach):
            z = choice(iteration(z, self.c))
        self.to_draw.clear()
        self.to_draw.add((z, 0))
        self.canvas.fill((255,255,255))
        self.canvas.blit(pygame.transform.smoothscale(self.mandelbrot, (4*self.scale, 4*self.scale)), self.to_canvas_coords(-2,2))
        self.update_label("pointer: {: .2f}{:+.2f}i".format(*self.to_plane_coords(*pygame.mouse.get_pos())),"c = {: .2f}{:+.2f}i".format(self.c.real, self.c.imag))
                    
    def leave(self, event):
        self.update_label("click to set c", "c = {: .2f}{:+.2f}i".format(self.c.real, self.c.imag))

    def update_label(self, left, right):
        self.label.fill(self.label_bg)
        text_left = self.font.render(left,True,(0,0,0), self.label_bg)
        text_right = self.font.render(right,True,(0,0,0), self.label_bg)
        width = text_right.get_width()
        self.label.blit(text_left, (self.label_offset, (self.label_height - self.font.get_ascent())/2))
        self.label.blit(text_right, (self.width - width - self.label_offset, (self.label_height - self.font.get_ascent())/2))
                
app = App(700, 700, scale=None,
          c=0,
          point_limit=200000, 
          approach=30, 
          center_x=0, center_y=0,
          points_per_frame=1000, 
          drag_point_size=1, point_size=0, 
          label_height=None, label_offset=None, label_font_size=None,
          )
app.run()

"""
try c=
-0.3905407802-0.5867879073j
0.28+0.53j
-0.83+0.16j
"""
