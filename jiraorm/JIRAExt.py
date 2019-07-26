from jira import JIRA
import json
from . import JSWContainer


class JIRAExt(JIRA):

    __container = None

    def __init__(self, iContainer, server=None, options=None, basic_auth=None, oauth=None, jwt=None, kerberos=False, kerberos_options=None,
                 validate=False, get_server_info=True, async_=False, async_workers=5, logging=True, max_retries=3, proxies=None,
                 timeout=None, auth=None):
        assert isinstance(iContainer,JSWContainer.JSWContainer), "Container shall be of " + str(type(JSWContainer.JSWContainer)) + " type"
        assert iContainer != None, "Container cannot be empty"
        self.__container = iContainer

        super(JIRAExt,self).__init__(server, options, basic_auth, oauth, jwt, kerberos, kerberos_options,
                 validate, get_server_info, async_, async_workers, logging, max_retries, proxies,
                 timeout, auth)

    def get_json_by_uri(self, uri : str):
        r_json = self._get_json(uri, base=self.AGILE_BASE_URL)
        return r_json

    def put_json_to_uri(self,uri,data):
        url = self._get_url('%s' % id, base=self.AGILE_BASE_URL)
        r = self._session.put(
            url, data=json.dumps(data))

        return json.loads(r)

    def update_board(self,boardId:int,propertyKey:str,propertyValue:str):
        url = self._get_url('board/%s/properties/%s' % (boardId,propertyKey), base=self.AGILE_BASE_URL)
        r = self._session.put(
            url, data=json.dumps(propertyValue))

        return json.loads(r)

    def search_issues_nolim(self, jql_str, startAt=0, maxResults=50, validate_query=True, fields=None, expand=None,
                      json_result=None):
        jiraIssuesLimitation = 200
        currentStartAt = startAt
        allIssues = super(JIRAExt,self).search_issues(jql_str, currentStartAt, maxResults, validate_query, fields, True,json_result)
        issues = allIssues

        while (len(allIssues) < issues.total-startAt and len(allIssues) < maxResults) and len(issues) != 0:
        #while (maxResults == None or len(allIssues) < maxResults) and (len(issues) == jiraIssuesLimitation):
            currentStartAt = len(allIssues)
            issues = super(JIRAExt,self).search_issues(jql_str, currentStartAt, maxResults, validate_query, fields, expand,json_result)
            if maxResults == None:
                allIssues.append(issues)
            elif len(allIssues) + len(issues) <= maxResults:
                allIssues.extend(issues)
            else:
                numtoAdd = len(allIssues) + len(issues) - maxResults
                allIssues.append( issues[0..numtoAdd] )

        return self.__container.getIssuesFromOriginals(allIssues)

            