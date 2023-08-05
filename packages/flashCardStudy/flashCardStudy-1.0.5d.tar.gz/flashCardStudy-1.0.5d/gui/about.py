from Tkinter import *
import tkFont
import webbrowser
from flashcardstudy import help

def open_website(evt):
    webbrowser.open(r"https://github.com/comatory/flashCardStudy")

def open_twitter(evt):
    webbrowser.open(r"https://twitter.com/ondrejsynacek")


def about_window():
        about = Toplevel()
        data = help.author_data()

        about_frame = Frame(about)
        about_frame.grid(row=0, column=0, padx=20, pady=10)

        appname_label = Label(about_frame, text='flashCardStudy ' + 'v' + data['version'], font='-weight bold')
        appname_label.grid(row=0, column=0)

        authorname_label = Label(about_frame, text='programming: ' + data['devname'])
        authorname_label.grid(row=1, column=0)

        twitter_link_label = Label(about_frame, text=data['twitter'], font='-underline True')
        twitter_link_label.grid(row=2, column=0)
        twitter_link_label.bind('<Button-1>', open_twitter)

        website_link_label = Label(about_frame, text=data['web'], font='-underline True')
        website_link_label.grid(row=3, column=0)
        website_link_label.bind('<Button-1>', open_website)

        spacer = Label(about_frame)
        spacer.grid(row=4, column=0)

        thanks_label = Label(about_frame, text='Thanks to:')
        thanks_label.grid(row=5, column=0)

        thankers_label = Label(about_frame, text = data['thanks'])
        thankers_label.grid(row=6, column=0)

        close_button = Button(about_frame, text='Close', command=about.destroy)
        close_button.grid(row=7, column=0)
        
        
