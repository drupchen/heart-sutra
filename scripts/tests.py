from pathlib import Path


def test_lines_words(file, orig, trans):
    orig = Path(f'../original/0-original/{file}_{orig}.txt').read_text().strip().split('\n')
    phonetics = Path(f'../original/1-phonetics/{file}_{trans}.txt').read_text().strip().split('\n')
    w2w = Path(f'../original/2-word-for-word/{file}_{trans}.txt').read_text().strip().split('\n')

    if not len(w2w) == len(orig) == len(phonetics):
        print(f'{file},{trans} 0-orig: {len(orig)}, 1-phon: {len(phonetics)}, 2-w2w: {len(w2w)}')

    for i in range(len(w2w)):
        w = w2w[i].strip().split(' ')
        o = orig[i].strip().split(' ')
        p = phonetics[i].strip().split(' ')
        if not len(w) == len(o) == len(p):
            print(f'{file},{trans} line {i+1} — 0-orig:{len(o)}, 1-phon:{len(p)}, 2-w2w:{len(w)}, , ')


if __name__ == '__main__':
    file, orig_lang, trans_lang = 'heart-sutra', 'BO', 'EN'
    test_lines_words(file, orig_lang, trans_lang)
