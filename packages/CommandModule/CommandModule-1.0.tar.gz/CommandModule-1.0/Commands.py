from _functools import reduce
import datetime
import gzip
import os
import re    

import CommandPattern


def log_time(func):
    def inner(*args, **kwargs):
        start = datetime.datetime.now()
        retval = func(*args, **kwargs)
        end = datetime.datetime.now()
        duration = end - start
        print("Method call {} microseconds".format(duration.microseconds))
        return retval
    return inner


class ListCommand(CommandPattern.Command):
    """Implements the directory listing command"""
    
    def __init__(self,command):
        #assuming second word would be the path
        if len(command.split(sep=" ")) >1 :
            self.folder_path = command.split(sep=" ")[1]
        else:
            self.folder_path="."
        
    def execute(self):
        files = os.listdir(path=self.folder_path)
        for file_ in files:
            print(file_)

class PwdCommand(CommandPattern.Command):
    """Implements the present working directory command"""
    
    def __init__(self, param):
        #this command has no data
        pass
    
    def execute(self):
        print(os.getcwd())

class QuitCommand(CommandPattern.Command):
    """Implements the present working directory command"""
    
    def __init__(self, param):
        #this command has no data
        pass
    
    def execute(self):
        quit()

class UnknownCommand(CommandPattern.Command):
    """Just prints unknown command"""
    
    def __init__(self, param):
        #this command has no data
        pass
    
    def execute(self):
        print("Unknown command")
        
class ChdirCommand(CommandPattern.Command):
    """Implements the present working directory command"""
    
    def __init__(self, command):
        #assuming second word would be the path
        if len(command.split(sep=" ")) >1 :
            self.folder_path = command.split(sep=" ")[1]
        else:
            self.folder_path="."
    
    def execute(self):
        os.chdir(self.folder_path)
        
class CopyCommand(CommandPattern.Command):
    """Implements the a command to copy one or more files"""
    
    def __init__(self, command):
        #assuming second word would be the path
        if len(command.split(sep=" ")) >2 :
            self.source = command.split(sep=" ")[1]
            self.dest_folder = command.split(sep=" ")[2]
        else:
            raise CommandPattern.CommandError("invalid cp syntax. Only works in current directory. Source file pattern can be regex. Usage: cp sourceFilePattern destFolder")
    
    @log_time
    def execute(self):
        files = os.listdir()
        
        file_count = 0
        for file_ in files:
            if os.path.isdir(file_): continue
            match_obj = re.match(self.source,file_)
            if match_obj:
                dest_file = self.dest_folder+"/"+file_
                with open(file_, mode='rb') as source_file, open(dest_file, mode='wb') as dest_file :
                    while True:
                        b = source_file.read()
                        if b:
                            dest_file.write(b)
                        else:
                            file_count+=1
                            break
        print("Copied {} files".format(file_count))
        
class GzipRegularCommand(CommandPattern.Command):
    """Implements the a command to gzip one or more files without using map/reduce/filter"""
    
    def __init__(self, command):
        #assuming second word would be the path
        if len(command.split(sep=" ")) >2 :
            self.source_pattern = command.split(sep=" ")[1]
            self.dest_folder = command.split(sep=" ")[2]
        else:
            raise CommandPattern.CommandError("invalid gzip syntax. Only works in current directory. Source file pattern can be regex. Usage: cp sourceFilePattern destFolder")
    
    @log_time
    def execute(self):
        files = os.listdir()
        process_count =0
        for file_name in files:
            # --- Filter operation ---
            if os.path.isdir(file_name): 
                continue
            match_obj = re.match(self.source_pattern,file_name)
            if not match_obj:
                continue
            # --- Map operation ---
            dest_file_name = os.getcwd()+"/temp/"+file_name+".gz"
            print("Compressing file: {} to {}".format(file_name,dest_file_name))
            with open(file_name, mode='rb') as source_file, gzip.open(dest_file_name, 'wb') as dest_file :
                dest_file.writelines(source_file)
                # --- Reduce operation ---
                process_count+=1
        print("{} files processed.".format(process_count))

class GzipCommand(CommandPattern.Command):
    """Implements the a command to gzip one or more files"""
    
    def __init__(self, command):
        #assuming second word would be the path
        if len(command.split(sep=" ")) >2 :
            self.source = command.split(sep=" ")[1]
            self.dest_folder = command.split(sep=" ")[2]
        else:
            raise CommandPattern.CommandError("invalid cp syntax. Only works in current directory. Source file pattern can be regex. Usage: cp sourceFilePattern destFolder")
    
    @log_time
    def execute(self):
        files = os.listdir()
        files_for_compress = filter(get_filter_function(self.source),files)
        status_elements = map(compress,files_for_compress)
        process_count = reduce(count, status_elements)
        print("{} files processed.".format(process_count))
        

def count(x,y):
    if(type(x)==bool.__class__):
        return 1
    else:
        return x+1
        
def compress(source_file_name):
    dest_file_name = os.getcwd()+"/temp/"+source_file_name+".gz"
    #print("Compressing file: {} to {}".format(source_file_name,dest_file_name))
    with open(source_file_name, mode='rb') as source_file, gzip.open(dest_file_name, 'wb') as dest_file :
        dest_file.writelines(source_file)
    return True
        
def get_filter_function(pattern):
    def pattern_filter(file_name):
        if os.path.isdir(file_name): 
            return False
        match_obj = re.match(pattern,file_name)
        if match_obj:
            return True
        else:
            return False
    return pattern_filter