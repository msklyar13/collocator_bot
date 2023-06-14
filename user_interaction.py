import dict_functions
import dict_fill

# обробити текст та додати нові іменниково-прикметникові пари до словника


def user_text_to_dict(text):
    dict_fill.db_fill_update(dict_fill.nlp_text_to_dict(text))
    print(f'''Базу даних оновлено. Знайдені словосполучення:
{dict(dict_fill.nlp_text_to_dict(text))}''')
    return

# user_text_to_dict(input('Введіть текст без абзаців для обробки та наповнення словника словосполучень: '))


# вивести весь словник (лематизований іменник: лематизовані прикметники)
def user_print_dict(dictionary):
    print('Всі іменниково-приметникові пари:')
    for noun, adjs in dictionary.items():
        print(f'{noun}: {adjs}')
    return

# user_print_dict(dict_fill.fetch_db_noun_adjs())


# вивести всі іменникаи словника (лематизовані)
def user_print_nouns(dictionary):
    print('Наявні в словнику іменники:')
    for noun in dictionary:
        print(noun)
    return

# user_print_nouns(dict_fill.fetch_db_noun_adjs())


# вивести прикметники до іменника за запитом  (лематизований іменник: прикметники)
def user_adjs_by_noun(noun):
    if noun in dict_fill.exact_noun_adjs(noun):
        print(dict_fill.exact_noun_adjs(noun)[noun])
    else:
        print('Іменника немає в словнику словосполучень.')
    return

# user_adjs_by_noun(input('Введіть іменник для пошуку: '))
