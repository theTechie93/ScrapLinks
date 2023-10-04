from tkinter import *

from modules import scrapData


class Application(Frame):
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        global ScrapUrl
        global SearchString
        global FdateString
        global TdateString

        ScrapUrl = StringVar(None)
        SearchString = StringVar(None)
        FdateString = StringVar(None)
        TdateString = StringVar(None)

        stepOne = LabelFrame(self, text="Web Scraping")
        stepOne.grid(row=0, columnspan=8, sticky='W', padx=5, pady=5, ipadx=180, ipady=50)

        # self.StringLabel = Label(stepOne, text="Search String: ")
        # self.StringLabel.place(x=1, y=10)

        self.SString = ""  # Entry(stepOne, textvariable=SearchString, width=42)
        # self.SString.place(x=80, y=10)

        # self.FDateLabel = Label(stepOne, text="From date: ")
        # self.FDateLabel.place(x=1, y=10)
        #
        # self.Fdate = Entry(stepOne, textvariable=FdateString, width=15)
        # self.Fdate.place(x=80, y=10)
        #
        # self.TDateLabel = Label(stepOne, text="To date: ")
        # self.TDateLabel.place(x=190, y=10)
        #
        # self.Tdate = Entry(stepOne, textvariable=TdateString, width=15)
        #
        # self.Tdate.place(x=242, y=10)

        ScrapBtn = Button(stepOne, width=15, text="Start Scraping",
                          command=lambda: scrapData())
        ScrapBtn.place(x=225, y=40)


global root
root = Tk()
root.title("Web Scraping")
root.geometry("400x115")
app = Application(root)
root.mainloop()
