import os
import pandas as pd 
import ipywidgets as widgets
from IPython.display import display


class Labler():
    def __init__(self, path, classes, csv='labels.csv', multiclass=False, autosubmit=True, autosave_interval=1):
        self.__dict__.update(locals())
        self.file = None
        self.labels = {}
        self.files = os.listdir(path)
        self.create_df()
        self.index = len(self.df)
        self.view = LablerView(self)
        self.get_next()

    def create_df(self):
        try:
            self.df = pd.read_csv(os.path.join(self.path, self.csv), index_col='file')
        except FileNotFoundError:
            self.df = pd.DataFrame([], columns=['labels'])
            self.df.index.name = 'file'

    def save_df(self):
        self.update_labels()
        self.df.to_csv(os.path.join(self.path, self.csv))

    def autosave(self):
        if self.autosave_interval > 0 and self.index % self.autosave_interval == 0:
            self.save_df()

    def get_labels(self):
        filename = os.path.basename(self.file.name)
        try:
            labels = self.df.at[filename, 'labels']
            self.labels = {}
            for label in labels.split(" "): self.labels[label] = True
        except KeyError:
            self.labels = {}
    
    def update_labels(self):
        if self.labels:
            filename = os.path.basename(self.file.name)
            labels = ' '.join([ label for label, isTrue in self.labels.items() if isTrue]) 
            self.df.at[filename, 'labels'] = labels
    
    def goto_index(self, index):
        if self.file: self.file.close()
        file = self.files[self.index]
        self.file = open(os.path.join(self.path, file), "rb")
        self.image = self.file.read()
        self.get_labels()
        self.view.refresh()

    def get_next(self):
        self.autosave()
        self.index +=1
        self.goto_index(self.index)

    def get_previous(self):
        self.index -= 1
        self.goto_index(self.index)
    
    def toggle_label(self, label=None, index=None):
        if isinstance(index, int): label = self.classes[index]
        new_labels = {}
        if self.multiclass: new_labels = self.labels
        new_labels[label] = not self.labels.get(label, False)
        self.labels = new_labels
        self.update_labels()
        if not self.multiclass and self.autosubmit: 
            self.get_next()
        else:
            self.view.refresh()
        
    
        


class LablerView():
    def __init__(self, controller):
        self.controller = controller
        self.initialize()

    def initialize(self):
        self.add_buttons()
        self.add_input()
        self.add_previous()
        self.add_next()
        self.add_save()
        self.add_image()
        self.display()

    
    def add_image(self):
        self.image = widgets.Image(width=600, height=400)


    def add_next(self):
        button = widgets.Button(
            button_style='success', 
            tooltip='next',
            icon='arrow-right'  
        )
        def click_button(b):
            elf.controller.get_next()

        button.on_click(click_button)
        self.next = button

    def add_previous(self):
        button = widgets.Button(
            button_style='success',  
            tooltip='previous',
            icon='arrow-left'
        )
        def click_button(b):
            self.controller.get_previous()

        button.on_click(click_button)
        self.previous = button

    def display(self):
        items = [self.input,self.previous,  self.save, self.next]
        for item in items: item.layout.width = '50px'
        nav = widgets.HBox(items)
        nav.layout.justify_content = 'center'
        display(nav)
        self.button_group.layout.justify_content = 'center'
        display(self.button_group)
        image_container = widgets.HBox([self.image])
        image_container.layout.justify_content = 'center'
        image_container.layout.align_items = 'flex-start'
        display(image_container)

    def add_save(self):
        button = widgets.Button(
            button_style='success', 
            tooltip='save to csv',
            icon='save'  # check
        )
        def click_button(b):
            self.controller.save_df()

        button.on_click(click_button)
        self.save = button


    def add_input(self):
        self.input = widgets.Text()
        def on_change(change):
            new = change.new
            if isinstance(new, str) and len(new) and new[-1].isdigit():
                self.controller.toggle_label(index=int(new[-1]))
            self.input.value=''

        def on_submit(*args):
            self.controller.get_next()
                
        self.input.observe(on_change)
        self.input.on_submit(on_submit)
    
    def add_buttons(self):
        self.buttons = []
        for i, label in enumerate(self.controller.classes):
            self.add_button(i, label)
        self.button_group = widgets.HBox(self.buttons)


    def add_button(self, index, label):
        button = widgets.Button(
            description=f'{index} {label}',
            disabled=False,
            button_style='primary',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip=label,
            icon='1'  # check

        )
        controller = self.controller
        def click_button(b):
            controller.toggle_label(label)

        button.on_click(click_button)
        self.buttons.append(button)
    
    def refresh(self):
        self.image.value = self.controller.image
        for button in self.buttons:
            button.button_style = 'warning' if self.controller.labels.get(button.tooltip, False) else 'primary'

