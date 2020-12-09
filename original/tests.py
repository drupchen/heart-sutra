from pathlib import Path


def test_lines_words():
    w2w = Path('word-for-word/EN.txt').read_text().strip().split('\n')
    orig = Path('orig/heart-sutra-bo-seg.txt').read_text().strip().split('\n')
    phonetics = Path('phonetics/EN.txt').read_text().strip().split('\n')

    if not len(w2w) == len(orig) == len(phonetics):
        print(f'w2w: {len(w2w)}, orig: {len(orig)}, phonetics: {len(phonetics)}')

    for i in range(len(w2w)):
        w = w2w[i].strip().split(' ')
        o = orig[i].strip().split(' ')
        p = phonetics[i].strip().split(' ')
        if not len(w) == len(o) == len(p):
            print(f'line {i+1}: word2word - {len(w)}, orig - {len(o)}, phonetics - {len(p)}')


if __name__ == '__main__':
    test_lines_words()
