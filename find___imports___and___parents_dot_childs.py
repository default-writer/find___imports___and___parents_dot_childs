import re
import os
import sys

#========================================================================================
# script vyvodit imena failov v ukazannoy papke i pronumerovannye stroki, soderzhaschie zadannyj tekst
# i prednaznachen dlia vyyavleniya vzaimosvyazey mezhdu failami proekta
# (sootvetstvenno, nado iskatj stroki, soderzhaschie slovo import i konstrukzii vida aa.bb(.cc...))
# pri etom, esli import zapisan v neskolko strok (import a,\n b, \n c), budet vyvedena tolko pervaya stroka
# (stroka, v kotoroy estj slovo "import")
# (sm. takzhe poyasneniya k nastroykam:)

######### (Nastroyki - nachalo:) #########

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
path_to_dir_for_analysis = r'.' #r'D:\_Maria\My_python_projects\pythonProject0011_by_Django_docs___First_app__continued\mysite'
extensions_of_files_for_analysis = ['.py', '.htm', '.html', '']   # naprimer ['.py', '.htm', '.html', ''] (s tochkoy v nachale)
# path_to_dir_for_analysis  - bez \ na kontze

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
file_results_out = os.path.splitext(os.path.basename(sys.argv[0]))[0] + "_results.txt"
#  resultat budet vyveden v konsoli
#   - esli   file_results_out = r''   ili   file_results_out = ''   ili   file_results_out = 0
#  resutat budet v sootvetstvuuschem faile
#   - esli file_results_out = r'result.txt'   ili   file_results_out = r'any_path\any_filename'
#       ili   file_results_out = os.path.splitext(os.path.basename(sys.argv[0]))[0] + "_results.txt"
#          (to ectj ot imeni nastoyaschego scripta ubiraem rasshirenie i dobavliaem  _results.txt)


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
file_encoding = "utf-8"       # kodirovka analiziruemyh failov - naprimer 'utf-8'
out_file_encoding = file_encoding  # kodirovka faila s resultatami

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
flag_exclude_comments = 'on'   # 'on'/'off' (for most cases 'on' is ok)
# we can skip comments from inspected files (which is useful if any dots or "import" is present in comments)
# these may be single-string comments (#...)  and multi-string comments ("""...""" and '''...''')
# sadly, those character sequences (#, """, ''') may appear inside string variables (' ... ' i " ... ")
# but for now this is not supported - so if there exist string variables that include #, """ or '''
# one should turn off comments exclusion so that the whole text of .py file would be analyzed

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
vyrazh = re.compile("(?i)(ImPORT)")

# esli    vyrazh = re.compile("([I,i][M,m][P,p][O,o][R,r][T,t])|((\w+)((\.(\w+))+))")
#     ili vyrazh = re.compile("(?i)(ImPORT)|((\w+)((\.(\w+))+))")
#     - to ischetsya "import" (case-insensitive) i "aaa.bbb(.ccc(.ddd.....))" (to estj parent.child....)
#                  (pravda, etomu sootvetstvuut imena_failov.extension tozhe, no eto ne ochenj meshaet)
# esli    vyrazh = re.compile("(?i)(ImPORT)")
#      to ischetsya tolko "import" (case-insensitive)

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
debug_mode = 'off'   # 'on'/'off'
# if 'on', intermediate printouts will be made

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
######### (Nastroyki - konetz) #########
#==================================================================================

def procedure_1_read_file_into_chars():
    # file dlia chteniya otkryvaetsya v main programme
    global amount_of_lines
    global chars_in_lines
    # with open(path_to_current_file, 'rt', encoding=file_encoding) as current_file: - teperj ne nado (eto teperj v main)
    amount_of_lines = 0
    for current_line in current_file:
        amount_of_lines += 1    # schitaem kolichestvo strok v naturalnom vide
    if debug_mode == 'on': print("amount_of_lines", amount_of_lines)
    # objavliaem massiv symvolov (pustoy, poka tolko kolichestvo strok zadaem):
    chars_in_lines = [''] * amount_of_lines              # bylo  [''] * amount_of_lines
    for line_number in range(0, amount_of_lines):        # poka numeraziya s 0
        chars_in_lines[line_number] = [line_number]      # bylo [line_number, '']
        # no nado, chtoby stroki (lines) numerovalisj s 1 - kak v IDE - ETO POTOM
    if debug_mode == 'on': print("chars_in_lines", chars_in_lines)
    if debug_mode == 'on': print("===============")

    current_file.seek(0)   # vozvrat k nachalu faila

    line_number = -1
    for current_line in current_file:
    # =============== for line_number in range(amount_of_lines):
        line_number += 1
        # there are no lines with zero length: at least a line contains EOL
        line_length_overall = len(current_line)
        # print("line_length_overall   ", line_length_overall)
        start_in_string = 0
        end_in_string = line_length_overall - 1
        # even for the last string read adds \n (if there wasn't) - so every string ends in \n
        # though this may be platform-specific - so watch it
        for s in range(start_in_string, end_in_string):
            #print("s", s)
            chars_in_lines[line_number].append(current_line[s])

# =======================================================================================

def procedure_2_replace_comments_with_spaces():
    global chars_in_lines
    # eto pered pereborom po strokam, tk takie kommentarii mb mnogostrochnymi
    flag_open_triple_single_quotes = 0
    flag_close_triple_single_quotes = 0

    flag_open_triple_double_quotes = 0
    flag_close_triple_double_quotes = 0

    for i in range(0, amount_of_lines):
        amount_of_items = len(chars_in_lines[i]) - 1 # potomy chto pervyy element - nomer stroki (s 0)
        last_item_plus_1 = amount_of_items + 1

        flag_hash = 0

        items_to_replace_with_spaces = []
        uncertain_single_qs = []
        uncertain_double_qs = []

        previous_char = ''         # pustoy
        before_previous_char = ''  # pustoy

        count_singles = 0
        count_doubles = 0

        for k in range(1, last_item_plus_1):
            current_char = chars_in_lines[i][k]

            if ((flag_hash == 1) or
                (flag_open_triple_single_quotes == 1 and flag_close_triple_single_quotes == 0
                and current_char !="'") or
                (flag_open_triple_double_quotes == 1 and flag_close_triple_double_quotes == 0
                and current_char !='"')):

                items_to_replace_with_spaces.append(k)

            if current_char == "#":
                flag_hash = 1

            # dalee pro triple single quote comments dva bloka:
            if current_char == "'":
                if previous_char != "'":
                    uncertain_single_qs.append(k)
                    count_singles = 1
                else:       # to estj esli previous_char == "'"
                    if before_previous_char != "'":
                        uncertain_single_qs.append(k)
                        count_singles = 2
                    else:       # to estj esli previous_char == "'" i before_previous_char == "'"
                        # uncertain_single_qs.append(k) ne delaem, a naoborot, ochishaem:
                        uncertain_single_qs.clear()
                        count_singles += 1 # nelzya pisatj = 3, tk mb boljshe kavychek podryad (to estj budet libo 3, libo otschet snachala posle obnuleniya)


            if count_singles == 3:
                if (flag_open_triple_single_quotes == 0):
                    flag_open_triple_single_quotes = 1
                    flag_close_triple_single_quotes = 0
                    count_singles = 0
                else:
                    flag_open_triple_single_quotes = 0
                    flag_close_triple_single_quotes = 1
                    count_singles = 0


            # dalee pro triple double quote comments dva bloka:
            if current_char == '"':
                if previous_char != '"':
                    uncertain_double_qs.append(k)
                    count_doubles = 1
                else:       # to estj esli previous_char == '"'
                    if before_previous_char != '"':
                        uncertain_double_qs.append(k)
                        count_doubles = 2
                    else:       # to estj esli previous_char == '"' i before_previous_char == '"'
                        # uncertain_single_qs.append(k) ne delaem, a naoborot, ochishaem:
                        uncertain_double_qs.clear()
                        count_doubles += 1 # nelzya pisatj = 3, tk mb boljshe kavychek podryad (to estj budet libo 3, libo otschet snachala posle obnuleniya)

            if count_doubles == 3:
                if (flag_open_triple_double_quotes == 0):
                    flag_open_triple_double_quotes = 1
                    flag_close_triple_double_quotes = 0
                    count_doubles = 0
                else:
                    flag_open_triple_double_quotes = 0
                    flag_close_triple_double_quotes = 1
                    count_doubles = 0

            before_previous_char = previous_char
            previous_char = current_char   # v takom imenno poryadke

        amount_of_uncertain_single_qs = len(uncertain_single_qs)
        for i_usq in range(0, amount_of_uncertain_single_qs):
            items_to_replace_with_spaces.append(uncertain_single_qs[i_usq])

        amount_of_uncertain_double_qs = len(uncertain_double_qs)
        for i_udq in range(0, amount_of_uncertain_double_qs):
            items_to_replace_with_spaces.append(uncertain_double_qs[i_udq])

        amount_to_replace = len(items_to_replace_with_spaces)
        for i_r in range(0, amount_to_replace):
            item_number = items_to_replace_with_spaces[i_r]
            chars_in_lines[i][item_number] = ' '  # ili 'X' dlia naglyadnosti mozhno


        if debug_mode == 'on': print(chars_in_lines[i])   # eto uzhe s zamenennymi kommentariyami
        del items_to_replace_with_spaces
        del uncertain_single_qs
        del uncertain_double_qs
        # pri etom sami troinye kavychki i # ne udaliaem - a to mozhno kod isportitj

# escho vozmozhen variant, kogda vse eto vnutri prostyh kavychek - eto potom
#========================================================================================


# teperj ischem parents_dot_childs i imports
def procedure_3_with_regexp_find_and_print_relations():
    target_line_numbers_from_zero = []
    #teperj ischem parents_dot_childs i imports
    for i in range(0, amount_of_lines):

        amount_of_items = len(chars_in_lines[i]) - 1  # potomy chto pervyy element - nomer stroki (s 0)
        last_item_plus_1 = amount_of_items + 1
        string = ''
        for k in range(1, last_item_plus_1):
            string += str(chars_in_lines[i][k])
        if debug_mode == 'on': print(str(string))
        answer = ''
        try:
            answer = vyrazh.search(string).group()
        except:
            pass
        if answer:
            # print('match found:', answer)
            target_line_numbers_from_zero.append(chars_in_lines[i][0])

    if debug_mode == 'on': print(target_line_numbers_from_zero)

    for i in target_line_numbers_from_zero:
        amount_of_items = len(chars_in_lines[i]) - 1  # potomy chto pervyy element - nomer stroki (s 0)
        last_item_plus_1 = amount_of_items + 1
        string = ''
        for k in range(1, last_item_plus_1):
            string += str(chars_in_lines[i][k])
        line_number_from_1 = i + 1  # byli s 0, a nado vyvesti s 1, t.k. v IDE nomera nachinautsya s 1
        if file_results_out:       # to estj esli file_out zadan
            with open(file_results_out, 'at', encoding=out_file_encoding) as results_file:
                print('(', line_number_from_1, ') ', string, file=results_file)
        else:              # esli file_out ne zadan, vyvodim v konsolj
            print('(', line_number_from_1, ') ', string)

#========================================================================================

# sobiraem:
if __name__ == '__main__':
    # obnuliaem ili sozdaem fail s resultatami:
    if file_results_out:  # to estj esli file_out zadan
        with open(file_results_out, 'wt', encoding=out_file_encoding) as results_file:
            pass
    for walk_root, _, walk_files in os.walk(path_to_dir_for_analysis):
        for walk_file in walk_files:
            path_to_current_file = os.path.join(walk_root, walk_file)
            _, current_extension = os.path.splitext(path_to_current_file)
            if debug_mode == 'on': print(current_extension, path_to_current_file)
            if current_extension in extensions_of_files_for_analysis:
                with open(path_to_current_file, 'rt', encoding=file_encoding) as current_file:
                    if current_file.readable():

                        procedure_1_read_file_into_chars()
                        if flag_exclude_comments == 'on':
                            procedure_2_replace_comments_with_spaces()
                        if file_results_out:  # to estj esli file_out zadan - risuem razgranichitelj i imya faila pishem
                            with open(file_results_out, 'at', encoding=out_file_encoding) as results_file:
                                print('\n', '====================================================================', '\n',
                                    path_to_current_file, '\n', file=results_file)
                        else:
                            print('\n', '====================================================================', '\n',
                                  path_to_current_file, '\n')
                        procedure_3_with_regexp_find_and_print_relations()


