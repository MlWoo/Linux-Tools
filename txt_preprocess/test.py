#coding= utf-8
import re
import numpy as np

full_text_path = "sdpz_full.txt"
part_text_path = "sorted_sdpz.txt"

float_range = 8

def length(s0, s1):
    if s0 is None:
        raise TypeError("Argument s0 is NoneType.")
    if s1 is None:
        raise TypeError("Argument s1 is NoneType.")
    first_idx = None
    s0_len, s1_len = len(s0), len(s1)
    x, y = s0[:], s1[:]
    n, m = s0_len + 1, s1_len + 1
    matrix = np.zeros((n, m))
    max_i = 1
    max_j = 1
    for i in range(1, s0_len + 1):
        for j in range(1, s1_len + 1):
            if x[i - 1] == y[j - 1]:
                if first_idx is None:
                    first_idx = (i-1, j-1)
                if max_i < i and max_j <= j:
                    max_i = i
                    max_j = j
                matrix[i][j] = matrix[i - 1][j - 1] + 1
            else:
                matrix[i][j] = max(matrix[i][j - 1], matrix[i - 1][j])
    last_idx = (max_i - 1, max_j - 1)
    return matrix[s0_len][s1_len], first_idx, last_idx


def get_most_match_text_single(ref_txt, recog_text):
    ambiguous = True
    min_idx = max(0, len(recog_text) - float_range)
    max_idx = min(len(ref_txt), len(recog_text) + float_range)
    if min_idx+1 >= max_idx:
        return ref_txt[:len(recog_text)],  ambiguous, (0, 0)
    else:
        all_ref_txt = [ref_txt[:x+1] for x in range(min_idx, max_idx)]
        best_lcs = 0
        match_text = all_ref_txt[0]
        for i, one_ref_txt in enumerate(all_ref_txt):
            length_str, first_idx, last_idx = length(one_ref_txt, recog_text)
            length_str = int(length_str)
            if length_str > best_lcs:
                best_lcs = length_str
                match_text = one_ref_txt
            elif length_str == best_lcs and best_lcs > 0:
                if last_idx[0] == len(ref_txt) - 1:
                    match_text = ref_txt[:last_idx[0]+1]
                    ambiguous = True
                elif last_idx[1] == len(recog_text) - 1:
                    match_text = ref_txt[:last_idx[0]+1]
                    ambiguous = False
                    break
                else:
                    match_text = ref_txt[:len(recog_text)]
        if best_lcs == 0:
            match_text = ref_txt[:len(recog_text)]
        return match_text, ambiguous, first_idx


def get_most_match_text_multiple(ref_txt_m, recog_text_0, recog_text_1):
    match_text, ambiguous, _ = get_most_match_text_single(ref_txt_m, recog_text_0)
    if ambiguous or match_text[-1] == '的':
        len_match_text = len(match_text)
        match_text_last_float = ref_txt_m[len_match_text-float_range:len_match_text+float_range]
        recog_text_1_fist_float = recog_text_1[:float_range]
        length_str, first_idx, last_idx = length(recog_text_1_fist_float, match_text_last_float)
        if int(length_str) > 1:
            if last_idx[1] - first_idx[1] < last_idx[0] - first_idx[0]:
                match_text = ref_txt_m[0: len_match_text - float_range + first_idx[1]]
            else:
                match_text = ref_txt_m[0: len_match_text-float_range+last_idx[1]-last_idx[0]]

    return match_text


def correct_text_auto(ref_full_txt, correct_txt_list, recog_txt_list, audio_name_list, chapter_idx):
    correct_list = []
    correct_line = 0
    last_end_idx = 0
    for i, recog_text in recog_txt_list:
        if correct_line < len(most_correct_list):
            correct_no, correct_idx, correct_text = correct_txt_list[correct_line]
            if i == correct_no:
                correct_line += 1
                last_end_idx = correct_idx + len(correct_text)
                correct_list.append((i, recog_text, recog_text, audio_name_list[i]))
                print("correct line", i, correct_text, last_end_idx)
            elif i == correct_no - 1:
                ref_txt = ref_full_txt[last_end_idx:correct_idx]
                last_end_idx = last_end_idx + len(ref_txt)
                correct_list.append((i, ref_txt, recog_text, audio_name_list[i]))
                print("modify line", i, ref_txt, last_end_idx)
            elif i < correct_no:
                ref_txt = ref_full_txt[last_end_idx:correct_idx]
                match_text = get_most_match_text_multiple(ref_txt, recog_text, part_text_list[i+1][1])
                if i == 65:
                    match_text = get_most_match_text_multiple(ref_txt, recog_text, part_text_list[i + 1][1])
                correct_list.append((i, match_text, recog_text, audio_name_list[i]))
                last_end_idx = last_end_idx + len(match_text)
                print("match line", i, match_text, recog_text, last_end_idx)
            else:
                print("last modify", i)
                break
        elif i < len(recog_txt_list)-1:
            ref_txt = ref_full_txt[last_end_idx:last_end_idx+len(ref_text)+float_range]
            match_text = get_most_match_text_multiple(ref_txt, recog_text, part_text_list[i + 1][1])
            correct_list.append((i, match_text, recog_text, audio_name_list[i]))
            last_end_idx = last_end_idx + len(match_text)
            print("match line", i, match_text, recog_text, last_end_idx)
        elif i == len(recog_txt_list)-1:
            ref_txt = ref_full_txt[last_end_idx:last_end_idx+len(ref_text)+float_range]
            match_text, _, _ = get_most_match_text_single(ref_txt, recog_text)
            correct_list.append((i, match_text, recog_text, audio_name_list[i]))
            last_end_idx = last_end_idx + len(match_text)
            print("match line", i, match_text, recog_text, last_end_idx)


    recog_text_path = "origin_sdpz" + str(chapter_idx) + ".txt"
    with open(recog_text_path, 'w', encoding="utf-8") as f:
        for i, _, text, audio_name in correct_list:
            f.write(audio_name + '|' + text + '\n')

    adjustify_text_path = "modified_sdpz" + str(chapter_idx) + ".txt"
    with open(adjustify_text_path, 'w', encoding="utf-8") as f:
        for i, text, _, audio_name in correct_list:
            f.write(audio_name + '|' + text + '\n')

    return last_end_idx

def get_recog_txt(start_idx, chapter_idx, part_text_path):
    audio_name_list = []
    part_text_list = []
    count = 0
    with open(part_text_path, encoding='utf-8') as f:
        f_list = list(f)
        for line in f_list[start_idx:]:
            split_part = line.strip().split('|')
            text = split_part[-1]
            audio_name = split_part[0]
            rst_search = re.search("([0-9])*_", audio_name)
            if rst_search is not None:
                text_charpter_idx = int(rst_search.group(0)[:-1])
                if text_charpter_idx != chapter_idx:
                    break
                part_text_list.append((count, text))
            count += 1
            audio_name_list.append(audio_name)
    next_start_idx = start_idx + count
    return next_start_idx, part_text_list, audio_name_list


with open(part_text_path, encoding='utf-8') as f:
    f_list = list(f)
    last_line = f_list[-1]
    split_part = last_line.strip().split('|')
    audio_name = split_part[0]
    rst_search = re.search("([0-9])*_", audio_name)
    assert rst_search is not None
    text_charpter_idx = int(rst_search.group(0)[:-1])
    last_chapter_idx = text_charpter_idx


def get_most_correct_txt_list(ref_txt, recog_txt):
    print("lines number", len(part_text_list))
    most_correct_list = []
    last_idx = 0
    last_found = False
    accum_missing_word = 0
    for i, recog_text_line in enumerate(recog_txt):
        idx = ref_txt.find(recog_text_line[1], last_idx)
        cur_len = len(recog_text_line[1])
        if idx != -1:
            if last_found and (idx < last_idx + cur_len):
                most_correct_list.append((i, idx, recog_text_line[1]))
                last_found = True
                last_idx = idx + cur_len
                accum_missing_word = 0

            elif not last_found:
                if idx < (last_idx + accum_missing_word + 100) and idx > (last_idx + accum_missing_word - 100):
                    most_correct_list.append((i, idx, recog_text_line[1]))
                    last_found = True
                    last_idx = idx + cur_len
                    accum_missing_word = 0
                elif idx < (last_idx + accum_missing_word + 3000):
                    # check the next iter
                    upper = min(len(recog_txt), i + len(recog_txt)//10)
                    next_flag_lead = False
                    for j in range(i, upper):
                        next_idx = ref_txt.find(recog_txt[j][1], last_idx)
                        if next_idx < idx and next_idx > last_idx and (len(recog_txt[j][1]) > 3):
                            next_flag_lead = True
                            break
                    if next_flag_lead:
                        last_found = False
                        accum_missing_word += cur_len
                    else:
                        most_correct_list.append((i, idx, recog_text_line[1]))
                        last_found = True
                        last_idx = idx + cur_len
                        accum_missing_word = 0
            else:
                last_found = False
                accum_missing_word += cur_len
        else:
            last_found = False
            accum_missing_word += cur_len
    return most_correct_list

full_text = None
with open(full_text_path, encoding='utf-8') as f:
    contents = f.read()
    for part_text_line in contents:
        if full_text is None:
            full_text = part_text_line
        else:
            full_text = full_text + part_text_line

recog_start_idx = 0
full_start_idx = 0
rst_search = re.search('(第(.)+章)+', full_text)
if rst_search is not None:
    full_chapter_pos = rst_search.span()
    full__end_idx = full_chapter_pos[0] + full_start_idx
    full_start_idx = full_chapter_pos[1] + full_start_idx


full_text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《》“”abcdedfghijklmnopqrsruvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]+", "", full_text)


for i in range(0, last_chapter_idx):
    chapter_idx = i + 1
    next_start_idx, part_text_list, audio_name_list = get_recog_txt(recog_start_idx, chapter_idx, part_text_path)
    text_to_find = full_text[full_start_idx:]
    ref_text = full_text[full_start_idx:]
    most_correct_list = get_most_correct_txt_list(ref_text, part_text_list)
    last_end_idx = correct_text_auto(ref_text, most_correct_list, part_text_list, audio_name_list, chapter_idx)
    full_start_idx = last_end_idx + full_start_idx
    recog_start_idx = next_start_idx




