from .interpreter import interpreter
from .pypeg2 import *
from .grammar import statements
from tkinter import *
import os.path


class Gooey():
	def __init__(self):
		self.window = GUIWindow()
		self.window.window.withdraw()
		self.interpreter = interpreter.Interpreter(self.window.window,None,dict())
		self.input_string = ""
		
	def read_file(self, f):
		self.input_string += f.read()

	def read_string(self, s):
		self.input_string += s

	def add_function(self, f):
		b = self.interpreter.makeBinding("function", f.__name__, f)
		self.interpreter.bindings = self.interpreter.addBinding(b)
		
	def get_component(self,v):
		c = self.interpreter.get_by_varname(v)
		return c

	def run_input(self, s):
		try:
			ast = parse(s, statements.Program)
			self.interpreter.interpret(ast)
			self.input_string = ""
		except SyntaxError as e:
		    print("Syntax error", e)
		    sys.exit(0)
		except interpreter.GooeyError as gooey_error:
		    print("Oops: ", gooey_error)
		    sys.exit(0)
		self.window.window.mainloop()
		
	def update(self,s):
		try:
			ast = parse(s, statements.Program)
			self.interpreter.interpret(ast)
			self.input_string = ""
			return True
		except SyntaxError as e:
		    print("Syntax error", e)
		    sys.exit(0)
		except interpreter.GooeyError as gooey_error:
		    print("Oops: ", gooey_error)
		    sys.exit(0)
		self.window.window.mainloop()

class GUIWindow():
    def __init__(self):
        self.window = Tk(className="Live Preview")
        self.window.resizable(width=False, height=False)
        m = Menu(self.window)
        self.window.config(menu=m)


def read(s):
	if os.path.isfile(s):
		try:
			f = open(s, "r")
			g.read_file(f)
		except IOError:
			print("Could not read input file.")
	else:
		g.read_string(s)

	
def get(varname):
	c = g.get_component(varname)
	if c:
		return c
	else: 
		print(varname, "undefined")
		return False
		
def update(s):
	if os.path.isfile(s):
		try:
			f = open(s, "r")
			g.update(f.read())
			return True
		except IOError:
			print("Could not read input file.")
			return False
	else:
		g.update(s)
		return True
	

def register_function(func):
	g.add_function(func)

def run():
	g.run_input(g.input_string)

g = Gooey()


		
