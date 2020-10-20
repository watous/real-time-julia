

from math import *
from random import choice
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from collections import deque
from sortedcontainers import SortedList
from PIL import Image, ImageTk
from image_export import create_image

def iteration(z, c):
    root = (z - c)**0.5
    return(root, -root)

def derivative(z):
    return 2*abs(z)

class App:
    #!! osa y vede dolů
    def __init__(self, root, width, height, scale=None,
                  max_points=100000, #snížit, pokud se to seká, zvýšit, pokud se to nevykresluje dost 
                  approach=50, #zvýšit, pokud ze zobrazují body mimo julia set, jinak klidně snížit
                  center_x=0, center_y=0,
                  points_per_frame=1000 #snížit, pokud se to seká nebo se Tk okno vůbec nenačte, zvýšit, pokud se to nevykresluje dost rychle
                  ):
        self.root = root
        self.width = width
        self.height = height
        self.scale = scale if scale is not None else min(self.width, self.height) // 4
        self.z = 50 +1j
        self.c = 0
        self.points = deque()
        self.to_draw = SortedList([(self.z, 0)], key = lambda x:-x[1])
        self.max_points = max_points
        self.approach = approach
        self.center_x = center_x
        self.center_y = center_y
        self.points_per_frame = points_per_frame
        self.paused = False
        self.prepare()

    def prepare(self):
        self.root.title("Tk Mandelbrot set")
        self.root.iconbitmap("mandelbrot.ico")
        self.label = Label(self.root, text = "", font = ("Courier New", 12))
        self.label.pack()
        self.leave(None)
        self.canvas = Canvas(self.root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()
        self.mandelbrot_image()
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Motion>", self.mousemove)
        self.canvas.bind("<Button-1>", self.drag)
        self.canvas.bind("<Enter>", self.mousemove)
        self.canvas.bind("<Leave>", self.leave)
        self.root.bind("<Control-s>", self.export_image)
        self.reset_points()
        
    def run(self):
        self.drawing_loop()
        self.root.mainloop()

    def export_image(self, event):
        print("exporting image... ", end="")
        self.paused = True
        c = self.c
        x, y = c.real, c.imag
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
        self.paused = False
        self.drawing_loop()

    def mandelbrot_image(self):
        img = Image.open("mandelbrot.png") #obrázek mandelbrot setu ve čtverci max(abs(x),abs(y))=2
        img = img.resize((4*self.scale, 4*self.scale))
        img = ImageTk.PhotoImage(img)
        self.mandelbrot = img
        self.mandelbrot_canvas = self.canvas.create_image(*self.to_canvas_coords(0,0), image = img, anchor = "center")



    def to_canvas_coords(self, x, y):
        canvas_x = self.width / 2 + (x - self.center_x) * self.scale
        canvas_y = self.height / 2 + (-y - self.center_y) * self.scale
        return(canvas_x, canvas_y)

    def to_plane_coords(self, x ,y):
        plane_x = (x - self.width / 2) / self.scale + self.center_x
        plane_y = -((y - self.height / 2) / self.scale + self.center_y)
        return(plane_x, plane_y)
    
    def add_point(self, z):
        if len(self.points) >= self.max_points:
            self.canvas.delete(self.points.popleft())
        x, y = z.real, z.imag
        x, y = self.to_canvas_coords(x, y)
        new_point = self.canvas.create_rectangle((x,y,x,y))
        self.points.append(new_point)

    def mousemove(self, event):
        x = event.x; y = event.y
        x, y = self.to_plane_coords(x, y)
        self.label["text"] = "pointer: {: .2f}{:+.2f}i      c = {: .2f}{:+.2f}i".format(x, y, self.c.real, self.c.imag)

    def drag(self, event):
        x = event.x; y = event.y
        x, y = self.to_plane_coords(x, y)
        self.c = x + y*1j
        self.label["text"] = "pointer: {: .2f}{:+.2f}i      c = {: .2f}{:+.2f}i".format(x, y, self.c.real, self.c.imag)
        self.z = 50 +1j
        self.reset_points()

    def reset_points(self):
        for i in range(self.approach):
            self.z = choice(iteration(self.z, self.c))
        self.to_draw.clear()
        self.to_draw.add((self.z, 0))
        while len(self.points) > 0:
            self.canvas.delete(self.points.popleft())
            
    def leave(self, event):
        self.label["text"] = "click to set c            c = {: .2f}{:+.2f}i".format(self.c.real, self.c.imag)
    
    def drawing_loop(self):
        if self.paused:
            return
        self.root.after(20, self.drawing_loop)
        for i in range(self.points_per_frame):
            point = self.to_draw.pop()
            self.add_point(point[0])
            for new_z in iteration(point[0], self.c):
                new_derivative = point[1] + log(derivative(new_z))
                self.to_draw.add((new_z, new_derivative))
        

x = Tk()
app = App(x, 600, 600,
          max_points=20000, #snížit, pokud se to seká, zvýšit, pokud se to nevykresluje dost 
          approach=50, #zvýšit, pokud ze zobrazují body zjevně mimo julia set, jinak klidně snížit
          points_per_frame=500 #snížit, pokud se to seká nebo se Tk okno vůbec nenačte, zvýšit, pokud se to nevykresluje dost rychle
          )
app.run()

"""
-0.3905407802-0.5867879073j
0.28+0.53j
-0.83+0.16j
"""
