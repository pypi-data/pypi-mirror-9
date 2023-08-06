from .utils import get_user_id, get_session, BASE_URL, validate_result
from classification_data import ClassificationData
from classification_model import ClassificationModel
import json

# contains various user operations

def _get_all_results(url, filters):
    params = dict(q=json.dumps(dict(filters=filters)), results_per_page=-1)
    response = get_session().get(url, params=params)
    result = validate_result(response)
    results = result["objects"]

    if result["total_pages"] > 1:
        # asking for all results at once didn't work.  request all available pages
        for page in xrange(2, result["total_pages"] + 1):
            params = dict(q=json.dumps(dict(filters=filters)), results_per_page=-1, page=page)
            response = get_session().get(url, params=params)
            result = validate_result(response)
            results.extend(result["objects"])

    return results


def list_datasets():
    """
    Returns identifiers to the users datasets
    """
    user_id = get_user_id()

    url = BASE_URL + "/api/datasets"
    filters = [dict(name='user_id', op='eq', val=user_id)]

    return [ClassificationData(id=d["id"], verbose=False) for d in _get_all_results(url, filters)]

def list_classifiers():
    """
    Returns identifiers to the users datasets
    """
    user_id = get_user_id()

    url = BASE_URL + "/api/classifiers"
    filters = [dict(name='user_id', op='eq', val=user_id)]

    return [ClassificationModel(id=m["id"]) for m in _get_all_results(url, filters)]

def delete_dataset(dataset):
    """
    Deletes the dataset with the given dataset id
    """
    url = BASE_URL + "/api/datasets/%d"%(dataset.id)
    response = get_session().delete(url)
    if len(response.text) > 0:
        result = validate_result(response)

    dataset.clear_values()

def delete_classifier(classifier):
    """
    Deletes the model with given model id
    """
    url = BASE_URL + "/api/classifiers/%d"%(classifier.id)
    response = get_session().delete(url)
    if len(response.text) > 0:
        result = validate_result(response)

    classifier.clear_values()
