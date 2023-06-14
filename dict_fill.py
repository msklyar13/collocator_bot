import re
import collections
from collections import defaultdict
from collections import Counter
import stanza
import sqlite3
import dict_functions
nlp = stanza.Pipeline(lang='uk', processors='tokenize,mwt,pos,lemma,depparse')


# пропускаємо текст через nlp пайплайн, оброблюємо та вилучаємо всі пари іменник -- прикметники (списком із дублікатами)
def nlp_text_to_dict(text):
    doc = nlp(text)
    all_noun_adjs = defaultdict(list)
    [all_noun_adjs[sent.words[word.head-1].lemma.lower()].append(word.lemma)
     for sent in doc.sentences for word in sent.words if word.deprel == 'amod']
    return all_noun_adjs


# під'єднуємося до БД, визначаємо курсор
conn = sqlite3.connect(
    'collocations.db', check_same_thread=False)
c = conn.cursor()
# видаляємо таблицю, якщо створюватимемо її наново
#c.execute('''DROP TABLE IF EXISTS adjs_for_noun''')

# створюємо таблицю, якщо вона ще не існує
c.execute('''CREATE TABLE IF NOT EXISTS adjs_for_noun (
        noun_id INTEGER PRIMARY KEY,
        noun VARCHAR(25),
        noun_gender VARCHAR(5),
        adjs TEXT)
        ''')


def db_fill_update(default_dictionary):
    # встановлюємо айді як 1 (якщо таблиця пуста) або як останнє айді + 1 (якщо в вже таблиці є дані)
    c.execute('''SELECT MAX(noun_id) AS maximum_id FROM adjs_for_noun''')
    if c.fetchone()[0] == None:
        noun_id = 1
    else:
        c.execute('''SELECT MAX(noun_id) AS maximum_id FROM adjs_for_noun''')
        noun_id = int(c.fetchone()[0]) + 1

    # заповнюємо таблицю: створюємо рядки для нових іменників...
    for i in range(0, len(default_dictionary)):
        c.execute(
            '''SELECT noun_id FROM adjs_for_noun WHERE noun = ?''', (list(default_dictionary.keys())[i], ))
        if c.fetchone() == None:
            c.execute('''INSERT INTO adjs_for_noun VALUES (?, ?, ?, ?)''',
                      (noun_id,
                       list(default_dictionary.keys())[i],
                       dict_functions.gender(
                           list(default_dictionary.keys())[i]),
                       " ".join(list(default_dictionary.values())[i])

                       )
                      )
            noun_id += 1
    # ...або оновлюємо існуючі, якщо іменник вже є в таблиці
        else:
            c.execute('''SELECT adjs FROM adjs_for_noun WHERE noun= ?''',
                      (list(default_dictionary.keys())[i],))
            upd_adj = str(c.fetchone()[0]) + ' ' + \
                ' '.join(list(default_dictionary.values())[i])
            c.execute(
                '''UPDATE adjs_for_noun SET adjs = ? WHERE noun = ?''', (upd_adj, list(default_dictionary.keys())[i],))
    conn.commit()
    return


'''
# відкриваємо файл та зчитуємо текст із нього
f = open(
    'input_text.txt', encoding='utf-8')
input_text = f.read().lower().replace('\n', ' ')
f.close()

# автоматично заповнюємо БД з поточного файлу даними з input_text
db_fill_update(nlp_text_to_dict(input_text))
'''

conn = sqlite3.connect(
    'collocations.db', check_same_thread=False)
c = conn.cursor()


# із даних БД укладаємо унікальний словник за допомогою функції з файлу dict_functions
def fetch_db_noun_adjs():
    output_noun_adjs = defaultdict(list)
    c.execute('''SELECT noun, adjs FROM adjs_for_noun''')
    for i in c.fetchall():
        output_noun_adjs[i[0]] = i[1].split()
    return dict_functions.unique_adjs_for_noun(output_noun_adjs)


# із даних БД вилучаємо всі прикметники до іменника переданого в змінній у функцію
def exact_noun_adjs(noun):
    output_exact_noun_adjs = defaultdict(list)
    c.execute('''SELECT noun, adjs FROM adjs_for_noun WHERE noun = ?''', (noun,))
    for i in c.fetchall():
        adjs = []
        [adjs.append(dict_functions.adjust_gender(i[0], adj))
         for adj in i[1].split()]
        output_exact_noun_adjs[i[0]] = adjs
    return dict_functions.unique_adjs_for_noun(output_exact_noun_adjs)


conn.commit()


# функція запису у файл (за потреби)
def user_record_dict(dictionary):
    record_noun_adjs = input('''Записати базу даних у файл? (+/-) ''')
    if record_noun_adjs == '+':
        with open('adjs_for_noun.txt', 'w') as f:
            for key, value in dictionary.items():
                f.write(f'{key}: {value}\n')
        print('Базу даних записано.')
    else:
        print('Не записуємо. Дякую за звернення')
    return
