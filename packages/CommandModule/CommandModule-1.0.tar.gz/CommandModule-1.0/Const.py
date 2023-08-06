class Const:
    class ConstError(TypeError): 
        pass
    
    def __setattr__(self,name,value):
        if name in self.__dict__:
            raise Const.ConstError("Can't rebind const {}".format(name))
        self.__dict__[name]=value

const = Const()
const.unknown_command = "unknown_command"
