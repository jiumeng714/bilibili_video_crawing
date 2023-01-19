import io
# allows for image formats other than gif
from PIL import Image, ImageTk
try:
  # Python2
  import Tkinter as tk
  from urllib2 import urlopen
except ImportError:
  # Python3
  import tkinter as tk
  from urllib.request import urlopen


def resize(w, h, w_box, h_box, pil_image):
    f1 = w_box / w
    f2 = h_box / h
    factor = min(f1, f2)
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


root = tk.Tk()
url = "http://i0.hdslb.com/bfs/archive/70f2317dfa0661127baff2c5913c2df7dba7487f.jpg"

image_bytes = urlopen(url).read()
# internal data file
data_stream = io.BytesIO(image_bytes)
# open as a PIL image object
pil_image = Image.open(data_stream)
# optionally show image info
# get the size of the image
w, h = pil_image.size
# w_box = root.winfo_width()
# h_box = root.winfo_height()
w_box = 800
h_box = 600
pil_image = resize(w, h, w_box=w_box, h_box=h_box, pil_image=pil_image)
# split off image file name
fname = url.split('/')[-1]
sf = "{} ({}x{})".format(fname, w, h)
root.title(sf)
# convert PIL image object to Tkinter PhotoImage object
tk_image = ImageTk.PhotoImage(pil_image)
# put the image on a typical widget
label = tk.Label(root, image=tk_image, bg='brown')
label.pack(padx=5, pady=5)
root.mainloop()





