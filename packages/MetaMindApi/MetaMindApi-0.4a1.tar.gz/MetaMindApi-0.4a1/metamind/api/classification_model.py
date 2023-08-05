import os
import time
import itertools
from json import dumps, loads

from .utils import check_api_key, get_session, validate_result, BASE_URL, \
                   repackage_input, process_input_in_batches

class ClassificationModel:
    """ A local representation of a MetaMind trainable classifier resource. """
    
    def __init__(self, name=None, private=None, id=None):
        """
        Creates a classifier local instance. 

        :param name: The name of the trainable classifier (will be updated on the server)
        :type name: str
        :param private: Whether or not the dataset is private
        :type private: bool
        :param id: The id of the classifier resource to have this local representation mirror
        :type id: int

        If a valid id is specified, the instance points to the 
        corresponding classifier. Otherwise, the reference is left unspecified 
        until the classifier is fitted to a dataset.
        """

        if id:
            if isinstance(id,str):
                result = {'id' : id}
            else:
                url=BASE_URL + '/api/v1.1/classifiers/%d'%(id);
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

        :param dataset: The dataset that will be fit. The dataset must have at least two classes.
        :type dataset: :class:`ClassificationData`
        :param options: A dictionary for fine-grained control of the training parameters. Currently, 
            the only allowed key is `test_dataset_id`, which must have the value of a valid dataset_id
            that is of the same type as `dataset`
        :type options: :mod:`dict`

        Fitting is performed asynchronously. Hence, fit_async() does not block.  In order to check the 
        training progress call status(). Training must finish before any predictions 
        can be made. Training can be stopped at any time by calling halt(). Note that if an id 
        was not specified in the ClassificationModel constructor, a new classifier is created.
        """
        if(self.id):
            url=BASE_URL + '/api/v1.1/classifiers/%d/fit'%(self.id)
        else:
            url=BASE_URL + '/api/v1.1/classifiers/fit'

        data=self.get_values()
        data['train_dataset_id']=dataset.id
        data.update(options)

        response=get_session().post(url,data=dumps(data))
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
        
        url=BASE_URL + '/api/v1.1/classifiers/%d/halt'%(self.id)

        response=get_session().post(url)
        
    def fit(self, dataset, options={}, verbosity=1):
        """
        Fit the classifier to the specified dataset, and wait until training is finished to return.

        :param dataset: The dataset that will be fit. The dataset must have at least two classes.
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
            header_printed = False
            while(True):
                status = self.status()
                stats = self.stats()

                if (time.time()-last_update)>interval_update:
                    if status=='submitted':
                        print "Your model is in the training queue!"

                    if stats:
                        if (stats["iteration"][-1]-last_iter)>=interval_iter:
                            if verbosity == 1:
                                print "Estimated minutes left in training: %6.2f"%stats["time_left"][-1]
                            elif verbosity == 2:
                                if not header_printed:
                                    print "est. time remaining (min)     iter     cost        training accuracy"
                                    header_printed = True
                                print "%-29.2f %-8d %-11f %-24f" % tuple([stats["time_left"][-1], stats["iteration"][-1], stats["cost"][-1], stats["train_accuracy"][-1]])
                            last_iter = stats["iteration"][-1]
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
        url_status=BASE_URL + '/api/v1.1/classifiers/%d/status'%(self.id)

        response=get_session().get(url_status)
        result = validate_result(response)

        return result["status"]

    def stats(self):
        """
        Retrieve the classifier training training stats.

        :returns: A :mod:`list` of sublists. Each sublist contains `[est_min_remaining, iteration, cost, train_accuracy]`

        Note that the `test_accuracy` is only updated periodically and maybe not reflect the current accuracy of 
        the classifier while training.
        """
        url_status=BASE_URL + '/api/v1.1/classifiers/%d/status'%(self.id)

        response=get_session().get(url_status)
        result = validate_result(response)

        return result["stats"]
        
    def predict(self, input_=None, dataset=None, is_tsv=False, unzip_on_client=True, skip_invalid_values=False):
        """
        Predict the class of the samples of either the specified dataset or a list of files.

        :param input_: This parameter can have multiple forms, illustrated by these examples:
        
            **Image Classifiers**::

                 predict([("/path/to/file1.jpg", "my label"), ("/path/to/file2.jpg", "my other label")])            # labeled files
                 predict(["/path/to/file1.jpg", "/path/to/file2.jpg"])                                              # unlabeled files
                 predict([("http://url/to/file1.png", "my label"), ("http://url/to/file2.tiff", "my other label")]) # labeled urls
                 predict(["http://url/to/file1.png", "http://url/to/file2.tiff"])                                   # unlabeled urls
                 predict("/path/to/zip/file.zip")                                                                   # zip file
                 predict("https://www.dropbox.com/sh/some/link?dl=0")                                               # a public dropbox link

            **Text Classifiers**::

                 predict([("that movie was great!", "positive"), ("that movie stunk", "negative")])                 # labeled text
                 predict(["that movie was great!", "that movie stunk"])                                             # unlabeled text
                 predict("/path/to/zip/file.zip")                                                                   # zip file
                 predict("https://www.dropbox.com/sh/some/link?dl=0")                                               # a public dropbox link
                 predict("/path/to/tsv/file.tsv",is_tsv=True)                                                       # text only

            Note that tsv files must be arranged in two columns with the first containing the label and the second containing the sample

            Note that zip files and Dropbox links must have the following directory structure:

                my_data/
                    label1/
                        first_image.jpg
                        second_image.jpg
                    label2/
                        third_image.jpg
                        fourth_image.jpg
                        fifth_image.jpg

        :type input_: :mod:`list` or :mod:`str`
        :param dataset: A dataset (can be labeled or unlabeled) with at least 1 uploaded sample, which has 
            the same type as the dataset associated with this classifier.
        :type dataset: :class:`ClassificationData`
        :param is_tsv: A flag for indicating if the uploaded files is a .tsv file or not
        :type is_tsv: bool
        :param skip_invalid_values: A flag for indicating whether to just pass over any invalid values
        :type skip_invalid_values: bool

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a `class` key which contains the :mod:`str` name of the predicted class, a `probability` key which
            contains the probability that the specified class is correct, and a `user_value` key which contains
            the original value uploaded (in the case of `image` data, this is the filename/url of the sample; in
            the case of `text` data, this is the text of the sample). The `user_value` key is important because if
            `dataset` is used to specify the samples to be predicted, the predictions will not necessarily be returned
            in the order they were uploaded. The dictionaries can contain additional keys with other information.
        """
        if input_ and dataset:
            raise ValueError("Only one of 'input_' or 'dataset' can be specified, not both.")

        if not dataset and not input_:
            raise ValueError("one of 'dataset' or 'input_' must be specified")

        if dataset:
            url=BASE_URL + '/api/v1.1/classifiers/' + str(self.id) + '/predict'
            data={'dataset_id' : dataset.id}
            response=get_session().post(url,data=dumps(data))
            result = validate_result(response)
            result = result["predictions"]

        elif input_:
            url=BASE_URL + '/api/v1.1/classifiers/' + str(self.id) + '/predict_streaming'
            input_ = repackage_input(input_,unzip_on_client)
            results = process_input_in_batches(url, input_, is_tsv=is_tsv, skip_invalid_values=skip_invalid_values)
            results = [result["predictions"] for result in results]
            # combine results into one long list
            result = list(itertools.chain(*results))

        return result

    def predict_proba(self, input_=None, dataset=None, is_tsv=False, unzip_on_client=True, skip_invalid_values=False):
        """
        Predict the probabilities for each class for each of the samples of a dataset, a single file or a list of files.

        :param input_: This parameter can have multiple forms, illustrated by these examples:
        
            **Image Classifiers**::

                 predict([("/path/to/file1.jpg", "my label"), ("/path/to/file2.jpg", "my other label")])            # labeled files
                 predict(["/path/to/file1.jpg", "/path/to/file2.jpg"])                                              # unlabeled files
                 predict([("http://url/to/file1.png", "my label"), ("http://url/to/file2.tiff", "my other label")]) # labeled urls
                 predict(["http://url/to/file1.png", "http://url/to/file2.tiff"])                                   # unlabeled urls
                 predict("/path/to/zip/file.zip")                                                                   # zip file
                 predict("https://www.dropbox.com/sh/some/link?dl=0")                                               # a public dropbox link

            **Text Classifiers**::

                 predict([("that movie was great!", "positive"), ("that movie stunk", "negative")])                 # labeled text
                 predict(["that movie was great!", "that movie stunk"])                                             # unlabeled text
                 predict("/path/to/zip/file.zip")                                                                   # zip file
                 predict("https://www.dropbox.com/sh/some/link?dl=0")                                               # a public dropbox link
                 predict("/path/to/tsv/file.tsv",is_tsv=True)                                                       # text only

            Note that zip files and Dropbox links must have the following directory structure::

                my_data/
                    label1/
                        first_image.jpg
                        second_image.jpg
                    label2/
                        third_image.jpg
                        fourth_image.jpg
                        fifth_image.jpg

        :type input_: :mod:`list` or :mod:`str`
        :param dataset: A dataset (can be labeled or unlabeled) with at least 1 uploaded sample, which has 
            the same type as the dataset associated with this classifier.
        :type dataset: :class:`ClassificationData`
        :param is_tsv: A flag for indicating if the uploaded files is a .tsv file or not
        :type is_tsv: bool

        :returns: A list of dictionaries, each of which correspond to a prediction. Each prediction will include 
            a list of `class` and `probabilities pairs, and a `user_value` key which contains 
            the original value uploaded (in the case of `image` data, this is the filename/url of the sample; in 
            the case of `text` data, this is the text of the sample). The `user_value` key is important because if 
            `dataset` is used to specify the samples to be predicted, the predictions will not necessarily be returned
            in the order they were uploaded. The dictionaries can contain additional keys with other information.
        """
        if input_ and dataset:
            raise ValueError("Only one of 'input_' or 'dataset' can be specified, not both.")

        if not dataset and not input_:
            raise ValueError("one of 'dataset' or 'input_' must be specified")

        if dataset:
            url=BASE_URL + '/api/v1.1/classifiers/' + str(self.id) + '/predict_probabilities'
            data={'dataset_id' : dataset.id}
            response=get_session().post(url,data=dumps(data))
            result = validate_result(response)
            result = result["predictions"]

        elif input_:
            url=BASE_URL + '/api/v1.1/classifiers/' + str(self.id) + '/predict_probabilities_streaming'
            input_ = repackage_input(input_,unzip_on_client)
            results = process_input_in_batches(url, input_, is_tsv=is_tsv, skip_invalid_values=skip_invalid_values)
            results = [result["predictions"] for result in results]
            # combine results into one long list
            result = list(itertools.chain(*results))

        return result

    def test(self, input_=None, dataset=None, is_tsv=False, normalize=True):
        """
        A wrapper around :func:`ClassificationModel.predict`, which returns the accuracy of the predictions instead of the
        predictions themselves.

        :param input_: Same as `input_` in :func:`ClassificationData.add_samples`
        :type input_: :mod:`list` or :mod:`str`
        :param dataset: A dataset (can be labeled or unlabeled) with at least 1 uploaded sample, which has 
            the same type as the dataset associated with this classifier.
        :type dataset: :class:`ClassificationData`
        :param is_tsv: A flag for indicating if the uploaded files is a .tsv file or not
        :type is_tsv: bool
        :param normalize: If `normalize == True`, the accuracy is returned as a fraction of the total number of samples. 
            Otherwise, the number of samples correct is returned.
        :type normalize: bool

        :returns: The accuracy of classifier on the given dataset (either fraction correct or number of samples correct,
            depending on the value of `normalize`)
        """
        if input_ and dataset:
            raise ValueError("Only one of 'input_' or 'dataset' can be specified, not both.")

        if not dataset and not input_:
            raise ValueError("One of 'dataset' or 'input_' must be specified")

        # this is a nice wrapper around our predict function, but it doesn't call
        # have any more routes than predict. Thus, we need to do some validation
        # to make sure the data is labeled.
        if input_:
            r_input = repackage_input(input_)
            if not all([(inp[1] is None) for inp in r_input]):
                raise ValueError("Every example in 'input_' must be labeled. " + 
                                 "The following examples were not labeled: " + 
                                 str([inp[0] for inp in r_input if inp[1] is None]))

        if dataset and not dataset.is_labeled:
            raise ValueError("if dataset is specified, it must be labeled")

        predictions = self.predict(input_=input_, dataset=dataset, is_tsv=is_tsv)

        num_samples = len(predictions)

        if input_:
            num_correct = sum([int(pred["class"] == inp[1]) for pred,inp in zip(predictions,input_)])
        elif dataset:
            num_correct = sum([int(pred["class"] == pred["correct_label"]) for pred in predictions])

        return float(num_correct)/float(num_samples)


    def set_values(self, result):
        """ Sets values on the local classifier instance given results from the api queries.

        :param result: Contains the values to set various :class:`ClassificationModel` attributes, including ["name", "private", "id"]
        :type result: dict
        """
        if('name' in result): self.name=result['name']
        if('private' in result): self.private=result['private']
        if('id' in result): self.id=result['id']

    def get_values(self):
        """ Packages the values of the local classifier into a dictionary

        :returns: A dictionary whose keys are the attributes of the :class:`ClassificationModel` object
        """
        result = {}
        params = ["name", "private", "id"]
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

