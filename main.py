import spacy
from spacy.training import Example
from spacy.scorer import Scorer
import pickle

import json

def load_json_line_gold():
    '''converting json string/file to json-inner-data-representation'''
    json_string = '{ "cars": [\
        {"text": "I like Europe and ice-creams.","meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]},\
        {"text": "I like Europe and ice-creams.","meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]},\
        {"text": "I like Europe and ice-creams.","meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]}\
    ]}'
    gold_obj_json = '{"text": "I like Europe and ice-creams.", "meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]}'
    labelled_obj  = json.loads(json_string)
    gold_obj = json.loads(gold_obj_json)
    return gold_obj

def format_json_line_data_gold(gold_obj):
    '''handling just json-data-structures'''
    loaded_gold_data = [gold_obj['text'], gold_obj['labels']]
    return loaded_gold_data

def load_json_line_labelled():
    '''converting json string/file to json-inner-data-representation'''
    json_string = '{ "cars": [\
        {"meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]},\
        {"meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]},\
        {"meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]}\
    ]}'
    labelled_obj_json = '{"meta": {"ord_id": 91, "fr_id": 0}, "labels": [[7, 13, "GPE"],[18,28,"food"]]}'
    labelled_obj  = json.loads(json_string)
    labelled_obj = json.loads(labelled_obj_json)
    return labelled_obj

def format_json_line_data_labelled(labelled_obj):
    '''handling just json-data-structures'''
    loaded_labelled_data =  labelled_obj['labels']
    return loaded_labelled_data

produce_annotation_files_gold_data = [
    ['I like Europe and ice-creams.', [(7, 13, 'GPE'),(18,28,'food')]],
    ['I like Europe and Africa and chocolate.', [(7, 13, 'GPE'), (18, 24, 'GPE'),(29,38,'food')]],
    ['I like Europe and Africa and Japan.', [(7, 13, 'GPE'), (18, 24, 'GPE'), (29, 34, 'GPE')]]
]
produce_annotation_files_labelled_data = [
    [(7, 13, 'GPE')],
    [(7, 13, 'GPE'),(18,24, 'GPE'),(29,38,'food')],
    [(7, 13, 'GPE'),(18,24, 'GPE')]
]

def produce_annotation_files(gold_data, labelled_data):
    with open('gold.pickle', 'wb') as f:
        pickle.dump(gold_data, f)
    with open('labelled.pickle', 'wb') as f:
        pickle.dump(labelled_data, f)

def init_nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("ner")
    nlp.begin_training()
    return nlp


def evaluate(ner_model, gold_annotations, labelled_data_list):
    scorer = Scorer(ner_model)
    list = []
    i = 0
    for input_textunit_, gold_annot in gold_annotations:
        if labelled_data_list:
            label_list_i = labelled_data_list[i]
            if i + 1 < len(labelled_data_list):
                i = i + 1
        else:
            label_list_i = []
        labelled_ner_textunit = ner_model.make_doc(input_textunit_)
        spans = [ labelled_ner_textunit.char_span(label[0], label[1], label[2]) for label in label_list_i]
        labelled_ner_textunit.ents = spans
        item = Example.from_dict(labelled_ner_textunit, {"entities": gold_annot})
        list.append(item)
    scores = scorer.score(list)
    return scores

def load_pickle_data():
    with open('gold.pickle', 'rb') as f:
        loaded_gold_data = pickle.load(f)
        print("read:", loaded_gold_data)
    with open('labelled.pickle', 'rb') as f:
        loaded_labelled_data = pickle.load(f)
        print("read:", loaded_labelled_data)
        return [loaded_gold_data, loaded_labelled_data]

def load_from_file():
    #return load_pickle_data()
    return [load_json_line_gold(), load_json_line_labelled()]

def format_data(file_data):
    """"
    INTERFACE
     - gold_data = [ ['I like Europe and ice-creams.', [(7, 13, 'GPE'),(18,28,'food')]],
                    ...]
     - labelled_data = [ [(7, 13, 'GPE')],
                    ...]
    returns [gold_data, labelled_data]
    """
    #return file_data
    file_data_gold = file_data[0]
    file_data_labelled = file_data[1]
    gold = format_json_line_data_gold(file_data_gold)
    labelled = format_json_line_data_labelled(file_data_labelled)
    return [[gold], [labelled]]


#produce_annotation_files(produce_annotation_files_gold_data,produce_annotation_files_labelled_data) #used once to produce external files
ner_model = init_nlp()
file_data = load_from_file()
[loaded_gold_data, loaded_labelled_data] = format_data(file_data)
print(ner_model.pipe_names)
results = evaluate(ner_model, loaded_gold_data, loaded_labelled_data)
print(results)