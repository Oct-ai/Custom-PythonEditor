import tkinter as tk
from tkinter import filedialog
from tkinter import Text
import subprocess
import threading

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.filename = None
        self.input_queue = []
        self.input_event = threading.Event()
        self.dark_mode = False

        # create a Text widget for the code and pack it into the root window
        self.code_text = Text(root, bg='white', fg='black')
        self.code_text.pack(fill='both', expand=True)

        # create a Text widget for the output and pack it into the root window
        self.output_text = Text(root, bg='white', fg='black')
        self.output_text.pack(fill='both', expand=True)

        # create an Entry widget for the input and pack it into the root window
        self.input_entry = tk.Entry(root, bg='white', fg='black')
        self.input_entry.pack(fill='x')

        # create a button for submitting input and pack it into the root window
        self.input_button = tk.Button(root, text='Submit', command=self.submit_input, bg='white', fg='black')
        self.input_button.pack(fill='x')

        # create a menu with File > Open and File > Save options, and a toggle for dark mode
        self.menu = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label='Open', command=self.open_file)
        self.file_menu.add_command(label='Save', command=self.save_file)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.dark_mode_menu = tk.Menu(self.menu, tearoff=0)
        self.dark_mode_menu.add_command(label='Toggle Dark Mode', command=self.toggle_dark_mode)
        self.menu.add_cascade(label='Appearance', menu=self.dark_mode_menu)
        root.config(menu=self.menu)

        # create a Run button and pack it into the root window
        self.run_button = tk.Button(root, text='Run', command=self.run_code, bg='white', fg='black')
        self.run_button.pack()

    def open_file(self):
        self.filename = filedialog.askopenfilename(filetypes=(('Python files', '*.py'),))
        with open(self.filename, 'r') as f:
            self.code_text.delete('1.0', 'end')
            self.code_text.insert('1.0', f.read())

    def save_file(self):
        if self.filename is None:
            self.filename = filedialog.asksaveasfilename(filetypes=(('Python files', '*.py'),))
        with open(self.filename, 'w') as f:
            f.write(self.code_text.get('1.0', 'end'))

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.root.config(bg='black')
            self.code_text.config(bg='black', fg='white')
            self.output_text.config(bg='black', fg='white')
            self.input_entry.config(bg='black', fg='white')
            self.input_button.config(bg='black', fg='white')
            self.run_button.config(bg='black', fg='white')
        else:
            self.root.config(bg='white')
            self.code_text.config(bg='white', fg='black')
            self.output_text.config(bg='white', fg='black')
            self.input_entry.config(bg='white', fg='black')
            self.input_button.config(bg='white', fg='black')
            self.run_button.config(bg='white', fg='black')


    def submit_input(self):
        # get the input from the Entry widget and append it to the input queue
        user_input = self.input_entry.get()
        self.input_queue.append(user_input)

        # clear the Entry widget and set the input event
        self.input_entry.delete(0, 'end')
        self.input_event.set()



    def run_code(self):
        # get the code from the code Text widget and write it to a temporary file
        code = self.code_text.get('1.0', 'end')
        with open('temp.py', 'w') as f:
            f.write(code)

        # run the temporary file using the Python interpreter and capture the output
        output = subprocess.run(['python', 'temp.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # display the output in the output Text widget
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', output.stdout)

        # check if the code called for input
        if output.stderr == '__input__\n':
            # wait for input to be submitted
            self.input_event.wait()
            self.input_event.clear()

            # get the next item in the input queue and send it as input to the code
            user_input = self.input_queue.pop(0)
            input_bytes = user_input.encode()
            input_proc = subprocess.Popen(['python', 'temp.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            output, _ = input_proc.communicate(input=input_bytes)

            # display the output in the output Text widget
            self.output_text.insert('end', output)
        elif output.returncode != 0:
            # display the error message in the output Text widget
            self.output_text.insert('end', output.stderr)

if __name__ == '__main__':
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()


# create a tkinter root window and an instance of the CodeEditor
root = tk.Tk()
editor = CodeEditor(root)

# start the tkinter event loop
root.mainloop()

