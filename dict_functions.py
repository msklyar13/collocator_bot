import re
import collections
from collections import defaultdict
from collections import Counter
import stanza

nlp = stanza.Pipeline(lang='uk', processors='tokenize,mwt,pos,lemma,depparse')


# визначаємо рід іменника та повртаємо його на виході з функції
def gender(noun):
    n = nlp(noun)
    properties = str([word.feats
                      for sent in n.sentences for word in sent.words])
    base_num = re.compile('Sing|Ptan')
    match_num = base_num.search(properties)

    base_gender = re.compile('Masc|Fem|Neut')
    match_gender = base_gender.search(properties)
    if match_num is not None and match_num.group() == 'Ptan':
        return match_num.group()
    elif match_gender == None:
        pass
    else:
        return match_gender.group()


# додаємо блок узгодження роду прикметника та іменника
def adjust_gender(noun, adj_to_change):
    if gender(noun) == 'Masc':
        # повертаємо як є (вихідна лематизована форма -- ч.р.), якщо іменник в ч.р.
        return adj_to_change
    elif gender(noun) == 'Ptan':
        plur_adj = re.sub('ий', 'і', adj_to_change)
        return plur_adj  # якщо множина -- закінчення -і
    elif adj_to_change.endswith('ий'):
        if gender(noun) == 'Fem':  # якщо ж.р. -- закінчення -а
            femn_adj = re.sub('ий', 'а', adj_to_change)
            return femn_adj
        elif gender(noun) == 'Neut':  # якщо с.р. -- закінчення -е
            neut_adj = re.sub('ий', 'е', adj_to_change)
            return neut_adj
    elif adj_to_change.endswith('ій'):  # те саме для м'якої групи
        if gender(noun) == 'Fem':
            femn_adj = re.sub('ій', 'я', adj_to_change)
            return femn_adj
        elif gender(noun) == 'Neut':
            neut_adj = re.sub('ій', 'є', adj_to_change)
            return neut_adj
    else:
        pass


# вилучаємо дублікати прикметників з укладеного словника, укладаючи прикметники за частотою
def unique_adjs_for_noun(dictionary):
    unique_adjs_dict = {}
    for i in range(0, len(dictionary)):
        unique_adjs_dict[list(dictionary.keys())[i]] = [value for value,
                                                        count in Counter(list(dictionary.values())[i]).most_common()]
    return unique_adjs_dict
