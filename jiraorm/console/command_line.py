import jiraorm
from jiraorm.BasicConfig import ConnectionConfig
from jiraorm.BasicConfig import SecurityConfig
from jiraorm.JSWContainer import JSWContainer

import argparse
from xdev.core.logger import logger


# Typical command line requests
# Check connection
# command_line.py -s "https://DOMAIN.atlassian.net" -u "USER@MAIL" -at "TOKEN" -log ".\working\jiraorm\log.txt" -op "Connect"
# Select items
# command_line.py -s "https://DOMAIN.atlassian.net" -u "MAIL" -at "TOKEN" -log ".\working\jiraorm\log.txt" -op "Select" -q "FILTER" -f "id,summary,assignee" -out ".\working\jiraorm\issues.json"


def main():
    l = logger("CL")
    l.msg("JIRA ORM Command line tool started")

    try:
        # This shall prepare and parse all arguments so that we can easily work with them afterwards
        args = parse_arguments(init_arguments())
        if args.logoutput != None:
            l.set_path(args.logoutput)

        try:
            l.msg("Operation %s" % str(args.operation))

            c = None
            output = None

            # For most of operations we need connection to JIRA so coding it once
            if args.operation == operation.Connect or args.operation == operation.Select:
                c = operation_connect(l, args)


            if args.operation == operation.Select:
                output = operation_select(l,args,c)
            else:
                if args.operation != operation.Connect:
                    l.warning("Operation %s not implemented" % str(args.operation))

            if output != None and args.output != None:
                with open(args.output,"w") as f:
                    return f.write(output)

        except Exception as e:
            l.error("Exception happened during operation processing: " + str(e))

    except Exception as e:
        l.error("Exception on commandline arguments parsing: " + str(e))

    l.msg("Command line tool finished")


def operation_connect(l:logger, args):
    ccfg = ConnectionConfig(args.server)
    scfg = SecurityConfig(args.username, args.access_token)

    c = JSWContainer(l, ccfg, scfg)

    c.getJIRA()
    l.msg("Successfully connected to JIRA")

    return c

def operation_select(l:logger, args, c:JSWContainer):
    if args.query != None:
        issuesExt = c.getJIRA().search_issues_nolim(args.query)
        l.msg("Retreived %d issues" % len(issuesExt))

        if args.output != None:
            fields = args.fields if args.fields != None else ['id', 'summary']
            return issues2json(issuesExt,fields)
    else:
        raise Exception("No query has been specified")

def issues2json(issues, fields):
    jsonString = "[\n"

    for issue in issues:
        jsonString += "\t" + issue2json(issue,fields) + ",\n"

    jsonString += "]\n"
    return jsonString

def issue2json(issue, fields):
    jsString = "{"

    for f in fields:
        if issue.hasField(f):
            jsString += '%s:"%s",' % (escape_string(f), escape_string(issue.getFieldAsString(f)))
        else:
            print('Field %s not found' % f)

    jsString += "}"

    return jsString

def escape_string(raw):
    s = str(raw)
    return s.translate(s.maketrans(
        {'"':  r'\"'}
    ))







from enum import Enum, unique

@unique
class operation(Enum):
    Connect = 1 # Test JIRA Connection
    Select = 2 # Select certain JIRA issues

def init_arguments():
    parser = argparse.ArgumentParser(description='JIRA ORM Command Line tool')

    parser = init_common_arguments(parser)

    operations_group = parser.add_argument_group('Script operations options')
    ops = [op.name for op in list(operation)]
    operations_group.add_argument('-op', '--operation', required=True,
                                  help='Operation that is to be executed', choices=ops)
    operations_group = init_common_operations_arguments(operations_group)

    return parser

def init_common_arguments(parser):
    assert isinstance(parser, argparse.ArgumentParser), "Parser has to be of argparse.ArgumentParser type. Given: " + str(type(parser))

    jira_group = parser.add_argument_group('JIRA server connection options')
    jira_group.add_argument('-s', '--server', required=True,
                            help='The JIRA instance to connect to, including context path.')

    apit_auth_group = parser.add_argument_group('APIToken auth options')
    apit_auth_group.add_argument('-u', '--username', required=True,
                                 help='The username to connect to this JIRA instance with.')
    apit_auth_group.add_argument('-at', '--access-token', required=True,
                                 help='API access token for the user (set it up at your user settings at id.atlassian.net).')

    cache_group = parser.add_argument_group('Local cache')
    cache_group.add_argument('-cc', '--cache-create', required=False,
                             help='Create cache ile by result of all operations.')
    cache_group.add_argument('-cu', '--cache-use', required=False,
                             help='Use cache file as initial data.')

    output_group = parser.add_argument_group('Script output options')
    output_group.add_argument('-log', '--logoutput', required=False,
                                  help='Store log output to file')
    output_group.add_argument('-out', '--output', required=False,
                                  help='Store output of operation to file')

    return parser


def init_common_operations_arguments(operations_group):
    operations_group.add_argument('-q', '--query', required=False,
                                  help='Initial query to get issues to process (if applicable)')
    operations_group.add_argument('-f', '--fields', required=False,
                                  help='comma separated fields list to process (if applicable)')
    return operations_group


def parse_arguments(parser: argparse.ArgumentParser):
    args = parser.parse_args()

    args.operation = operation[args.operation]
    if args.fields != None:
        args.fields = args.fields.rstrip(",").split(",")

    return args


if __name__ == "__main__":
    main()