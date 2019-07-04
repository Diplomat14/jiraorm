import pickle
from pickle import Pickler
from pickle import Unpickler
from pickle import HIGHEST_PROTOCOL

from jira.resources import Board

from jira import JIRA

class JSWPickler(Pickler):
    def persistent_id(self, obj):
        if isinstance(obj, JIRA):
            return ("JIRA", None)
        if isinstance(obj,Board):
            return ("jira.resources.Board", None)
        else:
            # If obj does not have a persistent ID, return None. This means obj
            # needs to be pickled as usual.
            return None

class JSWUnpickler(Unpickler):

    def persistent_load(self, pid):

        type_tag, key_id = pid
        if type_tag == "JIRA":
            return None
        if type_tag == "jira.resources.Board":
            return None
        else:
            # Always raises an error if you cannot return the correct object.
            # Otherwise, the unpickler will think None is the object referenced
            # by the persistent ID.
            raise pickle.UnpicklingError("unsupported persistent object")



class JSWPersistence (object):

    __filepath = ""

    def __init__(self, filepath = "pickeledcontainer"):
        assert isinstance(filepath, str), "filepath shall be a string"
        self.__filepath = filepath

    def pickle(self,container):
        #assert isinstance(container,JSWContainer), "only container class shall be pickled"
        file = open(self.__filepath,"wb")
        p = JSWPickler(file,HIGHEST_PROTOCOL)
        p.dump(container)
        file.close()

    def unpickle(self):
        #return None
        try:
            file = open(self.__filepath, "rb")
            up = JSWUnpickler(file)
            c = up.load()
            file.close()
            # assert isinstance(c, JSWContainer), "only container class shall be unpickled"
            return c
        except Exception as e:
            return None