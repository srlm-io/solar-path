

from tkinter import *
from tkinter.filedialog import askopenfilename

from PIL import Image, ImageTk

class UserMark():
    def __init__(self, title=None, color=None, image_x=None, image_y=None, circle_reference=None):
        self.title = title
        self.color = color
        self.image_x = image_x
        self.image_y = image_y
        self.circle_reference = circle_reference


# Need to install python3-pil.imagetk

POINT_RADIUS = 8
POINT_OUTLINE_WIDTH = 2
POINT_OUTLINE_COLOR = "#DDDDDD"

required_points = [
    UserMark(title='90 degree mark', color='#FF0000'),
    UserMark(title='15 degree mark', color='#00FF00'),
    UserMark(title='10 degree mark', color='#0000FF'),
]


if __name__ == "__main__":
    root = Tk()
    root.geometry('1200x600')

    # setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = Scrollbar(frame, orient=HORIZONTAL)
    xscroll.grid(row=1, column=0, columnspan=len(required_points) + 1, sticky=E + W)
    yscroll = Scrollbar(frame)
    yscroll.grid(row=0, column=len(required_points) + 2, sticky=N + S)
    canvas = Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, columnspan=len(required_points) + 1, sticky=N + S + E + W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)

    selected_mark = IntVar(value=0)
    column = 0
    for point in required_points:
        Radiobutton(frame, text=point.title, variable=selected_mark, value=column).grid(row=2, column=column, sticky=E + W)
        frame.grid_columnconfigure(column, weight=1)
        column += 1

    def submit_callback():
        print('All done!')

    Button(frame, text='Submit', command=submit_callback).grid(row=2, column=column, sticky=E + W)
    frame.grid_columnconfigure(3, weight=1)
    frame.grid_columnconfigure(4, weight=0)
    frame.pack(fill=BOTH, expand=1)

    # adding the image
    # File = askopenfilename(parent=root, initialdir="~", title='Choose an image.')
    File = './shopside_working.jpg'
    img = ImageTk.PhotoImage(Image.open(File))
    image_canvas = canvas.create_image(0, 0, image=img, anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))

    # function to be called when mouse is clicked
    def place_point(event):

        point = required_points[selected_mark.get()]

        point.image_x = canvas.canvasx(event.x)
        point.image_y = canvas.canvasy(event.y)

        if point.circle_reference is not None:
            canvas.delete(point.circle_reference)

        point.circle_reference = canvas.create_oval(
            point.image_x - POINT_RADIUS, point.image_y - POINT_RADIUS, point.image_x + POINT_RADIUS, point.image_y + POINT_RADIUS,
            fill=point.color, outline=POINT_OUTLINE_COLOR, width=POINT_OUTLINE_WIDTH)

        # Automatically select the next point to place that has not already been placed.
        # If all the points are already placed then don't do anything.
        for i in range(len(required_points)):
            test_index = (selected_mark.get() + i) % len(required_points)
            if required_points[test_index].circle_reference is None:
                selected_mark.set(test_index)
                break

    def scroll_canvas(event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            direction = 1
        if event.num == 4 or event.delta == 120:
            direction = -1

        canvas.yview_scroll(direction, 'units')

    canvas.bind("<Button 1>", place_point)
    canvas.bind('<MouseWheel>', scroll_canvas)
    canvas.bind('<Button 4>', scroll_canvas)
    canvas.bind('<Button 5>', scroll_canvas)

    root.mainloop()
