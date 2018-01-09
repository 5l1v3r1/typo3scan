#!/usr/bin/python
import sys
import socket
import getopt
import ssl
import argparse
import urllib2

# define variables
target = "typo3.org"
target_port = 80
SSL         = False
URL_typo3_changelog = "/typo3_src/ChangeLog"
typo3_root  = "/"
typo3_dirs  = ['fileadmin','typo3','typo3_src','typo3conf','typo3temp','uploads']
extensions_dirs = ['typo3/ext','typo3/sysext','typo3conf/ext']
hostname    = "typo3.org"

# main function
def main():
# read the commandline options
    parser = argparse.ArgumentParser(description='Perform a security scan of Typo3.')
    parser.add_argument('target',type=str,help='Target of security scan, provided as ip address or hostname.')
    parser.add_argument('-P','--port',type=int,default=80,help='Port on target, on which Typo3 web-interface listen.')
    parser.add_argument('-H','--hostname',type=str,default='',help='Hostname of Typo3 installation, needed by shared hosting.')
    parser.add_argument('-S','--ssl',action='store_true',help='If SSL-encrypted connection required.')
    parser.add_argument('-R','--root',type=str,default='/',help='Provide root folder of Typo3 installation.')
    parser.add_argument('-W','--wordlist',type=file,default='typo3_all_extensions.dic',help='Provide list of Typo3 extensions to test.')
    args = parser.parse_args()

    # debug output
    print "Target: "+ str(args.target)
    print "Target port: "+str(args.port)
    print "Use SSL: "+str(args.ssl)
    print "Hostname: "+str(args.hostname)
    print "Root folder of Typo3: "+str(args.root)

    # Parse passed address
    print "Try to determine ip address of given target"
    try:
        target = socket.gethostbyname(args.target)
        print "IP address of target: "+target
    except Exception as socket.error:
        print "Passed target isn't a valid IPv4 address!"

    # no ssl on port 80, switch to 443
    if args.ssl and args.port == 80:
        target_port = 443;
    else:
        target_port = args.port;

    # try to determine hostname, if none set
    if args.hostname == '':
        try:
            print "Try to determine the hostname of given target"
            hostname = socket.gethostbyaddr(target)[0]
            print "Found this hostname {} for this target {}".format(hostname,target)
        except Exception as socket.herror:
            print "No reverse record found!"
        finally:
            hostname = args.hostname
    else:
        hostname = args.hostname;

    # Load dictionary
    try:
        ext_dictionary = args.wordlist
        dictionary = ext_dictionary.readlines()
        print "Load dictionary with {} items".format(len(dictionary))
        ext_dictionary.close()
    except Exception as IOerror:
        print "Can't open dictionary file!"

    # Set appropriate root for further tests
    if args.root != '':
        typo3_root = args.root

    # Create appropriate socker for SSL-connection
    if args.ssl:
        print "Start SSL-connection to {} on port {}".format(target,target_port)
        context = ssl.create_default_context()
        context.check_hostname = False
        client = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((target,target_port))

    # Determine Typo3 version
    # Maybe with fingerprints or with ChangeLog in default folder
    ChangeLog_typo3 = send('GET',client,typo3_root+URL_typo3_changelog,hostname)
    first_line = ChangeLog_typo3.splitlines()[0]
    print "Got this ChangeLog: {}".format(first_line)

    #
    parsed_url = parse_url(target,hostname,args.ssl,typo3_root+URL_typo3_changelog)
    print parsed_url
    try:
        response = urllib2.urlopen(parsed_url)
        print "Type of response: {}".format(response.read(1024))
    except Exception as (URLError,HTTPError):
        print "Can't open this URL: {}".format(parsed_url)

    # Check for index in dirs

    # Get list and versions of used extensions
    #send(client,URL,hostname)


    # close socket
    client.close()

# Send HTTP request and return response
def send(method,connection,connect_url,hostname):
    # send root document
    if hostname != '':
        connection.send("{} {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(method,connect_url,hostname))
    else:
        connection.send("{} {} HTTP/1.0\r\n\r\n".format(method,connect_url))
    # receive some data
    response = ''
    buf = connection.recv(4096)
    while buf != '':
        #print "while loop..."
        response += buf
        buf = connection.recv(4096)

    return response

#
def parse_url(Ip,Hostname,Ssl,Request):
    scheme = "http://"
    if Ssl:
        scheme = "https://"
    if Hostname != '':
        url = scheme+Hostname+Request
    else:
        url = scheme+Ip+Request

    return url
# call main
main()
