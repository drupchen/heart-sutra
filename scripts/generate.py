from pathlib import Path
import re


def gen_tables(name, trans):
    line_len = 60  # chars in latin alphabet

    w2w_path = Path(f'../original/3-word-for-word/{name}_{trans}.csv')
    orig, phonetics, w2w = parse_w2w(w2w_path.read_text())
    literal = Path(f'../original/4-litteral/{name}_{trans}.txt').read_text().strip().split('\n')

    tables = []
    for line in range(len(orig)):
        o_els, p_els, w_els = orig[line], phonetics[line], w2w[line]
        sub_tables = []
        sub_table = [['\\tr'], ['\\tr'], ['\\tr']]
        char_count = 0
        w = 0
        table_w_max = 9
        table_w_cur = 0
        while w <= len(o_els)-1:
            o_word, p_word, w_word = o_els[w], p_els[w], w_els[w]
            if w == 0:
                char_count += update_char_count(p_word, w_word)

            if char_count <= line_len or table_w_cur <= table_w_max:
                for num, x in enumerate([o_word, p_word, w_word]):
                    sub_table[num].append(f'\\tc{table_w_cur}')
                    if num == 0:
                        sub_table[num].append(f'\ow {x} \ow*')
                    elif num == 1:
                        sub_table[num].append(f'\pw {x} \pw*')
                    else:
                        sub_table[num].append(f'\ww {x} \ww*')
                if table_w_cur < table_w_max:
                    table_w_cur += 1
                char_count += update_char_count(p_word, w_word)
                w += 1
                if char_count > line_len or table_w_cur > table_w_max:
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
        tables.append(f'\mi\n\\v {line+1}\n{table}\n\\sp {literal[line]}')

    header = '\id word_for_word\n'
    total = header + '\n'.join(tables)
    out_file = Path(f'../USFM/{name}_{trans}_tables.txt')
    out_file.write_text(total)


def update_char_count(word1, word2):
    if len(word1) > len(word2):
        return len(word1)
    return len(word2)


def parse_w2w(dump):
    dump = re.sub(r'\n,+\n', '\n\n', dump)
    chunks = dump.strip().split('\n\n')
    o, p, w = [], [], []
    for c in chunks:
        a, b, c = c.split('\n')
        a, b, c = a.strip(','), b.strip(','), c.strip(',')
        a, b, c = a.split(','), b.split(','), c.split(',')
        o.append(a)
        p.append(b)
        w.append(c)
    return o, p, w


if __name__ == '__main__':
    file, trans_lang = 'heart-sutra', 'EN'
    gen_tables(file, trans_lang)
