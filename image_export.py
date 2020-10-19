


from math import sqrt
from PIL import Image

def create_image (c, width = 800, height = 800,
                  xleft = -2, xright = 2,
                  ytop = 2, ybottom = -2,
                  iterations = 500,
                  prisoner_color = (0,0,0,255), escapee_color = (255,255,255,0)
                  ):


    abs_limit = (1+sqrt(1+4*abs(c)))/2

    pixel_list = []

    for y0 in range (height):
        y = ytop + (ybottom - ytop) * (y0 + 0.5) / height
        for x0 in range (width):
            x = xleft + (xright - xleft) * (x0 + 0.5) / width
            z = x + y*1j
            for i in range (iterations):
                z = z**2 + c
                if abs(z) > abs_limit: #escapee
                    pixel_list.append (escapee_color)
                    break
            else:
                pixel_list  .append (prisoner_color)

    img = Image.new ("RGBA", size = (width, height))
    img.putdata (pixel_list)
    return img

if __name__ == "__main__":
    c = eval(input("c = "))
    PATH = "../output/julia_set.png"
    img = create_image (c)
    img.save (PATH, format = "PNG")



