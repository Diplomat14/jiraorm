from jira.resources import Issue
from .SprintExt import SprintExt
from datetime import datetime

class IssueExt(object):
    SPRINTFIELDNAME = "Sprint"
    SPRINTFIELDID = {}
    
    __issue = None
    __container = None

    def __init__ ( self, original : Issue, container ):
        self.__issue = original
        self.__container = container
        if container not in IssueExt.SPRINTFIELDID.keys():
            IssueExt.SPRINTFIELDID[container] = container.getJIRA().getFieldIDString(IssueExt.SPRINTFIELDNAME)

    @property
    def container(self):
        return self.__container

    @property
    def original(self):
        return self.__issue

    def reloadFromServer(self, fields=None, expand=None):
        newI = self.__container.getJIRA().issue(self.__issue.id,fields=fields,expand=expand)
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
        return hasattr(self.original,name) or hasattr(self.original.fields,name) or self.hasCustomField(name)

    def getField(self, name:str):

        if name != None:
            if name == 'sprints':
                return self.getSprints()
            elif name == 'sprint' or name == 'lastsprint':
                return self.getLastSprint()
            elif name == 'firstsprint':
                return self.getFirstSprint()
            else:
                if name in ['changelog','id','key']:
                    id = name
                else:
                    id = self.__container.getJIRA().getFieldIDString(name)

                if hasattr(self.original,id):
                    return getattr(self.original,id)
                if hasattr(self.original.fields,id):
                    return getattr(self.original.fields,id)
                else:
                    return None
        else:
            return None

    def hasCustomField(self,name:str):
        id = self.__container.getJIRA().getFieldIDString(name)
        return id != None and id != name

    def getCustomField(self,name:str):
        fieldid = self.__container.getJIRA().getFieldIDString(name)
        if fieldid is not None and fieldid != "":
            return self.getField(fieldid)
        else:
            return None

    def getFieldAsString(self, name:str):
        v = self.getField(name)
        if type(v) is str:
            return v
        elif hasattr(v,'name'):
            return v.name
        elif v is None:
            return ''
        else:
            return str(v)

    def setField(self, field:str, value):
        self.original.update({field:value})

    def setFields(self, dict):
        self.original.update(dict)

    def isCustomFieldSet(self,fieldName: str):
        field = getattr(self.__issue.fields, fieldName)
        return True if hasattr(field, 'data') else False

    def getSprints(self):
        sprints = self.getField(IssueExt.SPRINTFIELDID[self.__container])
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


    def getFirstSprint(self):
        s = self.getSprints()
        return s[0] if len(s) > 0 else None

    def getChangelog(self,expand = False):
        if not self.hasField('changelog') and expand == True:
            self.reloadFromServer(expand='changelog')

        if self.hasField('changelog'):
            return self.getField('changelog')
        else:
            return None

    def getFieldUpdatesAsDT(self,name:str, useIssueCreated = True, expand = False):
        d = self.getFieldUpdated(name,useIssueCreated,expand)
        if d != None:
            dt = datetime.strptime(d,'%Y-%m-%dT%H:%M:%S.%f%z')
            return dt
        else:
            return None

    def getFieldUpdated(self,name:str, useIssueCreated = True, expand = False):
        cl = self.getChangelog(expand)
        defaultUpdated = None
        if useIssueCreated == True:
            defaultUpdated = self.getField('created')

        if cl != None:
            #assert isinstance(cl,jira.resources.PropertyHolder)
            updated = defaultUpdated
            for h in reversed(cl.histories):
                for i in h.items:
                    if i.field == name:
                        updated = h.created
            return updated
        else:
            return defaultUpdated