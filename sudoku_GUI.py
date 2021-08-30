import numpy as np
import tkinter as tk
from tkinter import font
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
from pathlib import Path
from sudoku_extrapolation import extrapolate_sudoku
from sudoku_solver import solve_sudoku


class sudoku_gui(tk.Tk):
    '''Container of the frames that are shown to the users'''

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = font.Font(family='Helvetica', size=20, weight="bold")
        self.subtitle_font = font.Font(family='Helvetica', size=14, weight="bold")
        self.button_font = font.Font(family='Helvetica', size=12)

        # create container with frames, raise a frame to make it visible
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (one_CNN, two_grid, three_solution):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # all frames in the same location
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("one_CNN")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()



class _variables:
    '''Keep some variables that are used and whose value is changed by other classes'''
    selected_model = ''
    sudoku_grid = np.zeros(shape=(9,9), dtype=np.int8)
    sudoku_grid_corrected = np.zeros(shape=(9,9), dtype=np.int8)
    margin = 20
    side = 50



class ToolTip(object):
    '''Create a tooltip'''
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=font.Font(family='Helvetica', size=10))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def CreateToolTip(widget, text):
    '''Given a widget and a text, create a tooltip'''
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)



class one_CNN(tk.Frame, _variables):
    '''First frame, contains the introduction and the choice between using a model for digital numbers only or even handwritten digits'''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.pack_propagate(0)

        # title label
        title_label = tk.Label(self, text="Sudoku solver", font=controller.title_font)
        title_label.place(height=45, width=600, x=300, y=4)

        # subtitle label
        label = tk.Label(self, text="Select the model", font=controller.subtitle_font)
        label.place(height=45, width=600, x=300, y=450)

        # introduction label
        intro_label = tk.Label(self, text="Hello, this program allows the user to solve a sudoku puzzle starting from a photo.\n\n"
                "This program can use a CNN trained on two different datasets.\n\n"
                "The first dataset is composed of the digits from 1 to 9 extracted from a sudoku magazine.\n"
                "The model trained on this dataset is then suitable for the recognition of sudoku puzzles that have not yet been solved.\n\n"
                "The second dataset is instead constituted by the union of the previous dataset and the MNIST handwritten digits dataset.\n"
                "So, the model trained on the second dataset can be used to recognize half-solved sudoku puzzles with handwritten digits.\n\n"
                "In the first page, the user will choose the model to be employed.\n"
                "In the second page, the user will upload an image of a sudoku and proceed with the number recognition.\n"
                "Any number can be modified just by clicking on the cell whose digit needs to be changed.\n"
                "This function can be useful in cases of wrong recognition or just to try different puzzles by changing some digits.\n"
                "Finally, in the third page, the user can obtain the sudoku puzzle's solution, only if existing.\n\n"
                "If there are any doubts on what a button does, a tooltip will appear when hoovering over it.\n\n"
                "First of all, select if you would like to solve a sudoku puzzle with or without handwritten numbers.",
                font=controller.button_font, justify='left', relief=tk.RIDGE)
        intro_label.place(height=380, width=900, x=150, y=60)

        # button to select the first model
        model1_button = tk.Button(self, text="Unsolved sudoku", font=controller.button_font,
                                command=lambda: [self.__init_model1(),
                                messagebox.showinfo(title='Model selected',
                                message="The model for unsolved sudoku puzzles will be used. Click on 'Continue' to proceed."),
                                model2_button.config(state=tk.DISABLED),
                                continue_button.config(state=tk.NORMAL),
                                reset_button.config(state=tk.NORMAL)])
        model1_button.place(height=35, width=240, x=350, y=515)
        CreateToolTip(model1_button, "Choose this option to use the model for\n"
                                "recognizing numbers of sudoku puzzles\nthat have not yet been solved.")

        # button to select the second model
        model2_button = tk.Button(self, text="Half-solved sudoku", font=controller.button_font,
                                command=lambda: [self.__init_model2(),
                                messagebox.showinfo(title='Model selected',
                                message="The model for half-solved sudoku puzzles will be used. Click on 'Continue' to proceed."),
                                model1_button.config(state=tk.DISABLED),
                                continue_button.config(state=tk.NORMAL),
                                reset_button.config(state=tk.NORMAL)])
        model2_button.place(height=35, width=240, x=610, y=515)
        CreateToolTip(model2_button, "Choose this option to use the model for recognizing\nnumbers of half-solved sudoku puzzles.")

        # button to reset the first frame
        reset_button = tk.Button(self, text="Reset", font=controller.button_font,
                            command=lambda: [model1_button.config(state=tk.NORMAL),
                            model2_button.config(state=tk.NORMAL),
                            continue_button.config(state=tk.DISABLED),
                            reset_button.config(state=tk.DISABLED)],
                            state=tk.DISABLED)
        reset_button.place(height=35, width=90, x=500, y=600)
        CreateToolTip(reset_button, "Reset this page.")

        # button to go to the second frame
        continue_button = tk.Button(self, text="Continue", font=controller.button_font,
                            command=lambda: controller.show_frame("two_grid"),
                            state=tk.DISABLED)
        continue_button.place(height=35, width=90, x=610, y=600)
        CreateToolTip(continue_button, "Go to the second page.")


    def __init_model1(self):
        '''Initialize the variable for the selected model with the first one'''
        _variables.selected_model = "sudoku_model/model_sudoku.hdf5"


    def __init_model2(self):
        '''Initialize the variable for the selected model with the second one'''
        _variables.selected_model = "sudoku_model/model_sudoku_mnist.hdf5"



class two_grid(tk.Frame, _variables):
    '''Second frame, contains the upload of a sudoku image and the extrapolation of the numbers, subsequently placed in a grid'''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.pack_propagate(0)

        self.row, self.col = -1, -1
        self.sudoku_grid = np.zeros(shape=(9,9), dtype=np.int8)
        self.sudoku_grid_corrected = np.zeros(shape=(9,9), dtype=np.int8)
        self.image_path = ''
        self.previous_image_path = ''
        self.control_var = 0
        self.img = ''
        self.cell_font = font.Font(family='Helvetica', size=12)

        # label where the image is displayed
        self.im_label = tk.Label(self, image=self.img)
        self.im_label.place(x=160, y=116)

        # frame's title label
        label = tk.Label(self, text="Upload the image and fill the grid", font=controller.subtitle_font)
        label.place(height=45, width=600, x=300, y=4)

        # label to upload the image
        image_button = tk.Button(self, text="Upload the image", font=controller.button_font,
                                command=lambda: [self.__init_prev_path(),
                                self.__open_image(),
                                self.__manage_numbers_and_buttons()])
        image_button.place(height=35, width=220, x=220, y=52)
        CreateToolTip(image_button, "Open the file path and choose\na sudoku image to upload.")

        # label showing the name of the choosen image
        self.path_label = tk.Label(self, text='', font=controller.button_font, fg='green')
        self.path_label.place(height=35, x=450, y=52)
        self.path_label.place_forget()

        # button which allows to rotate the image
        self.rotate_button = tk.Button(self, text=u"\u21BB", font=font.Font(size=25),
                            command=lambda: self.__rotate_image(),
                            state=tk.DISABLED)
        self.rotate_button.place(height=35, width=35, x=175, y=52)
        CreateToolTip(self.rotate_button, "Rotate the image by 90 degrees in clockwise direction.")

        # create and draw a grid for the sudoku
        self.margin = _variables.margin
        self.side = _variables.side
        self.dimension = self.side * 9 + self.margin * 2
        self.canvas = tk.Canvas(self, width=self.dimension, height=self.dimension)
        self.canvas.place(x=650, y=100)

        self.__draw_grid()
        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

        # button to fill the grid with the sudoku after the extrapolation from the image
        self.fill_button = tk.Button(self, text="Fill the grid with the sudoku", font=controller.button_font,
                            command=lambda: [self.__increase_control_var(),
                            self.__extrapolate_sudoku(),
                            self.__draw_sudoku(),
                            self.info_label.place(height=60, width=130, x=1020, y=38),
                            self.continue_button.config(state=tk.NORMAL)],
                            state=tk.DISABLED)
        self.fill_button.place(height=35, width=220, x=790, y=52)
        CreateToolTip(self.fill_button, "Extrapolate the sudoku from the image\nand fill the grid with the values of the cells.\n"
                    "It is possible to change the values in the grid.\n"
                    "In order to cancel a number enter a '0'\nor press 'BackSpace' on the keybord.")

        # label showing information
        self.info_label = tk.Label(self, text="Click on a cell\nto change or\ncancel its value",
                            font=controller.button_font, fg="red", justify='left')
        self.info_label.place(height=60, width=130, x=1020, y=38)
        self.info_label.place_forget()

        # button to return to the first frame
        return_button = tk.Button(self, text="Return", font=controller.button_font,
                            command=lambda: [controller.show_frame("one_CNN"),
                            self.im_label.config(image=''),
                            self.__reset_image_path(),
                            self.canvas.delete("numbers"),
                            self.__reset_sudoku(),
                            self.path_label.place_forget(),
                            self.info_label.place_forget(),
                            self.rotate_button.config(state=tk.DISABLED),
                            self.fill_button.config(state=tk.DISABLED),
                            self.continue_button.config(state=tk.DISABLED),
                            self.reset_button.config(state=tk.DISABLED)])
        return_button.place(height=35, width=90, x=445, y=600)
        CreateToolTip(return_button, "Return to the first page.")

        # button to reset the second frame
        self.reset_button = tk.Button(self, text="Reset", font=controller.button_font,
                            command=lambda: [self.im_label.config(image=''),
                            self.__reset_image_path(),
                            self.canvas.delete("numbers"),
                            self.__reset_sudoku(),
                            self.path_label.place_forget(),
                            self.info_label.place_forget(),
                            self.rotate_button.config(state=tk.DISABLED),
                            self.fill_button.config(state=tk.DISABLED),
                            self.continue_button.config(state=tk.DISABLED),
                            self.reset_button.config(state=tk.DISABLED)],
                            state=tk.DISABLED)
        self.reset_button.place(height=35, width=90, x=555, y=600)
        CreateToolTip(self.reset_button, "Reset this page.")

        # button to go to the third frame
        self.continue_button = tk.Button(self, text="Continue", font=controller.button_font,
                            command=lambda: controller.show_frame("three_solution"),
                            state=tk.DISABLED)
        self.continue_button.place(height=35, width=90, x=665, y=600)
        CreateToolTip(self.continue_button, "Go to the third page.")


    def __open_image(self):
        '''Open an image and display it'''
        try:
            filename = filedialog.askopenfilename(title='Open a file',
                        filetypes=(('Image Files', '*.png'), ('Image Files', '*.PNG'),
                        ('Image Files', '*.jpg'), ('Image Files', '*.JPG'),
                        ('Image Files', '*.jpeg'), ('Image Files', '*.JPEG')))
        except:
            pass

        if filename:
            self.image_path = filename
            img = Image.open(filename)
            img = self.__reorient_image(img)
            width, height = img.size
            if width < height:
                img = img.resize((340, 456), Image.ANTIALIAS)
            elif width > height:
                img = img.resize((456, 340), Image.ANTIALIAS)
            else:
                img = img.resize((340, 340), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            self.img = img
            self.im_label.configure(image=img)
            messagebox.showinfo(title='File uploaded successfully', message=f"Image has been successfully uploaded from '{filename}'. "
                                "Click on 'Fill the grid with the sudoku' to proceed. It may take a few seconds. Then click on 'Continue'.")


    def __reorient_image(self, im):
        '''Reorient an image using its exif'''
        try:
            image_exif = im._getexif()
            image_orientation = image_exif[274]
            if image_orientation in (2,'2'):
                return im.transpose(Image.FLIP_LEFT_RIGHT)
            elif image_orientation in (3,'3'):
                return im.transpose(Image.ROTATE_180)
            elif image_orientation in (4,'4'):
                return im.transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (5,'5'):
                return im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (6,'6'):
                return im.transpose(Image.ROTATE_270)
            elif image_orientation in (7,'7'):
                return im.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
            elif image_orientation in (8,'8'):
                return im.transpose(Image.ROTATE_90)
            else:
                return im
        except (KeyError, AttributeError, TypeError, IndexError):
            return im


    def __rotate_image(self):
        '''Rotate and save an image by 90 degrees in clockwise direction'''
        path = self.image_path
        im = Image.open(path)
        rot = im.rotate(270, resample=Image.BICUBIC, expand=True)
        rot.save(path, quality=95, subsampling=0)
        width, height = rot.size
        if width < height:
            img = rot.resize((340, 456), Image.ANTIALIAS)
        elif width > height:
            img = rot.resize((456, 340), Image.ANTIALIAS)
        else:
            img = rot.resize((340, 340), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.img = img
        self.im_label.configure(image=img)


    def __draw_grid(self):
        '''Draw a sudoku grid'''
        for i in range(10):
            color = "black" if i % 3 == 0 else "gray"

            x0 = self.margin + i * self.side
            y0 = self.margin
            x1 = self.margin + i * self.side
            y1 = self.dimension - self.margin
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = self.margin
            y0 = self.margin + i * self.side
            x1 = self.dimension - self.margin
            y1 = self.margin + i * self.side
            self.canvas.create_line(x0, y0, x1, y1, fill=color)


    def __draw_sudoku(self):
        '''Draw the extracted sudoku in the grid'''
        self.sudoku_grid_corrected = np.copy(self.sudoku_grid)
        _variables.sudoku_grid = self.sudoku_grid
        _variables.sudoku_grid_corrected = self.sudoku_grid_corrected 
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                value = self.sudoku_grid[i][j]
                if value != 0:
                    x = self.margin + j * self.side + self.side / 2
                    y = self.margin + i * self.side + self.side / 2
                    color = "black"
                    self.canvas.create_text(x, y, text=value, tags="numbers", fill=color, font=self.cell_font)


    def __draw_correct_sudoku(self):
        '''Draw the modified sudoku in the grid'''
        _variables.sudoku_grid_corrected = self.sudoku_grid_corrected
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                value = self.sudoku_grid_corrected[i][j]
                if value != 0:
                    x = self.margin + j * self.side + self.side / 2
                    y = self.margin + i * self.side + self.side / 2
                    color = "black" if value == self.sudoku_grid[i][j] else "red"
                    self.canvas.create_text(x, y, text=value, tags="numbers", fill=color, font=self.cell_font)


    def __draw_square(self):
        '''Draw a red square to show that a cell is selected'''
        self.canvas.delete("square")
        if self.row >= 0 and self.col >= 0:
            x0 = self.margin + self.col * self.side + 1
            y0 = self.margin + self.row * self.side + 1
            x1 = self.margin + (self.col + 1) * self.side - 1
            y1 = self.margin + (self.row + 1) * self.side - 1
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tags="square")


    def __cell_clicked(self, event):
        '''Determine what cell is clicked'''
        x, y = event.x, event.y
        if self.margin < x < self.dimension - self.margin and self.margin < y < self.dimension - self.margin:
            self.canvas.focus_set()
            row, col = (y - self.margin) // self.side, (x - self.margin) // self.side
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        self.__draw_square()


    def __key_pressed(self, event):
        '''Change a digit or cancel it depending on the key that is pressed'''
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.sudoku_grid_corrected[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_correct_sudoku()
            self.__draw_square()
        if self.row >= 0 and self.col >= 0 and event.keysym == "BackSpace":
            self.sudoku_grid_corrected[self.row][self.col] = 0
            self.__draw_correct_sudoku()
            self.__draw_square()

    
    def __init_prev_path(self):
        '''Initialize the path of the previous image'''
        self.previous_image_path = self.image_path

    
    def __increase_control_var(self):
        '''Assign a value of 1 to a control variable'''
        self.control_var = 1

        
    def __reset_image_path(self):
        '''Reset the path of the image'''
        self.image_path = ''

    
    def __manage_numbers_and_buttons(self):
        '''Manage the deletion of the numbers from the grid and the activation of the buttons, 
        depending on the selected path and the previous path'''
        if self.image_path == '':
            self.canvas.delete("numbers")
            self.__reset_sudoku()
            self.path_label.place_forget()
            self.info_label.place_forget()
            self.rotate_button.config(state=tk.DISABLED)
            self.fill_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.DISABLED)
            self.continue_button.config(state=tk.DISABLED)
        elif self.previous_image_path != self.image_path:
            self.control_var = 0
            self.path_label.config(text=Path(self.image_path).stem)
            self.path_label.place(height=35, x=450, y=52)
            self.canvas.delete("numbers")
            self.__reset_sudoku()
            self.info_label.place_forget()
            self.rotate_button.config(state=tk.NORMAL)
            self.fill_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.DISABLED)
        elif self.previous_image_path == self.image_path and self.control_var == 0:
            self.canvas.delete("numbers")
            self.__reset_sudoku()
            self.info_label.place_forget()
            self.rotate_button.config(state=tk.NORMAL)
            self.fill_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.DISABLED)
        elif self.previous_image_path == self.image_path and self.control_var != 0:
            self.rotate_button.config(state=tk.NORMAL)
            self.fill_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.NORMAL)

    
    def __extrapolate_sudoku(self):
        '''Extrapolate the sudoku numbers from an image using the appropriate function'''
        my_sudoku_grid = extrapolate_sudoku(self.image_path, _variables.selected_model)
        self.sudoku_grid = np.copy(my_sudoku_grid)

        if (my_sudoku_grid == np.zeros((9, 9), np.int8)).all():
            messagebox.showerror(title='No grid detected', message='There is a problem with the uploaded image, try to retake the picture. '
                                'The image must not be too warped. '
                                'The grid must be clearly visible and the outline must be well defined.')
    

    def __reset_sudoku(self):
        '''Reset to zero all the values of the sudoku grid'''
        self.sudoku_grid = np.zeros((9, 9), np.int8)


    def get_grid(self):
        '''Return the modified grid'''
        return self.sudoku_grid_corrected



class three_solution(tk.Frame, _variables):
    '''Third frame, contains the resolution of the sudoku'''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.pack_propagate(0)

        self.sudoku_grid = np.zeros(shape=(9,9), dtype=np.int8)
        self.sudoku_grid_corrected = np.zeros(shape=(9,9), dtype=np.int8)
        self.solved_sudoku_grid = np.zeros(shape=(9,9), dtype=np.int8)
        self.cell_font = font.Font(family='Helvetica', size=12)

        # frame's title label
        label = tk.Label(self, text="Solve the sudoku puzzle", font=controller.subtitle_font)
        label.place(height=45, width=600, x=300, y=4)

        # draw the grid
        self.margin = _variables.margin
        self.side = _variables.side
        self.dimension = self.side * 9 + self.margin * 2
        self.canvas = tk.Canvas(self, width=self.dimension, height=self.dimension)
        self.canvas.place(x=355, y=100)

        self.__draw_grid()
   
        # button to solve the sudoku puzzle
        solve_button = tk.Button(self, text="Show the solution", font=controller.button_font,
                            command=lambda: [self.__draw_solution(),
                            reset_button.config(state=tk.NORMAL)])
        solve_button.place(height=35, width=220, x=490, y=52)
        CreateToolTip(solve_button, "Fill the grid with the solution.\nIn case of a non existing solution,\na message will be displayed.")    

        # button to return to the second frame
        return_button = tk.Button(self, text="Return", font=controller.button_font,
                            command=lambda: [controller.show_frame("two_grid"),
                            reset_button.config(state=tk.DISABLED)])
        return_button.place(height=35, width=90, x=445, y=600)
        CreateToolTip(return_button, "Return to the second page.")

        # button to reset the third frame
        reset_button = tk.Button(self, text="Reset", font=controller.button_font,
                            command=lambda: [self.__draw_sudoku_grid(),
                            reset_button.config(state=tk.DISABLED)],
                            state=tk.DISABLED)
        reset_button.place(height=35, width=90, x=555, y=600)
        CreateToolTip(reset_button, "Reset this page.")

        # button to exit from the program
        exit_button = tk.Button(self, text="Exit", font=controller.button_font, command=lambda: self.__exit())
        exit_button.place(height=35, width=90, x=665, y=600)
        CreateToolTip(exit_button, "Close the program.")


    def __draw_grid(self):
        '''Draw the extracted sudoku in the grid'''
        for i in range(10):
            color = "black" if i % 3 == 0 else "gray"

            x0 = self.margin + i * self.side
            y0 = self.margin
            x1 = self.margin + i * self.side
            y1 = self.dimension - self.margin
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = self.margin
            y0 = self.margin + i * self.side
            x1 = self.dimension - self.margin
            y1 = self.margin + i * self.side
            self.canvas.create_line(x0, y0, x1, y1, fill=color)


    def __draw_sudoku_grid(self):
        '''Draw the modified sudoku in the grid'''
        self.sudoku_grid = _variables.sudoku_grid
        self.sudoku_grid_corrected = _variables.sudoku_grid_corrected
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                value = self.sudoku_grid_corrected[i][j]
                if value != 0:
                    x = self.margin + j * self.side + self.side / 2
                    y = self.margin + i * self.side + self.side / 2
                    color = "black" if value == self.sudoku_grid[i][j] else "red"
                    self.canvas.create_text(x, y, text=value, tags="numbers", fill=color, font=self.cell_font)


    def __draw_solution(self):
        '''Draw the resolved sudoku in the grid'''
        self.solved_sudoku_grid = np.copy(_variables.sudoku_grid_corrected)
        check = solve_sudoku(self.solved_sudoku_grid)
        if check == False:
            messagebox.showerror(title='No solution',
                                message='This sudoku has no solution. Return to the previous page and try to correct the values.')
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                value = self.solved_sudoku_grid[i][j]
                if value != 0:
                    x = self.margin + j * self.side + self.side / 2
                    y = self.margin + i * self.side + self.side / 2
                    color = ''
                    if value == _variables.sudoku_grid[i][j] and value == _variables.sudoku_grid_corrected[i][j]:
                        color = "black"
                    elif value == _variables.sudoku_grid_corrected[i][j]:
                        color = "red"
                    else:
                        color = "blue"
                    self.canvas.create_text(x, y, text=value, tags="numbers", fill=color, font=self.cell_font)


    def __exit(self):
        '''Exit from the program'''
        if messagebox.askyesno("Exit", "Do you really want to close the program?"):
            exit()
        else:
            pass


    def tkraise(self, aboveThis=None):
        '''Redefine the function to update the third frame'''
        # Get a reference to the second page
        two_grid_ref = self.controller.frames['two_grid']

        # Get the selected item from the second page
        self.sudoku_grid = two_grid_ref.get_grid()
        self.__draw_sudoku_grid()

        # Call the real .tkraise
        super().tkraise(aboveThis)





if __name__ == "__main__":
    gui = sudoku_gui()
    gui.title('Sudoku solver')
    gui.iconphoto(True, tk.PhotoImage(file='icon_and_demo_images/sudoku_icon.png'))
    gui.resizable('False', 'False')
    gui.geometry("1200x650")
    gui.mainloop()
