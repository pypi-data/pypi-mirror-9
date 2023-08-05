################################################################
# haufe.sharepoint
################################################################

import argparse
import pprint
import connector

def main():

    parser = argparse.ArgumentParser(description='haufe.sharepoint commandline utility')
    parser.add_argument('--username', type=str, dest='username', help='Username', required=True)
    parser.add_argument('--password', type=str, dest='password', help='Password', required=True)
    parser.add_argument('--url', type=str, dest='url', help='Sharepoint server URL', required=True)
    parser.add_argument('--list', type=str, dest='list', help='Name or ID of list', required=True)
    parser.add_argument('--cmd', type=str, dest='cmd', help='command: fields|items', required=True)

    args = parser.parse_args()
    service = connector.Connector(args.url,
                                  args.username, 
                                  args.password,
                                  args.list)

    cmd = args.cmd
    if cmd == 'fields':
        fields = service.model
        print 'Primary key: %s' % service.primary_key
        print 'Required fields:'
        pprint.pprint(sorted(service.required_fields))
        print 'All fields:'
        for field in sorted(service.all_fields):
            pprint.pprint(service.model[field])

    elif cmd == 'items':
        for row in service.getItems():
            pprint.pprint(row)


if __name__ == '__main__':
    main()
