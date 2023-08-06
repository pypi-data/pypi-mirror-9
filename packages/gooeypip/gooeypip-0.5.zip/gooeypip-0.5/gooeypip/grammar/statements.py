from ..pypeg2 import *
from .attributes import *
#Starts with a lowercase letter, can only be one word long,
#only contain letters, numbers, or underscore

varnameRegex = re.compile('[a-z][A-Za-z\d\_]*')

class VarName(str):
    grammar = varnameRegex

class MakeType(Keyword):
    grammar = Enum(K("Button"), K("Window"), K("Menu"), K("MenuItem"), K("TextBox"), K("Text"), K("Image"), K("Checkboxes"), K("RadioButtons"), K("FormattedText"))

class Make(List):
    #grammar = "make", blank, attr("type", MakeType), blank, attr("varname", VarName), optional("with", attr("attributes",AttributeList)), "."
    grammar = "make", blank, attr("type", MakeType), blank, attr("varname", VarName), optional(blank, "with", blank, attr("attributes",AttributeList))

class GooeySet(List):
    #grammar = "set", blank, attr("varname", VarName), attr("attributes",AttributeList), "."

     grammar = "set", blank, attr("varname", VarName), attr("attributes",AttributeList)

class Return(List):
    grammar = "return", optional(blank, attr("param", word))

class Line(List):
    grammar = attr("lineAction", [Make, GooeySet]), ";", blank

class LastLine(List):
    grammar = attr("lineAction", [Make, GooeySet, Return])

class FunctionDefinition(List):
    # grammar = "function", blank, attr("funcname", VarName), "(", attr("params", \
    # csl(maybe_some(word))), ")", blank, "does", blank, attr("funcaction", csl(maybe_some(word))), ";", \
    # blank, optional("returns", blank, word), "."
    # grammar = "function", blank, attr("funcname", VarName), "(", attr("params", \
    # csl(maybe_some(word))), ")", blank, "does", blank, attr("funcaction", csl(maybe_some(word))), "."
    # grammar = "function", blank, attr("funcname", VarName), "(", attr("params", \
    # csl(maybe_some(word))), ")", blank, "does", blank, attr("funcaction", [Make, GooeySet])
    grammar = "function", blank, attr("funcname", varnameRegex), "(", attr("params", csl(maybe_some(varnameRegex))), ")", blank, "does", blank, attr("funcaction", csl(maybe_some(Line), blank, LastLine))

class FunctionCall(List):
    # TODO: change this syntax
    grammar = "run", blank, attr("funcname", VarName), "(", attr("params", csl(maybe_some([QuotedText, varnameRegex, intRegex]))), ")", optional(blank, "as", blank, attr("returnTo", VarName))


class Program(List):
    grammar = maybe_some([Make, GooeySet, FunctionDefinition, FunctionCall], ".")
    #grammar = maybe_some([FunctionDefinition,FunctionCall,InstructionLine])
