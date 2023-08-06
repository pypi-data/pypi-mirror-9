import os
import time
import base64
import urllib2
import zipfile
import requests
import tempfile
import shutil
from copy import copy
from simplejson.scanner import JSONDecodeError
from random import randint
from warnings import warn
from simplejson import dumps
from glob import glob

BASE_URL = os.getenv("API_BASE_URL", "https://api.metamind.io")
API_KEY = None
session_override = None

def make_request(url, method, **kwargs):
    methods = {
        "GET" : get_session().get,
        "POST" : get_session().post,
        "DELETE" : get_session().delete,
    }

    num_tries = kwargs.pop("num_tries", 10)
    message = kwargs.pop("message", None)

    for i in range(num_tries):
        response = None
        try:
            response = methods[method](url, **kwargs)
            return validate_result(response)
        except Exception as e:
            import traceback
            traceback.print_exc()
            if i == num_tries-1 or response.status_code not in [502, 504]:
                raise
            else:
                if message is not None:
                    warn(message)
                else:
                    warn("Unable to complete request on try %d. Retrying..." % i)
                time.sleep(1)

def get_session():
    import logging
    check_api_key()
    
    session = session_override or requests.Session()
    session.headers.clear()
    session.headers["Authentication"] = "Basic " + API_KEY

    return session

def use_session(session):
    global session_override
    session_override = session

def set_api_key(api_key, verbose=True):
    """ Set the MetaMind.io api key for the module.

    :param api_key: Your user api key, which can be found on the metamind.io website (under Profile)
    :type api_key: :mod:`str`
    :param verbose: If True, the user's name is printed to :mod:`stdout`.
    :type verbose: bool
    """
    global API_KEY
    API_KEY=api_key

    if verbose: print "Hello, %s" % get_user_info()["full_name"]

def get_api_key():
    """ Get the MetaMind.io api key for the module.

    :returns: A :mod:`str` which is the user's api key (assuming the key has been set using :func:`set_api_key`)
    """
    header = get_session().headers.get("Authentication")
    return header[6:]

def check_api_key():
    if not API_KEY:
        raise ValueError("API_KEY key has not been set yet.")

def get_user_id():
    """ Get the user id for the current user (identified by their api key)

    :returns: An integer value which is the current user's id
    """
    return get_user_info()["id"]

def get_user_info():
    """ Get the user id for the current user (identified by their api key)

    :returns: An integer value which is the current user's id
    """
    check_api_key()
    url = BASE_URL + "/api/v1.2/current_user"
    response = get_session().get(url)
    return validate_result(response)

def get_input_from_path(path):
    """ Produces the appropriate input for the :func:`ClassificationData.add_samples` function given a path to a 
    """
    return [(f,os.path.split(label_dir)[1]) for label_dir in glob(os.path.abspath(path) + "/*") for f in glob(label_dir + "/*")]

def match_predictions_with_labels(predictions, file_input):
    file_input = repackage_input(file_input)

    fnames = list(zip(*file_input)[0])

    required_keys = ["user_value", "class"]
    for pred in predictions:
        for key in required_keys:
            if not pred.get(key):
                return ValueError("each dictionary in predictions must contain a '" + key + "' key")

    return [(pred["class"], file_input[fnames.index(pred["user_value"])][1]) for pred in predictions]

def validate_result(response):
    try:
        result=response.json()
    except JSONDecodeError:
      raise ValueError("Unknown server error (error code: %d, url: %s)" % (response.status_code, response.url))

    if "message" in result.keys():
        raise ValueError(result["message"])

    return result

def is_zipfile(f):
    try:
        zipfile.ZipFile(f)
        return True
    except:
        return False

def repackage_input(input_, input_type, unzip_on_client=True):
    input_=copy(input_)
    input_type=copy(input_type)
    # some minimal repackaging
    if input_type=="zip" and unzip_on_client:
        warn("Unzipping file '%s' into a temporary directory (for higher upload speed)"%input_, UserWarning)
        tmpdir = os.path.join(tempfile.gettempdir(), str(randint(0,10000000000)))
        if not os.path.isdir(tmpdir):
            os.makedirs(tmpdir)
        zf = zipfile.ZipFile(input_)
        zf.extractall(path=tmpdir)
        root = zf.namelist()[0].encode("ascii")
        if root != "/":
            tmpdir = os.path.join(tmpdir, root)
        input_ = get_input_from_path(tmpdir)
        input_type='files'
    elif isinstance(input_, str) or isinstance(input_,unicode):
        # repackage strings
        input_ = [(input_, None)]
    elif isinstance(input_, tuple):
        input_ = [input_]
    elif isinstance(input_, list):
        # repackage unlabeled lists
        for i,val in enumerate(input_[:]):
            if not isinstance(val, tuple):
                input_[i] = (val, None)
    else:
        raise ValueError("input must either be a string, tuple, or list")

    return input_,input_type

def process_input_in_batches(url, input_, input_type, unzip_on_client=False, skip_invalid_values=True, encoding='utf-8', verbose=False, options={}):
    assert input_,"input parameter must be specified"
    assert input_type,"input_type parameter must be specified"
    
    input_repackaged, input_type_repackaged = repackage_input(input_,input_type,unzip_on_client)
    
    # build request, looping over batches of the max number of open files (minus 50)
    results = []
    max_open_files = 150
    split_input = [input_repackaged[i:i+max_open_files] for i in range(0,len(input_repackaged), max_open_files)]
    num_uploaded_files = 0

    if isinstance(input_repackaged, list):
        num_files = len(input_repackaged)
    else:
        num_files = 1
    
    for batch_num, inp in enumerate(split_input):
        files=[]
        entries=[]

        i=0
        for (value, label) in inp:
            try:
                entry = {'label':label}
                if(input_type_repackaged in ['files','zip','tsv']):
                    files.append(('file',open(os.path.expanduser(value))))
                entries.append({'label':label,
                                'value':value})

                i+=1
            except IOError:
                pass

        num_uploaded_files += len(entries)
        data={"entry_type":input_type_repackaged,
              "skip_invalid_values":skip_invalid_values,
              "entries":dumps(entries, encoding=encoding)}
        data.update(options)

        result = make_request(url, 'POST', files=files, data=data)

        if result.get("skipped_values"):
            if result.get("name") and result.get("data_type"):
                warn("Skipping the following values because they were invalid for the dataset '%s' (which has the data type '%s'): %s" % (result["name"], result["data_type"], str(result["skipped_values"])))
            else:
                warn("Skipping the following values: %s" % (str(result["skipped_values"])))
        
        results.append(result)

        # close all the files
        for f in files:
            if not f[1].closed:
                f[1].close()
        if verbose: print "Finished uploading %d of %d samples..." %(num_uploaded_files, num_files)

    return results



