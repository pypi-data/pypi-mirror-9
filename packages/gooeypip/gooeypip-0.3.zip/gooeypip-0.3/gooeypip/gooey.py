from .interpreter import *
from .pypeg2 import *
from .statements import *
from tkinter import *
from tkinter.scrolledtext import *
from tkinter import font
import os.path


class Gooey():
	def __init__(self):
		self.window = GUIWindow()
		self.window.window.withdraw()
		self.interpreter = Interpreter(self.window.window,None,dict())
		self.input_string = ""
		
	def read_file(self, f):
		self.input_string += f.read()

	def read_string(self, s):
		self.input_string += s

	def add_function(self, f):
		b = self.interpreter.makeBinding("function", f.__name__, f)
		self.interpreter.bindings = self.interpreter.addBinding(b)

	def run_input(self, s):
		try:
			ast = parse(s, Program)
			self.interpreter.interpret(ast)
		except SyntaxError as e:
		    print("Syntax error", e)
		    sys.exit(0)
		except GooeyError as gooey_error:
		    print("Oops: ", gooey_error)
		    sys.exit(0)
		self.window.window.mainloop()
		
		

class GUIWindow():
    '''
    Wrapper class for the live preview window
    '''
    def __init__(self):
        '''
        Initializes preview window, bindings, and master window binding.
        '''
        self.window = Tk(className="Live Preview")
        self.window.resizable(width=False, height=False)
        m = Menu(self.window)
        self.window.config(menu=m)

        self.bindings = dict()
        # Keep track of the binding linked to our master window
        self.winBinding = None
        self.is_open = False

    def openWindow(self):
        '''
        Open the preview window.
        '''
        self.is_open = True
        self.window.deiconify()

    def stop(self):
        '''
        Close the preview window.
        '''
        self.is_open = False

    def modify(self, gooeyCode):
        '''
        Takes string Gooey code, parses and interprets it, and updates the preview window.
        Throws SyntaxError if syntax is incorrect, or GooeyError if there is an interpreter error.
        '''
        #create new instance of interpeter class, passing a reference the live preview window
        i = Interpreter(self.window,self.winBinding,self.bindings)

        ast = parse(gooeyCode, Program)

        (self.bindings,self.winBinding) = i.interpret(ast)
        del i


def read(s):
	if os.path.isfile(s):
		try:
			f = open(s, "r")
			g.read_file(f)
		except IOError:
			print("Could not read input file.")
	else:
		g.read_string(s)

def read_lazy(s):
	g.run_input(s)
	

def register_function(func):
	g.add_function(func)

def run():
	g.run_input(g.input_string)

g = Gooey()


		
