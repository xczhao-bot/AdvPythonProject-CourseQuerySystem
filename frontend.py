# name: Xuechi Zhao, Yueqi Wang
# CIS 41B final project : Udemy Courses Query System

import backend

"""DON'T change sequence of this block"""
import matplotlib

matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

"""DON'T change sequence of this block"""
from tkinter import ttk
import sqlite3
import os
from datetime import date
import tkinter.messagebox as tkmb
import webbrowser

UdemyColorDict = {"red": "#ec5252", "pearl": "#edece6", "yellow": "#f5c252",
                  "blue": "#69c1d0", "dark purple": "430d31", "purple": "#6e1952",
                  "orange": "f68f30", "dark blue": "#19263a", "mombasa": "#645a52"}


class MainWin(tk.Tk):
    """GUI TK window to drive the user interface"""
    DB = "courseDB.db"
    TB = "CoursesDB"
    TB_LEVEL = "Level"
    TB_PAY = "Payment"
    TB_SCAT = "Subcategory"

    def __init__(self):
        super().__init__()

        # make window resizable
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        my_sizegrip = ttk.Sizegrip(self)
        my_sizegrip.grid(row=0, sticky='nw')

        self.title("Udemy")
        # top label
        self.topLabel = tk.Label(self, text="Udemy IT Courses Query System", font=("Helvetica", 18, "bold"),
                                 fg=UdemyColorDict["red"])
        self.topLabel.grid(row=0, columnspan=3)

        # 3 buttons for overview options
        self.b1 = tk.Button(self, text="Course\nSummary",
                            height=4, width=12, fg=UdemyColorDict["mombasa"], font="Helvetica",
                            command=lambda: self.plot(1))
        self.b1.grid(row=1, column=0)
        self.b2 = tk.Button(self, text="Categories",
                            height=4, width=12, fg=UdemyColorDict["mombasa"], font="Helvetica",
                            command=lambda: self.plot(2))
        self.b2.grid(row=1, column=1)
        self.b3 = tk.Button(self, text="Language\n&\nLevels",
                            height=4, width=12, fg=UdemyColorDict["mombasa"], font="Helvetica",
                            command=lambda: self.plot(3))
        self.b3.grid(row=1, column=2)

        # label for the entry box
        self.entryLabel = tk.Label(self, text="Search Courses", font=("Helvetica", 15), fg=UdemyColorDict["mombasa"])
        self.entryLabel.grid(row=3, column=0, sticky="we")
        # entry widget
        self.E = tk.Entry(self)
        self.E.grid(row=3, column=1, columnspan=2, sticky='we')

        # database connection
        self.conn = sqlite3.connect(self.DB)
        self.cur = self.conn.cursor()

        self.cur.execute(f"SELECT level from {self.TB_LEVEL}")
        self.level = [t[0] for t in self.cur.fetchall()]
        self.cur.execute(f"SELECT subcategory from {self.TB_SCAT}")
        self.subcategory = [t[0] for t in self.cur.fetchall()]

        # optionMenu1: Levels
        self.optV1 = tk.StringVar()
        self.optV1.set(self.level[0])
        self.om1 = tk.OptionMenu(self, self.optV1, *self.level)
        self.om1.grid(row=4, column=1, sticky="we")
        # optionMenu2: Subcategories
        self.optV2 = tk.StringVar()
        self.optV2.set(self.subcategory[0])
        self.om2 = tk.OptionMenu(self, self.optV2, *self.subcategory)
        self.om2.grid(row=5, column=1, columnspan=2, sticky='we')
        # label to provide user instruction
        self.bottomLabel = tk.Label(self, text="* Enter keyword, select options and hit <<<GO>>> *",
                                    font=("Helvetica", 10), fg=UdemyColorDict["red"])
        self.bottomLabel.grid(row=6, columnspan=2, sticky='we')
        # Go Button
        goButton = tk.Button(self, text="<<<GO>>>", command=self._driver, fg=UdemyColorDict["mombasa"])
        goButton.grid(row=6, column=2)

        # close the tk window and disconnect from database when user click "X"
        self.protocol("WM_DELETE_WINDOW", self.end_app)

    def end_app(self):
        """close the app and disconnect with database"""
        self.conn.close()
        self.quit()

    def plot(self, option):
        """plot the overview chart based on user choice"""
        optionD = {1: backend.plotSummaryChart,
                   2: backend.plotCategoryChart,
                   3: backend.plotLevelChart}
        plotFunction = optionD[option]
        PlotWin(self, plotFunction)


    def _driver(self):
        """process user query criteria, present treeview window"""
        level = self.optV1.get()
        subcategory = self.optV2.get()
        search = f'%{self.E.get()}%'
        print("searching results for: ", level, subcategory, self.E.get())

        self.cur.execute(f'''SELECT {self.TB}.id, {self.TB}.title, {self.TB_LEVEL}.level, {self.TB}.price, 
                         {self.TB}.rating, {self.TB}.num_subscribers, {self.TB}.num_reviews, {self.TB}.last_update_date, {self.TB}.contents, {self.TB}.url   
                         FROM {self.TB} JOIN {self.TB_LEVEL} 
                         ON {self.TB}.level_id = {self.TB_LEVEL}.id 
                         JOIN {self.TB_SCAT} 
                         ON {self.TB}.subcategory_id = {self.TB_SCAT}.id 
                         WHERE {self.TB_LEVEL}.level = ?
                         AND {self.TB_SCAT}.subcategory = ?
                         AND {self.TB}.title LIKE ?''', (level, subcategory, search))
        results = self.cur.fetchall()
        if not results:
            tkmb.showerror(title="NOT SO LUCKY", message="NOT SO LUCKY.\nTry other combination." )
        else:
            Treeview(self, results)


class PlotWin(tk.Toplevel):
    """Canvas to display matplotlib"""

    def __init__(self, master, plotFct):
        super().__init__(master)
        self.title("Overview")
        fig = plotFct()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid()
        self.canvas.draw()


class Treeview(tk.Toplevel):
    """TopLevel window to show courses information based on user selection"""

    def __init__(self, master, lst):
        super().__init__(master)

        self.lst = lst

        self.tree = ttk.Treeview(self)
        self.tree.grid()

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(sticky='ns', row=0, column=1)
        self.tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.grid(sticky='ns', row=1, column=0)
        self.tree.configure(xscrollcommand=hsb.set)

        # define columns
        self.tree["columns"] = (
            "id", "title", "level", "price", "rating", "num_subscribers", "num_reviews", "last_update_date", "contents")
        self.tree['show'] = 'headings'
        widths = [1, 5, 1, 1, 1, 1, 1, 1, 1]
        dct = dict(zip(self.tree['columns'], widths))
        # format columns
        for col, w in dct.items():
            self.tree.column(col, anchor='center', width=w * 90, stretch=True)
            self.tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))

        # add Data
        i = 0
        for course in self.lst:
            self.tree.insert('', tk.END, values=course[:-1], iid=i)
            i += 1

        # add buttons to show web or save to file
        self.button = tk.Button(self, text="SELECT", command=self.selection, fg=UdemyColorDict["mombasa"])
        self.button.grid()
        # add style
        style = ttk.Style()
        style.configure("Treeview", foreground=UdemyColorDict["mombasa"], fieldbackground=UdemyColorDict["pearl"])
        # change selected color
        style.map("Treeview", background=[('selected', UdemyColorDict["blue"])])
        # make treeview resizable
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        my_sizegrip = ttk.Sizegrip(self)
        my_sizegrip.grid(row=0, sticky='nw')

    def selection(self):
        """open web or save to file"""
        # ask if user would like to save course title and url to file
        if self.tree.selection():
            openWeb = tkmb.askquestion(parent=self, title="Aspire for more", message="Would you like to open website and learn more about the course? ")
            print(openWeb, "???")
            if openWeb=="yes":
                for idx in self.tree.selection():
                    url = self.lst[int(idx)][-1]
                    if url:
                        webbrowser.open("https://www.udemy.com"+url)
            # ask if user would like to save to file
            else:
                save = tkmb.askquestion(parent=self, title="Save it for a rainy day",
                                       message="How about SAVE to FILE and learn later? ")
                if save=="yes":
                    askSaveFile = tk.filedialog.asksaveasfile(parent=self, title="save your favorite courses to file",
                                                          defaultextension='.txt', initialfile="UdemyWishlist",
                                                          initialdir=os.getcwd())
                    if askSaveFile:
                        with open(askSaveFile.name, "a") as fh:
                            fh.write("Here are your Udemy selections at " + str(date.today()) + '\n')
                            for idx in self.tree.selection():
                                title = self.lst[int(idx)][1]
                                url = "https://www.udemy.com" + self.lst[int(idx)][-1]
                                fh.write('\n' + title + '\n' + url + '\n')
        else:
            tkmb.showwarning(message="404. Ooops!!! \nNothing was selected")
        # reset the treeview by the end
        self.tree.selection_clear()

    def treeview_sort_column(self, tree, col, reverse):
        """enable the sorting functionality """
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0].split(' ')[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        # reverse sort next time
        self.tree.heading(col, text=col,
                          command=lambda _col=col: self.treeview_sort_column(self.tree, _col, not reverse))


if __name__ == "__main__":
    app = MainWin()
    app.mainloop()
