from pathlib import Path


def gen_tables(name, orig, trans):
    line_len = 60  # chars in latin alphabet

    orig = Path(f'../original/0-original/{name}_{orig}.txt').read_text().strip().split('\n')
    phonetics = Path(f'../original/1-phonetics/{name}_{trans}.txt').read_text().strip().split('\n')
    w2w = Path(f'../original/2-word-for-word/{name}_{trans}.txt').read_text().strip().split('\n')
    literal = Path(f'../original/3-litteral/{name}_{trans}.txt').read_text().strip().split('\n')

    tables = []
    for line in range(len(orig)):
        o_els, p_els, w_els = orig[line].split(' '), phonetics[line].split(' '), w2w[line].split(' ')
        sub_tables = []
        sub_table = [['\\tr'], ['\\tr'], ['\\tr']]
        char_count = 0
        w = 0
        table_w_max = 9
        table_w_cur = 0
        while w <= len(o_els)-1:
            o_word, p_word, w_word = o_els[w], p_els[w], w_els[w]
            if w == 0:
                char_count += update_char_count(p_word, w_word, w)

            if char_count <= line_len or table_w_cur <= table_w_max:
                for num, x in enumerate([o_word, p_word, w_word]):
                    sub_table[num].append(f'\\tc{table_w_cur}')
                    sub_table[num].append(x)
                if table_w_cur < table_w_max:
                    table_w_cur += 1
                char_count += update_char_count(p_word, w_word, w)
                w += 1
                if char_count >= line_len or table_w_cur >= table_w_max:
                    # went too far, so remove last word of sub_table and decrement w
                    for i in [0, 1, 2]:
                        sub_table[i] = sub_table[i][:-2]
                    w -= 1

                    # save sub_table and reinitialize vars
                    sub_tables.append(sub_table)
                    sub_table = [['\\tr'], ['\\tr'], ['\\tr']]
                    char_count = 0
                    table_w_cur = 0
            else:
                sub_tables.append(sub_table)
                sub_table = [['\\tr'], ['\\tr'], ['\\tr']]
                char_count = 0
                table_w_cur = 0

        if sub_table != [['\\tr'], ['\\tr'], ['\\tr']]:
            sub_tables.append(sub_table)

        print('')
        table = '\n\\b\n'.join(['\n'.join([' '.join(a) for a in sub]) for sub in sub_tables])
        tables.append(f'\p\n\\v {line+1}\n{table}\n\\sp {literal[line]}')

    total = '\n'.join(tables)
    out_file = Path(f'../USFM/{name}_{trans}_tables.txt')
    out_file.write_text(total)


def update_char_count(word1, word2, w):
    if len(word1) > len(word2):
        return len(word1)
    return len(word2)


if __name__ == '__main__':
    file, orig_lang, trans_lang = 'heart-sutra', 'BO', 'EN'
    gen_tables(file, orig_lang, trans_lang)