from jira.resources import Issue
from .SprintExt import SprintExt

class IssueExt(object):
    SPRINTFIELDNAME = "Sprint"
    SPRINTFIELDID = "customfield_10113"
    
    __issue = None
    __container = None

    def __init__ ( self, original : Issue, container ):
        self.__issue = original
        self.__container = container

    @property
    def container(self):
        return self.__container

    @property
    def original(self):
        return self.__issue

    def reloadFromServer(self):
        newI = self.__container.getJIRA().issue(self.__issue.id)
        if newI:
            self.__issue = newI
            return True
        else:
            return False

    def getLinks(self):
        if hasattr(self.__issue.fields,'issuelinks') or self.reloadFromServer() == True:
            return self.__issue.fields.issuelinks
        else:
            return None

    def getLinksByType( self, typeName : str, Inward : bool = True ):
        links = self.getLinks()
        validLinks = []
        for link in links:
            if link.type.name == typeName and ((Inward == True and hasattr(link, 'inwardIssue')) or (Inward == False and hasattr(link, 'outwardIssue'))):
                validLinks.append(link)
        return validLinks

    def getChildren( self, linkType:str,linkInward:bool = False):
        links = self.getLinksByType(linkType,linkInward)
        children = []
        for l in links:
            children.append(
                self.__container.getIssueFromOriginal(
                    l.outwardIssue if linkInward == False else l.inwardIssue
                )
            )
        return children

    def hasField(self, name:str):
        if ( name == 'id' or name == 'key'):
            return True
        else:
            return hasattr(self.original.fields,name)

    def getField(self, name:str):
        if name == 'id':
            return self.original.id
        elif name == 'key':
            return self.original.key
        else:
            if self.hasField(name):
                return getattr(self.original.fields,name)
            else:
                return None

    def getFieldAsString(self, name:str):
        v = self.getField(name)
        if type(v) is str:
            return v
        elif hasattr(v,'name'):
            return v.name
        else:
            return str(v)

    def setField(self, field:str, value):
        self.original.update({field:value})

    def isCustomFieldSet(self,fieldName: str):
        field = getattr(self.__issue.fields, fieldName)
        return True if hasattr(field, 'data') else False

    def getSprints(self):
        sprints = self.getField(self.SPRINTFIELDID)
        sprintsExt = []
        if type(sprints) == str:
            sext = SprintExt.getSprintFromRawStringWithId(sprints,self.__container)
            sprintsExt.append(sext)
        elif type(sprints) == list and type(sprints[-1]) == str:
            for s in sprints:
                sext = SprintExt.getSprintFromRawStringWithId(s,self.__container)
                sprintsExt.append(sext)
            
        return sprintsExt

    def getLastSprint(self):
        s = self.getSprints()
        return s[-1] if len(s) > 0 else None

