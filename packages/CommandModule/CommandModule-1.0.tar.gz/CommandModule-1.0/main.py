#----------------------------
# modularized command processor
#----------------------------
import os
import Const
import CommandPattern
import Commands
       

class ContextFolder(object):
    def __init__(self,folder):
        self.folder = folder
        
    #Presense of the __call__ method makes this object a callable. Means an instance of the object x can be used as x(original_func)
    def __call__(self, original_func):
        decorator_self = self
        def decorator_function( *args, **kwargs):
            print("setting context dir...")
            backup = os.getcwd()
            os.chdir(decorator_self.folder)
            original_func(*args,**kwargs)
            os.chdir(backup)
        return decorator_function
    


def ListCommandClosure(command, commands_dict):
    """Implements the directory listing command"""
    
    @ContextFolder("/Users/maruthir")
    def execute():
        #assuming second word would be the path
        if len(command.split(sep=" ")) >1 :
            folder_path = command.split(sep=" ")[1]
        else:
            folder_path="."
        files = os.listdir(path=folder_path)
        for file_ in files:
            print(file_)
    return execute

def ListRecursiveCommandClosure(command, commands_dict):
    """Implements the directory listing recursive command"""
    
    def execute ():
        #assuming second word would be the path
        if len(command.split(sep=" ")) >1 :
            folder_path = command.split(sep=" ")[1]
        else:
            folder_path="."
        files = os.listdir(path=folder_path)
        for file_ in files:
            if os.path.isdir(file_):
                print("DIR >>> ",file_) 
                commands_dict["ls"]("ls {}/{}".format(folder_path,file_),commands_dict)()
                print("<<< END DIR")
            else:
                print(file_)
    return execute

def get_command(command):
    commands = {"ls" : ListCommandClosure, "lsr" : ListRecursiveCommandClosure}
    command_name = command.split(sep=" ")[0]
    if command_name in commands :
        return commands[command_name](command,commands)

#--------------------------------------------------------------------------------
    

        

    


    
while True:
    command = input("> ")
    commands = {}
    commands["ls"] = Commands.ListCommand
    commands["pwd"] = Commands.PwdCommand
    commands["exit"] = Commands.QuitCommand
    commands["cd"] = Commands.ChdirCommand
    commands["cp"] = Commands.CopyCommand
    commands["gzip"] = Commands.GzipCommand
    commands["gzipr"] = Commands.GzipRegularCommand
    commands[Const.const.unknown_command] = Commands.UnknownCommand
    cf = CommandPattern.CommandFactory(commands)
    command = cf.get_command(command)
    command.execute()
