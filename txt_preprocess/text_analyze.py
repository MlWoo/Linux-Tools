#coding= utf-8
import re
import mmap

full_text_path = "sdpz_full.txt"
part_text_path = "sdpz_part1.txt"
adjustify_text_path = "sdpz_part1_adjustify.txt"


def get_recog_txt():
    
    return idx, txt_list, last_line_idx

with open(part_text_path, encoding='utf-8') as f:
    for line in f:
        split_part = line.strip().split('|')
        text = split_part[-1]
        part_text_list.append((count, text))
        count += 1

full_text = None
with open(full_text_path, encoding='utf-8') as f:
    contents = f.read()
    for part_text_line in contents:
        if full_text is None:
            full_text = part_text_line
        else:
            full_text = full_text + part_text_line


full_text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《》“”]+", "", full_text)
print("lines number", len(part_text_list))
most_correct_list = []
last_idx = 0
last_found = False
count = 0
for i, part_text_line in part_text_list:
    idx = full_text.find(part_text_line, last_idx)
    cur_len = len(part_text_line)
    if idx != -1:
        if idx < last_idx + cur_len:
            most_correct_list.append((i, idx, part_text_line))
            last_found = True
            last_idx = idx + cur_len
            count += 1
        elif not last_found and idx < last_idx + 1000:
            most_correct_list.append((i, idx, part_text_line))
            last_found = True
            last_idx = idx + cur_len
            count += 1
        else:
            last_found = False
    else:
        last_found = False


assert most_correct_list[0][0] == 0

float_range = 8

import numpy as np

def length(s0, s1):
    if s0 is None:
        raise TypeError("Argument s0 is NoneType.")
    if s1 is None:
        raise TypeError("Argument s1 is NoneType.")
    first_idx = None
    last_idx = None
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


correct_list = []
correct_line = 0
last_end_idx = 0
for i, recog_text in part_text_list:
    if correct_line >= len(most_correct_list):
        break
    correct_no, correct_idx, correct_text = most_correct_list[correct_line]
    if i == correct_no:
        correct_line += 1
        last_end_idx = correct_idx + len(correct_text)
        correct_list.append((i, '| wml 已校正               | ' + recog_text + " | " + recog_text))
        print("correct line", i, correct_text, last_end_idx)
    elif i == correct_no - 1:
        ref_txt = full_text[last_end_idx:correct_idx]
        last_end_idx = last_end_idx + len(ref_txt)
        correct_list.append((i, '| wml 可能大段增删         | ' + ref_txt + " | " + recog_text))
        print("modify line", i, ref_txt, last_end_idx)
    elif i < correct_no:
        ref_txt = full_text[last_end_idx:correct_idx]
        match_text = get_most_match_text_multiple(ref_txt, recog_text, part_text_list[i+1][1])
        if i == 65:
            match_text = get_most_match_text_multiple(ref_txt, recog_text, part_text_list[i + 1][1])
        correct_list.append((i, '| wml 基本小幅删改          | ' + match_text + " | " + recog_text))
        last_end_idx = last_end_idx + len(match_text)
        print("match line", i, match_text, recog_text, last_end_idx)
    else:
        print("last modify", i)
        break

with open(adjustify_text_path, 'w', encoding="utf-8") as f:
    for i, text in correct_list:
        f.write(text + '\n')

