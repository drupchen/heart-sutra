from pathlib import Path


def gen_tables(name, orig, trans):
    orig = Path(f'../original/0-original/{name}_{orig}.txt').read_text().strip().split('\n')
    phonetics = Path(f'../original/1-phonetics/{name}_{trans}.txt').read_text().strip().split('\n')
    w2w = Path(f'../original/2-word-for-word/{name}_{trans}.txt').read_text().strip().split('\n')

    tables = []
    for line in range(len(orig)):
        table = [
            ['\\tr'],
            ['\\tr'],
            ['\\tr']
        ]
        o_els, p_els, w_els = orig[line].split(' '), phonetics[line].split(' '), w2w[line].split(' ')
        for w in range(len(o_els)):
            for num, x in enumerate([o_els[w], p_els[w], w_els[w]]):
                table[num].append(f'\\tc{w+1}')
                table[num].append(x)
        tables.append(f'\p\n\\v {line+1}\n{" ".join(table[0])}\n{" ".join(table[1])}\n{" ".join(table[2])}')

    total = '\n'.join(tables)
    out_file = Path(f'../USFM/{name}_{trans}_tables.txt')
    out_file.write_text(total)


if __name__ == '__main__':
    file, orig_lang, trans_lang = 'heart-sutra', 'BO', 'EN'
    gen_tables(file, orig_lang, trans_lang)