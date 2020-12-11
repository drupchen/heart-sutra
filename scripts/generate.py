from pathlib import Path


def gen_tables(name, orig, trans):
    orig = Path(f'../original/0-original/{name}_{orig}.txt').read_text().strip().split('\n')
    phonetics = Path(f'../original/1-phonetics/{name}_{trans}.txt').read_text().strip().split('\n')
    w2w = Path(f'../original/2-word-for-word/{name}_{trans}.txt').read_text().strip().split('\n')

    tables = []
    for line in range(len(orig)):
        table = []
        o_els, p_els, w_els = orig[line].split(' '), phonetics[line].split(' '), w2w[line].split(' ')
        sub_tables = []
        sub_table = None
        for w in range(len(o_els)):
            if w % 9 == 0:
                if sub_table:
                    sub_tables.append(sub_table)
                sub_table = [
                    ['\\tr'],
                    ['\\tr'],
                    ['\\tr']
                ]
            for num, x in enumerate([o_els[w], p_els[w], w_els[w]]):
                sub_table[num].append(f'\\tc{(w % 9) + 1}')
                sub_table[num].append(x)
        if sub_table:
            sub_tables.append(sub_table)

        print('')
        table = '\n\\b\n'.join(['\n'.join([' '.join(a) for a in sub]) for sub in sub_tables])
        tables.append(f'\p\n\\v {line+1}\n{table}')

    total = '\n'.join(tables)
    out_file = Path(f'../USFM/{name}_{trans}_tables.txt')
    out_file.write_text(total)


if __name__ == '__main__':
    file, orig_lang, trans_lang = 'heart-sutra', 'BO', 'EN'
    gen_tables(file, orig_lang, trans_lang)