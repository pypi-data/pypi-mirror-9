def compareTaggers(model1, model2, string_list, module_name):
    """
    Compare two models. Given a list of strings, prints out tokens & tags
    whenever the two taggers parse a string differently. This is for spot-checking models
    :param tagger1: a .crfsuite filename
    :param tagger2: another .crfsuite filename
    :param string_list: a list of strings to be checked
    :param module_name: name of a parser module
    """
    module = __import__(module_name)

    tagger1 = pycrfsuite.Tagger()
    tagger1.open(module_name+'/'+model1)
    tagger2 = pycrfsuite.Tagger()
    tagger2.open(module_name+'/'+model2)

    count_discrepancies = 0

    TAGGER = tagger1

    for string in string_list: