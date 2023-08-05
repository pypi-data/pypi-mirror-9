import os
from Tkinter import * 
import tkFont
import display
import about
from flashcardstudy import sfile
from flashcardstudy import stack 
from flashcardstudy import card
import config
from about import open_website
from config import default_directory, check_conf_file, check_datadir, ConfigurationFile

### GUI FUNC

def flashCardStudyGUI():

    # Check & create conf file
    def check_user_data():
            try:
                    if not check_conf_file():
                            print "conf file doesn't exist"
                            conf_file = ConfigurationFile()
                            os.makedirs(conf_file.defaultdir, 0777)
                            f = open(os.path.join(conf_file.defaultdir, conf_file.filename), 'w')
                            f.close()
                            print "conf file created: ", conf_file
                            conf_file.write_datadir()
                            print "data dir written:", conf_file.datadir
                    else:
                            print "conf file exists!"
            except IOError:
                    print "you don't have permission to read target folder"

    check_user_data()

    # Reads data directory for flashcards
    def get_default_path():
            print "user dir retrieved"
            return check_datadir()
            
    # Main window
    root = Tk()
    root.title("flashCardStudy")

    # Stack reorder icons
    icon_up_base64 = '''\
        R0lGODlhEAAQAJEAAAAAAP///////wAAACH5BAEAAAIALAAAAAAQABAAAAIflI+pywfQ
0ovuQWpvy3PzyHVKKErkQlpjqhmsSsVRAQA7
'''
    icon_down_base64 = '''\
        R0lGODlhEAAQAJEAAAAAAP///////wAAACH5BAEAAAIALAAAAAAQABAAAAIdlI+pq+AP
XYqx0bcuYJpTZnygOGJgaJ6CpKLtCxcAOw==
'''

    icon_up = PhotoImage(data=icon_up_base64)
    icon_down = PhotoImage(data=icon_down_base64) 

    card_warning = "Click '+' to add cards"
    stack_warning = "Click '+' to add a stack"

    # Checker funcs

    def stack_sel():
            return int(stack_browser.curselection()[0])

    def card_sel():
            return int(stack_browser.curselection()[0]), int(card_browser.curselection()[0])

    def check_stacks():
            if stack_browser.size() == 0:
                    stack_browser.insert(0, stack_warning)

    def cb_check():
            if wildcard.get():
                    randomize_cards_checkbutton.config(state=DISABLED)
                    randomize_stacks_checkbutton.config(state=DISABLED)
            elif random_cards.get() or random_stacks.get():
                    wildcard_checkbutton.config(state=DISABLED)
            else:
                    randomize_cards_checkbutton.config(state=NORMAL)
                    randomize_stacks_checkbutton.config(state=NORMAL)
                    wildcard_checkbutton.config(state=NORMAL)


    # Stack browser
    stack_view = LabelFrame(root, text="Stacks")
    stack_view.grid(row=0, column=0, padx=5)

    stack_browser = Listbox(selectmode=EXTENDED, activestyle="dotbox", exportselection=0)

    def refresh_files():
            files = sfile.read_stack_files(sfile.lookup_stack_files(dir=get_default_path()))
            files.sort()
            return files

    def refresh_stacks(files):
            stack_browser.delete(0, END)
            for a_stack in files:
                    stack_browser.insert(a_stack[0], a_stack[1])
                    print "Stack file detected: ", a_stack 

    def refresh_cards(files):
            card_browser.delete(0, END)
            for cards in files[int(stack_browser.curselection()[0])][2]:
                    card_browser.insert(cards[0], (cards[1], cards[2]))

    def delete_stk_files(evt):
            list_of_files = []
            for index in stack_browser.curselection():
                    a_file = stack_browser.get(index)
                    list_of_files.append(a_file)
            stack.delete_stack_file(gui=True, filenames=list_of_files)
            stack.renumber_stacks(refresh_files())
            refresh_stacks(refresh_files())

    def delete_cards(evt):
            stack_browser_select = stack_browser.curselection()[0]
            list_of_cards = []
            for index in card_browser.curselection():
                    list_of_cards.append(index)
                    #print "Removing %d items" % len(list_of_cards[int(index)])
            
            card.delete_card(refresh_files(), gui=True, stack_index=stack_browser.curselection()[0], card_index=list_of_cards)
            refresh_cards(refresh_files())
            refresh_stacks(refresh_files())
            binds()
            stack_browser.selection_set(stack_browser_select)

    def send_to_display(evt):
            contents = []
            for selected_stack in stack_browser.curselection():
                    contents.append(refresh_files()[int(selected_stack)])

            contents.sort()
            display.session(contents, random_cards.get(), random_stacks.get(), flip_cards.get(), wildcard.get())

    def select_all_stacks():
            stack_browser.selection_set(0,END)
            card_browser.delete(0,END)

    def move_stack_up():
        new_selection = stack_sel() - 1
        stack.move_stack_gui(refresh_files(),stack_sel())
        refresh_stacks(refresh_files())
        binds()
        stack_browser.activate(new_selection)
        stack_browser.selection_set(new_selection)


    def move_stack_down():
        new_selection = stack_sel() + 1
        stack.move_stack_gui(refresh_files(), stack_sel(), up=False)
        refresh_stacks(refresh_files())
        binds()
        stack_browser.activate(new_selection)
        stack_browser.selection_set(new_selection)

    refresh_stacks(refresh_files())

    stack_browser.grid(row=0, column=0, in_=stack_view, padx=3, pady=2)

    # Stack buttons
    stack_buttons = Frame(stack_view)
    stack_buttons.grid(row=1, column=0, pady=1, sticky=W)

    stack_add_button = Button(text="+")
    stack_add_button.grid(row=0, column=0, in_=stack_buttons)
    stack_remove_button = Button(text="-")
    stack_remove_button.grid(row=0, column=1, in_=stack_buttons)
    stack_move_up_button = Button(image = icon_up, command=move_stack_up)
    stack_move_up_button.grid(row=0, column=2, in_=stack_buttons)
    stack_move_down_button = Button(image = icon_down, command=move_stack_down)
    stack_move_down_button.grid(row=0, column=3, in_=stack_buttons)
    stack_sel_all_button = Button(text="All", command=select_all_stacks)
    stack_sel_all_button.grid(row=0, column=4, in_=stack_buttons, sticky=E)

    # Edit stacks window
    def edit_stack_window(evt, files=None):

            window = Toplevel()
            entry_name = Entry(window)
            entry_name.grid(row=0,column=0,in_=window, padx=5, pady=(2,0))
            button_frame = Frame(window)
            button_frame.grid(row=1, column=0, sticky=E, pady=(7,2), padx=(0,5))
            cancel_button = Button(button_frame, text="Cancel")
            cancel_button.grid(row=1,column=0, in_=button_frame)
            ok_button = Button(button_frame,text="OK")
            ok_button.grid(row=1,column=1, in_=button_frame)
            cancel_button.configure(command=window.destroy)

            entry_name.focus_set()

            def get_entry():
                    new_stack_name = str(entry_name.get())
                    stack_id = stack_browser.size() + 1
                    stack.new_stack_file(gui=True, filename=new_stack_name, fileid=stack_id)
                    stack.renumber_stacks(refresh_files())
                    refresh_stacks(refresh_files())
                    binds()
                    window.destroy()
                    card_browser.delete(0, END)
                    card_browser.insert(0, card_warning)
                    stack_browser.selection_set("end")

            def rename_stack():
                    former_selection = stack_sel()
                    print "Renaming ", '"/' + refresh_files()[stack_sel()][1] + '"/ ... '
                    stack.rename_stack_name(refresh_files()[stack_sel()], entry_name.get())
                    refresh_stacks(refresh_files())
                    binds()
                    window.destroy()
                    stack_browser.select_set(former_selection)

            if files:
                    w = evt.widget
                    index = w.curselection()[0]
                    stack_name = files[int(index)][1]
                    window.title("Edit stack "+"\""+str(stack_name)+"\"")
                    entry_name.insert(0,stack_name)
                    ok_button.configure(command=rename_stack)
            else:
                    window.title("Add new stack")
                    new_stack_name = str(entry_name.get())
                    ok_button.configure(command=get_entry)


    # Card browser

    card_view= LabelFrame(root, text="Cards")
    card_view.grid(row=0, column=1, padx=5)

    card_browser= Listbox(selectmode=EXTENDED, exportselection=0)
    card_browser.insert(0, "<- Select stack")
    card_browser.grid(row=0, column=0, in_=card_view, padx=3, pady=2)

    def select_all_cards():
            card_browser.selection_set(0,END)

    def selectlistbox(evt, files):
            try:
                    card_browser.delete(0, END)
                    w = evt.widget
                    index = w.curselection()[0]
                    if len(w.curselection()) > 1:
                            card_browser.delete(0, END)
                    else:
                            selected_stack = files[int(index)]
                            if len(selected_stack[2]) == 0:
                                    card_browser.insert(0, card_warning)

                            for cards in selected_stack[2]:
                                    card_browser.insert(cards[0], (cards[1], cards[2]))
            except TypeError:
                    card_browser.insert(0, card_warning)

    def move_card_up():
            new_selection = card_sel()[1] - 1 
            card.move_card_gui(refresh_files(), card_sel()[0], card_sel()[1])
            refresh_cards(refresh_files())
            binds()
            card_browser.selection_set(new_selection)
            card_browser.activate(new_selection)

    def move_card_down():
            new_selection = card_sel()[1] + 1 
            card.move_card_gui(refresh_files(), card_sel()[0], card_sel()[1], up=False)
            refresh_cards(refresh_files())
            binds()
            card_browser.selection_set(new_selection)
            card_browser.activate(new_selection)

    card_buttons = Frame(card_view)
    card_buttons.grid(row=1, column=0, pady=1, sticky=W)

    card_add_button = Button(text="+")
    card_add_button.grid(row=0, column=0, in_=card_buttons)
    card_remove_button = Button(text="-")
    card_remove_button.grid(row=0, column=1, in_=card_buttons)
    card_move_up_button = Button(image=icon_up, command=move_card_up)
    card_move_up_button.grid(row=0, column=2, in_=card_buttons)
    card_move_down_button = Button(image=icon_down, command=move_card_down)
    card_move_down_button.grid(row=0, column=3, in_=card_buttons)
    card_sel_all_button = Button(text="All", command=select_all_cards)
    card_sel_all_button.grid(row=0, column=4, in_=card_buttons, sticky=E)


    # Options
    options = LabelFrame(root, text="Options")
    options.grid(row=1, column=0, padx=5, pady=5, sticky=W)
    random_cards = IntVar() 
    random_stacks = IntVar() 
    flip_cards = IntVar() 
    wildcard = IntVar()

    randomize_cards_checkbutton = Checkbutton(text="Randomize cards", variable=random_cards, command=cb_check)
    randomize_stacks_checkbutton = Checkbutton(text="Randomize stacks", variable=random_stacks, command=cb_check)
    wildcard_checkbutton = Checkbutton(text="Wildcard", variable=wildcard, command=cb_check)
    flip_cards_checkbutton = Checkbutton(text="Flip cards", variable=flip_cards)

    randomize_cards_checkbutton.grid(row=0, column=0, in_=options, sticky=W)
    randomize_stacks_checkbutton.grid(row=1, column=0,in_=options, sticky=W)
    wildcard_checkbutton.grid(row=2, column=0, in_=options, sticky=W)
    flip_cards_checkbutton.grid(row=3, column=0, in_=options, sticky=W)

    # Main Buttons
    main_buttons = Frame(root)
    main_buttons.grid(row=1, column=1, rowspan=3, padx=5, pady=5, sticky=SE)
    start_button = Button(text="Start")
    start_button.grid(row=0, column=1,in_=main_buttons)

    def binds():
            stack_browser.bind('<<ListboxSelect>>', lambda evt, arg=refresh_files():selectlistbox(evt, arg))
            stack_browser.bind('<Double-1>', lambda evt, arg=refresh_files():edit_stack_window(evt, arg))
            card_browser.bind('<Double-1>', lambda evt, arg=refresh_files():edit_card_window(evt, arg))
            stack_add_button.bind('<Button-1>', edit_stack_window)
            stack_remove_button.bind('<Button-1>', delete_stk_files) 
            card_add_button.bind('<Button-1>', lambda evt:edit_card_window(evt))
            card_remove_button.bind('<Button-1>', delete_cards)
            start_button.bind('<Button-1>', send_to_display)

    # Edit cards window
    def edit_card_window(evt, files=None):

            w = evt.widget
            window = Toplevel()
            entry_frame = Frame(window)
            entry_frame.grid(row=0, column=1, padx=2,pady=(2,5))

            stack_browser_select = stack_browser.curselection()[0]

            side1_label = Label(entry_frame,text="Side 1:")
            side1_label.grid(row=0, column=0)
            card_side1 = Entry(entry_frame)
            card_side1.grid(row=0, column=1)
            side2_label = Label(entry_frame,text="Side 2:")
            side2_label.grid(row=1, column=0)
            card_side2 = Entry(entry_frame)
            card_side2.grid(row=1, column=1)

            card_side1.focus_set()

            button_frame = Frame(window)
            button_frame.grid(row=1, column=1, sticky=E, pady=(7,2), padx=(0,5))
            cancel_button = Button(button_frame, text="Cancel")
            cancel_button.grid(row=1,column=0, in_=button_frame)
            ok_button = Button(button_frame,text="OK")
            ok_button.grid(row=1,column=1, in_=button_frame)
            cancel_button.configure(command=window.destroy)

            def add_cards(evt):
                    former_selection = stack_sel() 
                    files = refresh_files()
                    cards = card_side1.get(), card_side2.get()
                    print "Side one: ", cards[0]
                    print "Side two: ", cards[1]
                    card.add_card(files=files, cards=cards, index=stack_browser_select, gui=True)
                    refresh_cards(refresh_files())
                    refresh_stacks(refresh_files())
                    binds()
                    window.destroy()
                    stack_browser.selection_set(stack_browser_select)

            def update_cards():
                    former_selection = stack_sel() 
                    cards = card_side1.get(), card_side2.get()
                    print "Changing cards: ", str(refresh_files()[card_sel()[0]][2][card_sel()[1]]) + ' ... '
                    card.modify_card(refresh_files(), gui=True, cards=cards, index=card_sel())
                    refresh_cards(refresh_files())
                    binds()
                    window.destroy()
                    stack_browser.select_set(former_selection)

            if files:
                    index = card_browser.curselection()[0]
                    cards = files[int(stack_browser_select)][2][int(index)][1:3]

                    window.title("Edit cards")
                    card_side1.insert(END,cards[0])
                    card_side2.insert(END,cards[1])
                    ok_button.configure(command=update_cards)

            else:
                    window.title("Add cards")
                    ok_button.bind('<Button-1>', lambda evt:add_cards(evt))


    def quit_program():
        root.destroy()

    # Menus
    menu = Menu(root)
    root.config(menu=menu)
    filemenu = Menu(menu)

    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Exit", command=quit_program)

    helpmenu = Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="Website", command=lambda evt=None: open_website(evt))
    helpmenu.add_separator()
    helpmenu.add_command(label="About", command=about.about_window)


    binds()
    check_stacks()
    root.resizable(0,0)
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()

