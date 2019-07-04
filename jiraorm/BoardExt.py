from jira.resources import Board

class BoardExt(object):
    __id = None
    __name = None
    __board = None
    __container = None
    __cfgDict = None

    def __init__ ( self, original : Board, container ):
        self.__board = original
        self.__id = self.__board.id
        self.__name = self.__board.name
        self.__container = container
        self.__initConfig()


    def __initConfig(self):
        self.__cfgDict = self.__container.getJIRA().get_json_by_uri('board/' + str(self.__id) + '/configuration')

    @property
    def original(self, reload = True):
        if self.__board == None:
            self.__board = self.__container._creatorFromServer.createBoardFromServer(self.__id, self.__name)
        return self.__board

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def config(self):
        return self.__cfgDict

    @property
    def configColumns(self):
        return self.__cfgDict['columnConfig'];

    def setConfigColumns(self,newCfgDict):
        self.__cfgDict['columnConfig'] = newCfgDict
        return self.__container.getJIRA().update_board(self.__board.id,'columns', newCfgDict)
    