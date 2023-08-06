import os
from json import dumps

from .utils import get_session, validate_result, BASE_URL, \
                   repackage_input, process_input_in_batches

class ClassificationData:
    """ A local representation of a MetaMind dataset resource. """

    def __init__(self, name=None, private=None, data_type=None, id=None, verbose=True):
        """ Creates a local dataset reference. 

        :param name: The name of the dataset (will be updated on the server)
        :type  name: :mod:`str`
        :param private: Whether or not the dataset is private
        :type private: :mod:`bool`
        :param data_type: Either "image" or "text"
        :type data_type: :mod:`str`
        :param id: The id of the dataset resource to have this local representation mirror
        :type id: :mod:`int`
        :param verbose: If True, some info about the dataset is printed to :mod:`stdout`.
        :type verbose: :mod:`bool`

        :returns: :class:`ClassificationData`.

        If a valid id is specified, 
        it grabs the reference points to the corresponding dataset. 
        Otherwise, it creates a new dataset is created and referenced.
        """
        if(id):
            url = BASE_URL + "/api/v1.2/datasets/%d"%(id)
            response=get_session().get(url)
            verb = "fetching"

        else:
            url=BASE_URL + "/api/v1.2/datasets"
            
            data={"name" : name,
                  "private" : private,
                  "data_type" : data_type}
            
            response = get_session().post(url, data=data)
            verb = "creating"

        result = validate_result(response)

        self.set_values(result)

        if verbose:
            print "You are " + verb + " dataset '%s', with id: %d" % (self.name, self.id)


    def add_samples(self, input_, input_type, unzip_on_client=True, verbose=True, skip_invalid_values=True, encoding='utf-8'):
        """ Add samples to the dataset associated with this data object.

        :param input_: This parameter can have multiple forms, illustrated by these examples:
        
            **Image Datasets**::

                 add_samples([("/path/to/file1.jpg", "my label"), ("/path/to/file2.jpg", "my other label")], input_type="files")            # labeled files
                 add_samples(["/path/to/file1.jpg", "/path/to/file2.jpg"], input_type="files")                                              # unlabeled files
                 add_samples([("http://url/to/file1.png", "my label"), ("http://url/to/file2.tiff", "my other label")], input_type="urls")  # labeled urls
                 add_samples(["http://url/to/file1.png", "http://url/to/file2.tiff"], input_type="urls")                                    # unlabeled urls
                 add_samples("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file

            **Text Datasets**::

                 add_samples([("that movie was great!", "positive"), ("that movie stunk", "negative")], input_type="text" )                 # labeled text
                 add_samples(["that movie was great!", "that movie stunk"], input_type="text")                                              # unlabeled text
                 add_samples("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file
                 add_samples("/path/to/tsv/file.tsv", input_type="tsv")                                                                     # text only

            Note that tsv files must be arranged in two columns with the first containing the label and the second containing the sample

            Note that zip files must have the following directory structure::

                my_data/
                    label1/
                        first_image.jpg
                        second_image.jpg
                    label2/
                        third_image.jpg
                        fourth_image.jpg
                        fifth_image.jpg

        :type input_: :mod:`list` or :mod:`str`
        :param input_type: The input format being used: 'files', 'urls', 'zip', 'tsv' or 'text'. This parameter is required for all inputs other than datasets.
        :type input_type: :mod:`str`
        :param unzip_on_client: A flag for indicating if we allow files to be unzipped on the client (improves performance)
        :type unzip_on_client: :mod:`bool`
        :param verbose: When true, will print progress to stdout
        :type verbose: :mod:`bool`
        :param skip_invalid_values: A flag for indicating whether to just pass over any invalid values
        :type skip_invalid_values: :mod:`bool`
        :param encoding: When uploading text data this specifies the text encoding
        :type encoding: :mod:`str`
        """

        url = BASE_URL + "/api/v1.2/datasets/%d/entries"%(self.id)
        if verbose: print "Starting data upload..."

        results = process_input_in_batches(url,
                                           input_, input_type,
                                           unzip_on_client=unzip_on_client, skip_invalid_values=skip_invalid_values, encoding=encoding,
                                           verbose=verbose)
        # we only need the last one
        self.set_values(results.pop())

    def list_samples(self, **kwargs):
        """ Get some information about samples in this dataset.

        :param **kwargs: keys are one of ["user_value", "value", "label"]
            and the values are a list of values for the specified key for which any sample
            with matching values will be included. In the case of "image" data, "user_value" 
            should be original filenames/links used to upload (in the case of zip files, 
            it should be the relative paths and filenames from the root of the zipfile). 
            In the case of "text" data, "values" should be the exact text of the entry

        :returns: A list of dictionaries, one for each sample which satisifies all the filters provided
            using **kwargs. Each dictionary contains information about each sample, including all of the 
            keys that can be used for filtering ("user_value", "value", "label")
        """
        
        url = BASE_URL + "/api/v1.2/datasets/%d/entries"%(self.id)

        response = get_session().get(url, data=kwargs)
        result = validate_result(response)
        
        return result["entries"]

    def remove_samples(self, **kwargs):
        """
        Remove values using the given filters.

        :param **kwargs: keys are one of ["user_value", "value", "label"]
            and the values are a list of values for the specified key for which any sample
            with matching values will be included. In the case of "image" data, "user_value" 
            should be original filenames/links used to upload (in the case of zip files, 
            it should be the relative paths and filenames from the root of the zipfile). 
            In the case of "text" data, "values" should be the exact text of the entry

        """

        url = BASE_URL + "/api/v1.2/datasets/%d/entries"%(self.id)

        response = get_session().delete(url, data=kwargs)
        result = validate_result(response)

    def set_values(self, result):
        """
        Sets values on the local dataset instance given results from the api queries.
        """
        self.name=result['name']
        self.private=result['private']
        self.data_type=result['data_type']
        self.id=result['id']        
        self.n_entries=result['n_entries']
        self.labels=result.get('labels', None)
        self.is_labeled=result.get('is_labeled', None)

    def get_values(self):
        """ Packages the values of the local model into a dictionary

        :returns: A dictionary whose keys are the attributes of the :class:`ClassificationModel` object
        """
        result = {}
        params = ["name", "private", "data_type", "id", "n_entries", "labels", "is_labeled"]
        for param in params:
            if hasattr(self, param):
                if getattr(self, param):
                    result[param] = getattr(self, param)

        return result

    def clear_values(self):
        """
        Clears the values on the local dataset instance.
        """
        self.name = None
        self.private = None
        self.data_type = None
        self.id = None
        self.n_entries = None
        self.labels = None
        self.is_labeled = None
