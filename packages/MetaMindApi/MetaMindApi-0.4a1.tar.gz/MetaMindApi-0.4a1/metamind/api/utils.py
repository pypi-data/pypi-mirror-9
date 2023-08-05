import os
import base64
import resource
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

BASE_URL = "https://api.metamind.io"
API_KEY = None

def get_session():
    check_api_key()
    
    session = requests.Session()
    session.headers.clear()
    session.headers["Authentication"] = "Basic " + API_KEY

    return session

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
    url = BASE_URL + "/api/v1.1/current_user"
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

def repackage_input(input_, unzip_on_client=True):
    input_ = copy(input_)
    # some minimal repackaging
    if isinstance(input_, str) or isinstance(input_,unicode):
        if unzip_on_client and zipfile.is_zipfile(input_):
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
        else:
            # repackage strings
            input_ = [(input_, None)]
    elif isinstance(input_, list):
        # repackage unlabeled lists
        for i,val in enumerate(input_[:]):
            if not isinstance(val, tuple):
                input_[i] = (val, None)
    else:
        raise ValueError("input must either be a string or a list")

    return input_

def process_input_in_batches(url, input_, is_tsv=False, verbose=False, skip_invalid_values=True):
    # build request, looping over batches of the max number of open files (minus 50)
    # input_ = copy(input_)
    results = []
    max_open_files = min(128, resource.getrlimit(resource.RLIMIT_NOFILE)[0] / 2)
    split_input = [input_[i:i+max_open_files] for i in range(0,len(input_), max_open_files)]
    num_uploaded_files = 0
    for inp in split_input:
        data = {}
        files = {}
        open_files = []
        for i, (value, label) in enumerate(inp):
            key = "file%d" % i # write the key in the same way as javascript
            try:
                f = open(os.path.expanduser(value))
                open_files.append(f)
                files[key] = f
            except IOError:
                pass

            data["label%d"%i] = dumps(label)
            data["user_value%d"%i] = dumps(value)
            data["is_tsv%d"%i] = dumps(is_tsv)

        num_uploaded_files += len(data.keys())/3
        data["skip_invalid_values"] = skip_invalid_values

        response = get_session().post(url, files=files, data=data)
        result = validate_result(response)

        if result.get("skipped_values"):
            warn("Skipping the following values because they were invalid for the dataset '%s' (which has the data type '%s'): " % (result["name"], result["data_type"]) + str(result["skipped_values"]))

        
        results.append(result)

        # close all the files
        for f in open_files:
            if not f.closed:
                f.close()
        if verbose: print "Finished uploading %d of %d samples..." %(num_uploaded_files, len(input_))

    return results



