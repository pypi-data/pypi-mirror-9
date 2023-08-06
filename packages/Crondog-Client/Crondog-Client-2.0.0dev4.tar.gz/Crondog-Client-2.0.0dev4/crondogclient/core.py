import tempfile
import pwd
import platform
import urllib2
import time
import os


def handle_normally(data):
    """Handle the command output normally (stdout) """
    print data


def run_command(command):
    """ Run the command, retrieve the output """
    result = {}

    outfile = tempfile.mktemp()
    errfile = tempfile.mktemp()

    t_start = time.time()

    result['command'] = command
    result['user'] = pwd.getpwuid(os.getuid()).pw_name
    result['hostname'] = platform.node()
    result['return_code'] = os.system("( %s ) > %s 2> %s" % (command, outfile, errfile)) >> 8
    result['start_time'] = t_start
    result['run_time'] = time.time() - t_start
    result['stdout'] = open(outfile, "r").read().strip()
    result['stderr'] = open(errfile, "r").read().strip()

    os.remove(outfile)
    os.remove(errfile)
    return result


def send_data(url, data, key):
    """ Send the data to the api """
    try:
        import json
    except:
        import simplejson as json

    json_string=json.dumps(data)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=json_string)
    request.add_header('X-AppKey', key)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'POST'

    try:
        response = opener.open(request)
        response.read()
        return True
    except urllib2.HTTPError, e:
        print e.read()

    return False
