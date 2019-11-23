from collections.abc import Iterable

from xdev.core.logger import logger
from .BasicConfig import ConnectionConfig
from .BasicConfig import SecurityConfig
from .JIRAExt import JIRAExt
from .IssueExt import IssueExt
from .EpicExt import EpicExt
from .SprintExt import SprintExt
from .BoardExt import BoardExt

from jira.resources import GreenHopperResource
from jira.resources import Issue
from jira.resources import Sprint
from jira.resources import Board

import ast
from datetime import datetime

class JSWContainer (object):

    # Utility classes
    __creatorFromOriginal = None
    __creatorFromServer = None
    __logger = None

    # Key configuration
    __connectionConfig = None
    __securityConfig = None
    __useMultithreading = False
    __poolSize = 0

    # Dynamic data
    __jiraExt = None
    __issuesExtId = {}
    __issuesExtKey = {}
    __sprintsExt = {}
    __boardsExt = {}

    def __init__(self, iLogger:logger, iConnectionCfg : ConnectionConfig, iSecurityCfg : SecurityConfig):
        assert isinstance(iLogger, logger)
        assert isinstance(iConnectionCfg, ConnectionConfig)
        assert isinstance(iSecurityCfg, SecurityConfig)

        assert iConnectionCfg != None, "Connection configuration shall be set. None given."
        assert iSecurityCfg != None, "Security configuration shall be set. None given."

        self.__logger = logger.from_parent(str(type(self)),iLogger)
        self.__connectionConfig = iConnectionCfg
        self.__securityConfig = iSecurityCfg

        self.__creatorFromServer = JSWContainerCreatorFromServer(self.__logger, self.__securityConfig, self.__connectionConfig, self)
        self.__creatorFromOriginal = JSWContainerCreatorFromOriginal(self.__logger, self)

    @property
    def _creatorFromOriginal(self):
        return self.__creatorFromOriginal

    @property
    def _creatorFromServer(self):
        return self.__creatorFromServer

    @property
    def connectionConfig(self):
        return self.__connectionConfig

    @property
    def securityConfig(self):
        return self.__securityConfig

    def getJIRA(self):
        return self.__creatorFromServer.getJIRA()

    def getIssueFromOriginal(self, original:Issue, date):
        if not original:
            return None
        else:
            assert hasattr(original,'id'), "original shall have id attribute"
            id = int(original.id)
            key = original.key
            created = original.fields.created
            if not date or datetime.strptime(created,'%Y-%m-%dT%H:%M:%S.%f%z').date() < datetime.strptime(date, '%Y-%m-%d').date():
                if id not in self.__issuesExtId:
                    self.__issuesExtId[id] = self.__creatorFromOriginal.createIssueFromOriginal(original)
                    self.__issuesExtKey[key] = self.__creatorFromOriginal.createIssueFromOriginal(original)
                return self.__issuesExtId[id]

    def getIssuesFromOriginals(self,originals, date):
        assert isinstance(originals, Iterable), "originals shall be a list"
        issues = []
        for o in originals:
            assert isinstance(o, Issue), "original items shall be of type " + str(type(Issue))
        for o in originals:
            issue = self.getIssueFromOriginal(o, date)
            if issue:
                issues.append(issue)
        return issues

    def getIssueByKey(self, key, fields=None, expand=None):
        assert isinstance(key, str), "id shall be a string"

        if key not in self.__issuesExtKey:
            issue = self.__creatorFromServer.createIssueFromServer(key,fields,expand)
            self.getIssueFromOriginal(issue)  # self.__issuesExt[id] = <<< will be done inside getSprintFromOriginal
        return self.__issuesExtKey[key]

    def getIssueById(self, id, fields=None, expand=None):
        assert isinstance(id, str), "id shall be a string"

        if id not in self.__issuesExtId:
            issue = self.__creatorFromServer.createIssueFromServer(id,fields,expand)
            self.getIssueFromOriginal(issue)  # self.__issuesExt[id] = <<< will be done inside getSprintFromOriginal
        return self.__issuesExtId[id]

    def getSprintFromOriginal(self, original:Sprint):
        if not original:
            return None
        else:
            assert hasattr(original,'id'), "original shall have id attribute"
            id = int(original.id)
            if id not in self.__sprintsExt:
                self.__sprintsExt[id] = self.__creatorFromOriginal.createSprintFromOriginal(original)
            return self.__sprintsExt[id]

    def getSprintById(self,id):
        assert isinstance(id, int), "id shall be of type int"
        if id not in self.__sprintsExt:
            sprint = self.__creatorFromServer.createSprintFromServer(id)
            self.getSprintFromOriginal(sprint) # self.__sprintsExt[id] = <<< will be done inside getSprintFromOriginal
        return self.__sprintsExt[id]

    def getBoardByIdName(self,id,name=""):
        if id not in self.__boardsExt:
            self.__boardsExt[id] = self.__creatorFromServer.createBoardFromServer(id,name)
        return self.__boardsExt[id]

    def getBoardFromOriginal(self, original:Board):
        if not original:
            return None
        else:
            assert hasattr(original,'id'), "original shall have id attribute"
            id = int(original.id)
            if id not in self.__boardsExt:
                self.__boardsExt[id] = self.__creatorFromOriginal.createBoardFromOriginal(original)
            return self.__boardsExt[id]


    def __getstate__(self):
        return {
            '__logger' : self.__logger,
            '__connectionConfig' : self.__connectionConfig,
            '__securityConfig' : self.__securityConfig,
            '__useMultithreading' : self.__useMultithreading,
            '__poolSize' : self.__poolSize,
            #'__issuesExt': self.__issuesExt,
            #'__sprintsExt': self.__sprintsExt,
            '__boardsExt': self.__boardsExt
        }

    def __setstate__(self, state):
        self.__logger = state['__logger']
        self.__connectionConfig = state['__connectionConfig']
        self.__securityConfig = state['__securityConfig']
        self.__useMultithreading = state['__useMultithreading']
        self.__poolSize = state['__poolSize']
        ##self.__issuesExt = state['__issuesExt']
        #self.__sprintsExt = state['__sprintsExt']
        self.__boardsExt = state['__boardsExt']
        self.__creatorFromServer = JSWContainerCreatorFromServer(self.__logger, self.securityConfig, self.connectionConfig, self)
        self.__creatorFromOriginal = JSWContainerCreatorFromOriginal(self.__logger, self)


class JSWContainerCreatorFromServer:
    def __init__(self, iLogger:logger, securityConfig, connectionConfig, iContainer:JSWContainer):
        assert isinstance(iLogger, logger)
        assert isinstance(iContainer, JSWContainer)

        self.__securityConfig = securityConfig
        self.__connectionConfig = connectionConfig
        self.__logger = logger.from_parent(str(type(self)),iLogger)
        self.__container = iContainer
        self.__jiraExt = None

    def getJIRA(self):
        if self.__jiraExt == None:
            self.__jiraExt = self.__createJIRAFromServer(self.__securityConfig, self.__connectionConfig)
        return self.__jiraExt


    def __createJIRAFromServer(self, securityConfig, connectionConfig):
        assert isinstance(securityConfig, SecurityConfig), "id shall be of type int"
        assert isinstance(connectionConfig, ConnectionConfig), "id shall be of type int"
        options = {'agile_rest_path': GreenHopperResource.AGILE_BASE_REST_PATH}
        if connectionConfig.options:
            options.update(ast.literal_eval(connectionConfig.options))

        return JIRAExt(
            self.__container,
            basic_auth=(securityConfig.user, securityConfig.APIToken),
            server=connectionConfig.server,
            options=options)

    def createSprintFromServer(self,id):
        assert isinstance(id, int), "id shall be of type int"
        return self.getJIRA().sprint(id)

    def createIssueFromServer(self,id, fields=None, expand=None):
        assert isinstance(id, str), "id shall be of type string"
        return self.getJIRA().issue(id,fields,expand)

    def createBoardFromServer(self, iId, iName):
        assert isinstance(iId, int), "id shall be of type int"
        assert isinstance(iName, str), "name shall be of type str"
        board = None
        candidates = self.__container.getJIRA().boards(name=iName)
        for b in candidates:
            if b.name == iName and b.id == iId:
                board = b
                break

        return b


class JSWContainerCreatorFromOriginal:

    __logger = None
    __container = None

    def __init__(self, iLogger:logger, iContainer:JSWContainer):
        assert isinstance(iLogger, logger)
        assert isinstance(iContainer, JSWContainer)

        self.__logger = logger.from_parent(str(type(self)),iLogger)
        self.__container = iContainer

    def createIssueFromOriginal(self, original):
        if not original:
            return None
        else:
            assert isinstance(original, Issue), "original parameter shall be of type " + str(type(Issue))
            if original.fields.issuetype.name == 'Epic':
                issueExt = EpicExt(original, self.__container)
            else:
                issueExt = IssueExt(original,self.__container)
            return issueExt

    def createSprintFromOriginal(self, original:Sprint):
        if not original:
            return None
        else:
            assert isinstance(original, Sprint), "original shall be a of type " + str(Sprint)
            return SprintExt(original,self.__container)

    def createBoardFromOriginal(self, original:Board):
        if not original:
            return None
        else:
            assert isinstance(original, Board), "original shall be a of type " + str(Board)
            return BoardExt(original, self.__container)