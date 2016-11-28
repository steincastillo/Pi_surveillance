
from tkinter import *
from tkinter import ttk 

root = Tk()
root.wm_title("Pi Surveillance")

content = ttk.Frame(root, padding=(7,7,7,7))

feed = ttk.Frame(content, borderwidth=5, relief="sunken", width=450, height=350)

sep = ttk.Separator(content, orient=VERTICAL)

lbl_temp = ttk.Label(content, text="Temperature:")
lbl_press = ttk.Label(content, text="Pressure:")
lbl_hum = ttk.Label(content, text="Humidity: ")
ent_temp = ttk.Entry(content)
ent_press = ttk.Entry(content)
ent_hum = ttk.Entry(content)

but_capture = ttk.Button(content, text="Capture")
but_quit = ttk.Button(content, text="Quit")
but_check = ttk.Button(content, text="Check")

console = Text(content, state="disabled",  width=70, height=8, wrap="none")

content.grid(column=0, row=0, sticky=(N,S,E,W))
feed.grid(column=0, row=0, columnspan=3, rowspan=3)

lbl_temp.grid(column=3, row=0, sticky="E")
lbl_press.grid(column=3, row=1, sticky="E")
lbl_hum.grid(column=3, row=2, sticky="E")
ent_temp.grid(column=4, row=0)
ent_press.grid(column=4, row=1)
ent_hum.grid(column=4, row=2)

console.grid(column=0, row=3, columnspan=5, rowspan=1, pady=5)

but_capture.grid(column=2, row=5, sticky="E", pady=5)
but_check.grid(column=3, row=5, sticky="E", pady=5)
but_quit.grid(column=4, row=5, sticky="W", pady=5)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=1)
content.columnconfigure(4, weight=1)
content.rowconfigure(1, weight=1)

root.mainloop()

