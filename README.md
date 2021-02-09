# real-time-juila
Python3 real-time Julia sets generator in pygame. 
Run `main.py`. Click or use arrows to change the constant *c* in the function z → z<sup>2</sup>+c and you will get the border of this function's prisoner set - the Julia set. 
Press <kbd>ctrl</kbd>+<kbd>S</kbd> to export the prisoner set as a bitmap (PNG). There is the Mandelbrot set in the background as a "map".

Requirements:
```
pygame>=2.0.0
sortedcontainers
Pillow #necessary for image export only
```
![Running example GIF](/images/example.gif)
