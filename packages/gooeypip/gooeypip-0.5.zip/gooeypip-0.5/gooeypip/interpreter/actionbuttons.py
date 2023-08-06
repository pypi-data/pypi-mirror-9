from tkinter import *




# Print something actions
#def write(printTest):
def write(window, item):
    printTest = item.action.arguments
    print(printTest)
    #return (window, item)

# Close window actions
#def close(window):
def quit(window, item):
    window.quit()
    #return (window, item)

# Change color of window actions
#def windowColorChange(window, c):
def windowColorChange(window,item):
    c = item.action.arguments
    window.configure(bg= c)
    #return (window,item)

## Changes size of window
#def windowSizeChange(window, item):
#    c = item.action.size
#    if c.lower() == "large":
#        window.geometry('600x600')
#    elif c.lower() == "medium":
#        window.geometry('400x400')
#    elif c.lower() == "small":
#        window.geometry('200x200')

def findAction(item):
    action = str(item.action.funcname)
    #a = "%s(window,item)" % action
    #print(a)
    #a = "Actions.%s(window,item)" % action
    a = "%s" % action
    return a

def findMenuAction(item):
    action = str(item.action)
    a = "%s" % action
    return a

def callAction(window,item,action):
    print("calling action")

    # print(locals())
    # print(globals())
    exec(action+"(window,item)")

def checkActions(action):
    actionList = ['write','quit','windowColorChange','windowSizeChange']
    if action not in actionList:
        return False
    else:
        return True


    # Submit button

    # Main method which goes through all other methods?  Maybe?
    # def callToAction(type):
    # Nevermind, won't work, still need to make action part of statement
