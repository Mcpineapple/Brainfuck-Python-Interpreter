from tkinter import * #the graphic interface shall be built with tkinter
from tkinter import ttk #tkinter module imported to create tabs within the tkinter interface
import waiting
from threading import Thread # used with waiting, allows interpreter to run alongside interface without problems



class bf_gui :

    """Initialising this class opens the graphic interface."""

    def __init__(self):
        self.root = Tk()

        self.root.title("Brainfuck Interpreter")

        self.tabs = ttk.Notebook(self.root) # allows us to use tabs

        self.frame_code = Frame(self.root) # this frame shall be the tab storing the widgets allowing us to code a brainfuck program within the interface
        self.frame_code.pack()

        self.import_code = Frame(self.root) # this frame shall be the tab allowing us to run a brainfuck file
        self.import_code.pack()

        self.output_frame = Frame(self.root) #this frame shall be the tab containing the output widgets
        self.output_frame.pack()

        """"Adding each frame to the notebook to create tabs."""
        self.tabs.add(self.frame_code, text='Write Code')
        self.tabs.add(self.import_code, text='Execute File')
        self.tabs.add(self.output_frame, text='Output')

        """Configuring coding tab"""

        self.code_input = Text(self.frame_code, height = 20, width = 50) #text box widget to code in
        self.code_input.pack()

        """Implementing a scrollbar within the textbox to allow long codes"""
        self.sb = Scrollbar(self.frame_code) #scrollbar widget
        self.sb.pack(side=RIGHT, fill=BOTH)
        self.code_input.config(yscrollcommand=self.sb.set)
        self.sb.config(command=self.code_input.yview)

        self.code_run = Button(self.frame_code, text="Run", command=self.interpret_code) #button widget to run the program
        self.code_run.pack()

        """Configure opening file tab"""

        self.file_path = Entry(self.import_code, width=40) #enter the file path in the widget
        self.file_path.pack()

        self.open_code_widg = Button(self.import_code, text="Open BF file.", command=self.open_code) # button to open and run the file
        self.open_code_widg.pack()


        """Configuring output tab"""

        self.input_info_bool = False #bool variable to check if an input is needed
        self.input_info_text = StringVar() #stringvar is used to modify label text
        self.input_info = Label(self.output_frame, textvariable=self.input_info_text) #tells user if an input is needed
        self.input_info.pack()
        self.input_info_text.set("No input needed.")

        self.input_entry = Entry(self.output_frame, width=1) #entry for user input (when ',' is in the program)
        self.input_entry.pack()
        self.input_valid = Button(self.output_frame, text='OK', command=self.input_manage) #button to validate entry
        self.input_valid.pack()

        self.output_text = StringVar()
        self.output_widget = Label(self.output_frame, textvariable=self.output_text) # label containg the output of the program
        self.output_widget.pack()
        self.output_text.set("")


        self.tabs.pack(expand=1, fill="both")
        self.root.mainloop()


    def open_code(self):
        path = self.file_path.get()
        file = open(path, "rt") # since the brainfuck file, no matter what extension it has, should be in clear text, opening it as a text file is fine
        text = file.read()
        file.close()
        def program():
            self.output_text.set(self.interpret(text))
        thread = Thread(target=program) #using a thread prevents problems conflicts between the interpreter and the interface by dividing them
        thread.start()

    def interpret_code(self):
        def program():
            self.output_text.set(self.interpret(self.code_input.get("1.0","end")))
        thread = Thread(target=program)
        thread.start()


    def interpret(self,text):
        array = [0] * 30000
        pointer = 0 # data pointer
        instr_pointer = 0 #intruction pointer
        repeat = [] #used to store location of brackets for the loops
        text_output = "Output : \n"

        while instr_pointer < len(text) - 1:

            if text[instr_pointer] == '[':
                repeat.append(instr_pointer)
                if array[pointer] == 0:
                    proceed = [True, len(repeat)]
                    while proceed[0] and instr_pointer < len(text) -1:
                        """Moves intruction pointer to the matching bracket if the data pointer is 0 """
                        instr_pointer += 1
                        if text[instr_pointer] == '[':
                            repeat.append(instr_pointer)
                        elif text[intr_pointer] == ']':
                            if len(repeat) == proceed[1]:
                                proceed[0] = False
                            proceed.pop()


                    instr_pointer += 1
                else :
                    instr_pointer += 1

            elif text[instr_pointer] == ']':
                if array[pointer] != 0:
                    while instr_pointer != repeat[-1]:
                        """Moves instruction pointer to matching bracket if data pointer is nonzero."""
                        instr_pointer -=1
                    instr_pointer += 1

                else :
                    repeat.pop()
                    instr_pointer += 1

            elif text[instr_pointer] == '>':
                """Increment data pointer."""
                if pointer == 29999:
                    """Cycles back to the beginning at the end of the array. Doesn't seem to be the standard way brainfuck works but whatever."""
                    pointer = 0
                else:
                    pointer += 1
                instr_pointer += 1

            elif text[instr_pointer] == '<':
                """Decrement data pointer."""
                if pointer == 0:
                    """Cycles to the end at the beginning of the array."""
                    pointer = 29999
                else:
                    pointer -= 1
                instr_pointer +=1

            elif text[instr_pointer] == '+':
                """Increment byte at data pointer."""
                if array[pointer] == 255:
                    array[pointer] = 0
                else:
                    array[pointer] += 1
                instr_pointer += 1

            elif text[instr_pointer] == '-':
                """Decrement byte at data pointer."""
                if array[pointer] == 0:
                    array[pointer] = 255
                else:
                    array[pointer] -= 1
                instr_pointer += 1

            elif text[instr_pointer] == '.':
                """Output byte as ASCII."""
                if array[pointer] >= 0:
                    text_output += chr(array[pointer])
                instr_pointer += 1

            elif text[instr_pointer] == ',':
                """Accepts one byte of input. Requires interaction with Graphic interface, this is the part where threading became necessary."""
                self.input_info_text.set('Input needed.')
                self.input_info_bool = True
                waiting.wait(self.input_ready,timeout_seconds=120) #waits for user to input a character, 2 min timeout
                self.input_info_text.set('No input needed.')
                array[pointer] = ord(self.input_entry.get())
                self.input_entry.delete(0,'end')
                instr_pointer += 1

            else:
                instr_pointer+=1 #increment intruction pointer

        return text_output #return output 

    def input_manage(self):
        """Pressing on the input button (OK) in the output tab sets the bool to false, informing the program that a character has been inputted, allowing it to proceed"""
        self.input_info_bool = False

    def input_ready(self):
        """Used by the interpreter to check if the bool is false or not (if the user has inputted a char"""
        return not(self.input_info_bool)






if __name__ == '__main__':
    bf = bf_gui() #launch program
