import Const
class CommandFactory:
    """A factory of command objects"""
    
    def __init__(self, commands_dict):
        self.commands = commands_dict
        
        
    def get_command(self,command):
        #extract first word that will be the command name
        command_name = command.split(sep=" ")[0]
        if command_name in self.commands :
            return self.commands[command_name](command)
        else:
            return self.commands[Const.const.unknown_command](command)
        
class Command:
    """Command interface that establishes a contract for all commands"""
    def __init__(self, command):
        raise NotImplementedError( "Cannot create an instance of the interface" )
    
    def execute(self):
        raise NotImplementedError( "{} should implement the execute method".format(self.__class__) )
    
class CommandError(Exception):
    """Used to indicate errors in any kind of command processing"""
    def __init__(self, arg):
        self.arg = arg
