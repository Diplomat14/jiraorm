from jira.resources import Sprint

class SprintExt(object):
    
    __sprint = None
    __container = None
    

    def __init__ ( self, original : Sprint, container ):
        self.__sprint = original
        self.__container = container

    @property
    def original(self):
        return self.__sprint

    @property
    def name(self):
        return self.__sprint.name

    @classmethod
    def getSprintFromRawStringWithId(cls,rawdata,container):
        assert isinstance(rawdata, str), "rawdata parameter shall be string. " + str(type(rawdata)) + " given."
        # Didn't manage to do it with built-in available methods as returned raw data is not a valid JSON string.
        # That is why jsut parsing id to use internal simpl emethod to get it. Not using regexp to be a bit faster may be
        id = None
        sprintExt = None

        idpos = rawdata.index('id=')
        commapos = rawdata.index(',',idpos)
        if idpos > 0 and commapos > 0 and idpos < commapos:
            id = int(rawdata[idpos+3:commapos])

        if id != None:
            sprintExt = container.getSprintById(id)
        
        return sprintExt

        

    