import logging



class CreateData(object):
    __instance__ = None

    def __init__(self):
        if CreateData.__instance__ is None:
            CreateData.__instance__ = self
        else:
            raise Exception("You cannot create another WebFormSocketManager class")

    @staticmethod
    def get_instance():
        if not CreateData.__instance__:
            CreateData()
        return CreateData.__instance__

    def get_chain_of_responsibility(self):
        pass
