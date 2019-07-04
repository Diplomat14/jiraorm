import jiraorm
from jiraorm.BasicConfig import ConnectionConfig
from jiraorm.BasicConfig import SecurityConfig
from jiraorm.JSWContainer import JSWContainer

import argparse
from xdev.core.logger import logger


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

            if output != None and args.out != None:
                with open(args.output) as f:
                    return f.write(output)

        except Exception as e:
            l.error("Exception happened during operation processing" + str(e))

    except Exception as e:
        l.error("Exception on commandline arguments parsing: " + str(e))

    l.msg("JIRA ORM Command line tool finished")


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
        l.msg("Retreived %d issues" % issuesExt.count())
    else:
        raise Exception("No query has been specified")










from enum import Enum, unique

@unique
class operation(Enum):
    Connect = 1 # Test JIRA Connection
    Select = 2 # Select certain JIRA issues

def init_arguments():
    parser = argparse.ArgumentParser(description='JIRA ORM Command Line tool')

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

    operations_group = parser.add_argument_group('Script operations options')
    ops = [op.name for op in list(operation)]
    operations_group.add_argument('-op', '--operation', required=True,
                                  help='Operation that is to be executed', choices=ops)
    operations_group.add_argument('-log', '--logoutput', required=False,
                                  help='Store log output to file')
    operations_group.add_argument('-q', '--query', required=False,
                                  help='Initial query to get issues to process (if applicable)')
    operations_group.add_argument('-out', '--output', required=False,
                                  help='Store output of operation to file')

    return parser


def parse_arguments(parser: argparse.ArgumentParser):
    args = parser.parse_args()

    args.operation = operation[args.operation]

    return args