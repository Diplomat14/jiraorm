#from .JSWContainer import JSWContainer
from .IssueExt import IssueExt

class EpicExt(IssueExt):
    EPICLINKFIELDNAME = "Epic Link" #customfield_10006
    EPICLINKFIELD = "" #customfield_10006

    def __init__ ( self, original, container ):
        if EpicExt.EPICLINKFIELD == "":
            EpicExt.EPICLINKFIELD = container.getJIRA().getFieldIDString(EpicExt.EPICLINKFIELDNAME)
        super(EpicExt,self).__init__(original,container)

    def getIssuesInEpic(self):
        super(EpicExt, self).container.getJIRA()
        top_request_query = '"%s" = %s ORDER BY summary ASC' % (EpicExt.EPICLINKFIELDNAME, self.original.key)
        return super(EpicExt,self).container.getJIRA().search_issues_nolim(top_request_query)
        

    