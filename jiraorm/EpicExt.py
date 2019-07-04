#from .JSWContainer import JSWContainer
from .IssueExt import IssueExt

class EpicExt(IssueExt):
    EPICLINKFIELD = "customfield_10006" #customfield_10006

    def __init__ ( self, original, container ):
        super(EpicExt,self).__init__(original,container)

    def getIssuesInEpic(self):
        top_request_query = '"Epic Link" = %s ORDER BY summary ASC' % (self.original.key)
        return super(EpicExt,self).container.getJIRA().search_issues_nolim(top_request_query)
        

    