import os
import time
import itertools
from json import dumps, loads

from .utils import check_api_key, get_session, validate_result, BASE_URL, \
                   repackage_input, process_input_in_batches, make_request

classifier_query_type_map = {
    "TwitterTextClassifier" : "twitter"
}

class ClassificationModel:
    """ A local representation of a MetaMind trainable classifier resource. """
    
    def __init__(self, name=None, private=None, id=None):
        """
        Creates a classifier local instance. 

        :param name: The name of the trainable classifier (will be updated on the server)
        :type name: :mod:`str`
        :param private: Whether or not the dataset is private
        :type private: :mod:`bool`
        :param id: The id of the classifier resource to have this local representation mirror
        :type id: :mod:`int`

        If a valid id is specified, the instance points to the 
        corresponding classifier. Otherwise, the reference is left unspecified 
        until the classifier is fitted to a dataset.
        """

        if id:
            if isinstance(id,str):
                result = {'id' : id}
                if str(id) in ["TwitterTextClassifier"]: 
                    result["query_type"] = classifier_query_type_map[id] 
            else:
                url=BASE_URL + '/api/v1.2/classifiers/%d'%(id);
                response=get_session().get(url)
                result = validate_result(response)
        else:
            result={'name':name,
                    'private':private,
                    'id':None}
        
        self.set_values(result)

    def fit_async(self, dataset, options={}, verbosity=1):
        """
        Fit the classifier to the specified dataset asynchronously.

        :param dataset: The dataset that will be fit. The dataset must have at least two labels.
        :type dataset: :class:`ClassificationData`
        :param options: A dictionary for fine-grained control of the training parameters. Currently, 
            the only allowed key is `test_dataset_id`, which must have the value of a valid dataset_id
        :type options: :mod:`dict`

        Fitting is performed asynchronously. Hence, fit_async() does not block.  In order to check the 
        training progress call status(). Training must finish before any predictions 
        can be made. Training can be stopped at any time by calling halt(). Note that if an id 
        was not specified in the ClassificationModel constructor, a new classifier is created.
        """
        if(self.id):
            url=BASE_URL + '/api/v1.2/classifiers/%d/fit'%(self.id)
        else:
            url=BASE_URL + '/api/v1.2/classifiers/fit'

        data=self.get_values()
        data['train_dataset_id']=dataset.id
        data.update(options)

        response=get_session().post(url,data=data)
        result = validate_result(response)

        self.set_values(result)
        if verbosity>=1:
            print "Your MetaMind %s model is now training on the server!" % dataset.data_type

    def halt(self,verbosity=1):
        """
        Stops asynchronous training.
        """

        if verbosity >= 1:
            print "Halting..."
        
        url=BASE_URL + '/api/v1.2/classifiers/%d/halt'%(self.id)
        response=get_session().post(url)
        
        
    def fit(self, dataset, options={}, verbosity=1):
        """
        Fit the classifier to the specified dataset, and wait until training is finished to return.

        :param dataset: The dataset that will be fit. The dataset must have at least two labels.
        :type dataset: :class:`ClassificationData`
        :param options: A dictionary for fine-grained control of the training parameters. Currently, 
            the only allowed key is `test_dataset_id`, which must have the value of a valid dataset_id
            that is of the same type as `dataset`
        :type options: :mod:`dict`
        :param verbosity: indicates the level of verbosity. `1` has no printing, `2` prints
            estimaged time left, `3` prints estimated time left plus some training statistics (iteration, 
            cost, training_accuracy, testing accuracy)
        :type verbosity: int
        """
        try:
            self.fit_async(dataset=dataset,options=options,verbosity=verbosity)
            
            interval_iter=1
            interval_update=1
            last_update=time.time()
            last_iter = -1
            last_time_left=-1
            header_printed = False
            stats = {}
            while(True):
                status = self.status()
                stats = self.stats()
                
                if (time.time()-last_update)>interval_update:
                    if status=='submitted':
                        print "Your model is in the training queue for free users!"
                    
                    if stats:
                        if 'time_left' in stats and last_time_left!=stats['time_left'] and verbosity>=1:
                            remaining_minutes=stats['time_left']/60
                            remaining_seconds=stats['time_left']%60

                            print "Estimated time left in training: %dm %ds"%(remaining_minutes,remaining_seconds)                        

                            last_time_left=stats['time_left']
                        
                    last_update=time.time()

                if status=='done':
                    if verbosity >= 1: print "Your model is done training!"
                    break
                if status=='failed':
                    if verbosity >= 1: print "Your model failed during training!"
                    break

                time.sleep(1)

            if verbosity >= 1:
                print "Model name: %s"%(self.name)
                print "Model id: %s"%(self.id)

        except KeyboardInterrupt:
            self.halt(verbosity=verbosity)
            raise


    def status(self):
        """
        Retrieve the classifier training status (e.g. "done", "running", "halted", "failed")

        :returns: a :mod:`str` that tells the status of this classifier on the server
        """
        url_status=BASE_URL + '/api/v1.2/classifiers/%d/status'%(self.id)

        response=get_session().get(url_status)
        result = validate_result(response)

        return result["status"]

    def stats(self):
        """
        Retrieve the classifier training training stats.

        :returns: A :mod:`dict` with the keys "time_left" and "training_stats". "time_left" gives an
        estimate of the the number of seconds left in training. "training_stats" is a :mod:`dict`
        containing several lists with keys ["iterations","cost","train_accuracy","test_accuracy"].

        Note that the `test_accuracy` is only updated periodically and maybe not reflect the current
        accuracy of the classifier while training.
        """
        url_status=BASE_URL + '/api/v1.2/classifiers/%d/status'%(self.id)

        response=get_session().get(url_status)
        result = validate_result(response)

        #print "result:",result
        
        packed={}
        if 'stats' in result:
            for stat in ['time_left','training_stats']:
                if stat in result['stats']:
                    packed[stat]=result['stats'][stat]

        return packed
        
    def transform_encoding(self, result, encoding):
        """
        Convert the webserver response to the user-specified encoding
        """

        if encoding != 'utf-8':
            for entry in result:
                for key in entry.keys():
                    if isinstance(entry[key], basestring):
                        entry[key] = entry[key].encode(encoding)
        return result

    def predict(self, input_=None, input_type=None, dataset=None, unzip_on_client=True, skip_invalid_values=True, retry_on_timeout=True, encoding='utf-8', options={}):
        """
        Predict the label of the samples of either the specified dataset or a list of files.

        :param input_: This parameter can have multiple forms, illustrated by these examples:
        
            **Image Datasets**::

                 predict([("/path/to/file1.jpg", "my label"), ("/path/to/file2.jpg", "my other label")], input_type="files")            # labeled files
                 predict(["/path/to/file1.jpg", "/path/to/file2.jpg"], input_type="files")                                              # unlabeled files
                 predict([("http://url/to/file1.png", "my label"), ("http://url/to/file2.tiff", "my other label")], input_type="urls")  # labeled urls
                 predict(["http://url/to/file1.png", "http://url/to/file2.tiff"], input_type="urls")                                    # unlabeled urls
                 predict("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file

            **Text Datasets**::

                 predict([("that movie was great!", "positive"), ("that movie stunk", "negative")], input_type="text" )                 # labeled text
                 predict(["that movie was great!", "that movie stunk"], input_type="text")                                              # unlabeled text
                 predict("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file
                 predict("/path/to/tsv/file.tsv", input_type="tsv")                                                                     # text only

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
        :param dataset: A dataset (can be labeled or unlabeled) with at least 1 uploaded sample, which has 
            the same type as the dataset associated with this classifier.
        :type dataset: :class:`ClassificationData`
        :param unzip_on_client: A flag for indicating if we allow files to be unzipped on the client (improves performance)
        :type unzip_on_client: :mod:`bool`
        :param skip_invalid_values: A flag for indicating whether to just pass over any invalid values
        :type skip_invalid_values: :mod:`bool`
        :param retry_on_timeout: A flag for indicating whether to retry a request if it times out (which can happen if predictions are made on a dataset that is too large).
        :type retry_on_timeout: :mod:`bool`
        :param encoding: A string indicating the encoding of any text that is uploaded (either directly passed as a string, or in a text file)
        :type encoding: :mod:`str`
        :param options: An optional dictionary for specifying any additional prediction parameters (currently only allowed
            option is `compute_stats`, which is a :mod:`bool` indicating if the classifier should update it's statistics
            using the results of these predictions)
        :type options: :mod:`dict`

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a `label` key which contains the :mod:`str` name of the predicted label, a `probability` key which
            contains the probability that the specified label is correct, and a `user_value` key which contains
            the original value uploaded. The `user_value` key is important because if `dataset` is used to 
            specify the samples to be predicted, the predictions will not necessarily be returned in the order 
            they were uploaded. The dictionaries can contain additional keys with other information.
        """
        self._verify_input(input_, input_type, dataset)

        if dataset:
            url=BASE_URL + '/api/v1.2/classifiers/' + str(self.id) + '/predict'
            data={'dataset_id' : dataset.id}
            data.update(options)
            result = make_request(url, "POST", data=data, message="It looks like you're trying to make too many " + \
                                                                  "predictions at once. Try breaking up your dataset " + \
                                                                  "into smaller chunks and make predictiosn on each of those.")
            result = result["predictions"]

        elif input_:
            url=BASE_URL + '/api/v1.2/classifiers/' + str(self.id) + '/predict'
            results = process_input_in_batches(url, input_, input_type, unzip_on_client=unzip_on_client, skip_invalid_values=skip_invalid_values, encoding=encoding, options=options)
            if not all([result.get("predictions") for result in results]):
                return
            results = [result["predictions"] for result in results]
            # combine results into one long list
            result = list(itertools.chain(*results))

        result = self.transform_encoding(result, encoding)

        return result


    def predict_proba(self, input_=None, input_type=None, dataset=None, unzip_on_client=True, skip_invalid_values=True, encoding='utf-8', options={}):
        """
        Predict the probabilities for each label for each of the samples of a dataset, a single file or a list of files.

        :param input_: This parameter can have multiple forms, illustrated by these examples:
        
            **Image Datasets**::

                 predict_proba([("/path/to/file1.jpg", "my label"), ("/path/to/file2.jpg", "my other label")], input_type="files")            # labeled files
                 predict_proba(["/path/to/file1.jpg", "/path/to/file2.jpg"], input_type="files")                                              # unlabeled files
                 predict_proba([("http://url/to/file1.png", "my label"), ("http://url/to/file2.tiff", "my other label")], input_type="urls")  # labeled urls
                 predict_proba(["http://url/to/file1.png", "http://url/to/file2.tiff"], input_type="urls")                                    # unlabeled urls
                 predict_proba("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file

            **Text Datasets**::

                 predict_proba([("that movie was great!", "positive"), ("that movie stunk", "negative")], input_type="text" )                 # labeled text
                 predict_proba(["that movie was great!", "that movie stunk"], input_type="text")                                              # unlabeled text
                 predict_proba("/path/to/zip/file.zip", input_type="zip")                                                                     # zip file
                 predict_proba("/path/to/tsv/file.tsv", input_type="tsv")                                                                     # text only

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
        :param dataset: A dataset (can be labeled or unlabeled) with at least 1 uploaded sample, which has 
            the same type as the dataset associated with this classifier.
        :type dataset: :class:`ClassificationData`
        :param unzip_on_client: A flag for indicating if we allow files to be unzipped on the client (improves performance)
        :type unzip_on_client: :mod:`bool`
        :param skip_invalid_values: A flag for indicating whether to just pass over any invalid values
        :type skip_invalid_values: :mod:`bool`
        :param retry_on_timeout: A flag for indicating whether to retry a request if it times out (which can happen if predictions are made on a dataset that is too large).
        :type retry_on_timeout: :mod:`bool`
        :param encoding: A string indicating the encoding of any text that is uploaded (either directly passed as a string, or in a text file)
        :type encoding: :mod:`str`
        :param options: An optional dictionary for specifying any additional prediction parameters (currently only allowed
            option is `compute_stats`, which is a :mod:`bool` indicating if the classifier should update it's statistics
            using the results of these predictions)
        :type options: :mod:`dict`

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a list of `label` and `probabilities tuples, and a `user_value` key which contains the original value 
            uploaded (e.g. the url of an image in the case that `input_type="urls"`). The `user_value` key is 
            important because if `dataset` is used to specify the samples to be predicted, the predictions will 
            not necessarily be returned in the order they were uploaded. The dictionaries can contain additional 
            keys with other information.
        """
        self._verify_input(input_, input_type, dataset)

        if dataset:
            url=BASE_URL + '/api/v1.2/classifiers/' + str(self.id) + '/predict_probabilities'
            data={'dataset_id' : dataset.id}
            data.update(options)
            result = make_request(url, "POST", data=data, message="It looks like you're trying to make too many " + \
                                                                  "predictions at once. Try breaking up your dataset " + \
                                                                  "into smaller chunks and make predictiosn on each of those.")
            result = result["predictions"]

        elif input_:
            url=BASE_URL + '/api/v1.2/classifiers/' + str(self.id) + '/predict_probabilities'
            results = process_input_in_batches(url, input_, input_type, unzip_on_client=unzip_on_client, skip_invalid_values=skip_invalid_values, encoding=encoding, options=options)
            if not all([result.get("predictions") for result in results]):
                return
            results = [result["predictions"] for result in results]
            # combine results into one long list
            result = list(itertools.chain(*results))

        result = self.transform_encoding(result, encoding)

        return result

    def _verify_input(self, input_, input_type, dataset):
        if input_ and dataset:
            raise ValueError("Only one of 'input_' or 'dataset' can be specified, not both.")

        if not dataset and not input_:
            raise ValueError("one of 'dataset' or 'input_' must be specified")

        if input_ and not input_type:
            raise ValueError("'input_type' must be specified if input_ is given")

    def query_and_predict(self, query, encoding='utf-8', options={}):
        """
        Make predictions on a dataset built from a query (e.g. a Twitter search query)

        :param query: A query used for building the dataset (e.g. a Twitter search query)
        :type query: :mod:`str`
        :param encoding: A string indicating the encoding of the query
        :type encoding: :mod:`str`
        :param options: An optional dictionary for specifying any additional prediction parameters. Currently this
            is a placeholder for future parameters.
        :type options: :mod:`dict`

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a `label` key which contains the :mod:`str` name of the predicted label, a `probability` key which
            contains the probability that the specified label is correct, and a key which indicates the value which 
            was predicted on (e.g. for a Twitter classifier, the key is `tweet` and contains the text of the tweet)
            which was predicted on. The dictionaries can contain additional keys with other information.

        Given a query, an entry type, and a trained model, will automatically download data of that type and then 
        run the pretrained model on it.  For example, for 'twitter', you can download a bunch of tweets, then run 
        predictions on them.
        """
        url = BASE_URL + '/api/v1.2/query_and_predict'
        params = dict(entry_type = self.query_type, trained_model_id = self.id, query = query)
        params.update(options)
        result = make_request(url, "POST", data=params)
        predictions = self.transform_encoding(result['predictions'], encoding)
        return predictions

    def query_and_predict_proba(self, query, encoding='utf-8', options={}):
        """
        Make predictions (and return probabilities) on a dataset built from a query (e.g. a Twitter search query)

        :param query: A query used for building the dataset (e.g. a Twitter search query)
        :type query: :mod:`str`
        :param encoding: A string indicating the encoding of the query
        :type encoding: :mod:`str`
        :param options: An optional dictionary for specifying any additional prediction parameters. Currently this
            is a placeholder for future parameters.
        :type options: :mod:`dict`

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a list of `label` and `probabilities tuples, and a `user_value` key which contains the original value 
            uploaded (e.g. the url of an image in the case that `input_type="urls"`). The `user_value` key is 
            important because if `dataset` is used to specify the samples to be predicted, the predictions will 
            not necessarily be returned in the order they were uploaded. The dictionaries can contain additional 
            keys with other information.

        Given a query, an entry type, and a trained model, will automatically download data of that type and then run 
        the pretrained model on it.  For example, for 'twitter', you can download a bunch of tweets, then return the 
        probabilities for each label in the classifier.
        """
        url = BASE_URL + '/api/v1.2/query_and_predict_probabilities'
        params = dict(entry_type = self.query_type, trained_model_id = self.id, query = query)
        params.update(options)
        result = make_request(url, "POST", data=params)
        predictions = self.transform_encoding(result['predictions'], encoding)
        return predictions

    def set_values(self, result):
        """ Sets values on the local classifier instance given results from the api queries.

        :param result: Contains the values to set various :class:`ClassificationModel` attributes, including ["name", "private", "id"]
        :type result: dict
        """
        if('name' in result): self.name=result['name']
        if('private' in result): self.private=result['private']
        if('id' in result): self.id=result['id']
        if('query_type' in result): self.query_type = result['query_type']

    def get_values(self):
        """ Packages the values of the local classifier into a dictionary

        :returns: A dictionary whose keys are the attributes of the :class:`ClassificationModel` object
        """
        result = {}
        params = ["name", "private", "id", "query_type"]
        for param in params:
            if hasattr(self, param):
                if getattr(self, param) is not None:
                    result[param] = getattr(self, param)

        return result

    def clear_values(self):
        """
        Clears values on the local classifier instance.
        """
        self.name = None
        self.private = None
        self.id = None
        self.query_type = None

