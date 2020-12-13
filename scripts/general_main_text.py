from pathlib import Path
import re
from collections import defaultdict


def parse_text(dump, commentary=False):
    par_sep = '\n\n\n'
    line_sep = '\n\n'
    verse_sep = '\n'
    verse_mark = ('\t', '    ')

    document = defaultdict(defaultdict)
    verse_count = 0
    for i, par in enumerate(dump.split(par_sep)):
        cur_par = document[f'par{i + 1}'] = defaultdict(defaultdict)
        line_count = 0
        lines = par.split(line_sep)

        if not lines:  # make sure last test of function never fails
            raise ValueError(f'par {i + 1} has problem:\n"{par}"')

        for i, line in enumerate(lines):

            for verse in line.split(verse_sep):
                cur_line = cur_par[f'line{line_count + 1}'] = defaultdict(dict)
                cur_line['text'] = verse.strip()

                if verse.startswith(verse_mark[0]) or verse.startswith(verse_mark[1]):
                    cur_line['poetry'] = True

                if ('\\' in verse and verse[:verse.find('\\')].strip() == '') or ' \ ' in verse:  # check there are only spaces before \
                    if not commentary:
                        cur_line['nonverse'] = True
                        non_verse_idx = verse.find('\\')
                        if verse[non_verse_idx+1] == ' ':
                            cur_line['text'] = verse[non_verse_idx+1:].strip()
                        if ' \ ' in verse:
                            cur_line['text'] = re.sub(r' \\ ', r' ', verse)
                    else:
                        cur_line['v_count'] = verse_count + 1
                        verse_count += 1
                else:
                    if not commentary:
                        cur_line['v_count'] = verse_count + 1
                        verse_count += 1

                line_count += 1

            if len(lines) > 1 and i < len(lines)-1:
                cur_line['line_break'] = True

    return document


def format_usfm(doc):
    pass


if __name__ == '__main__':
    file, trans_lang = 'heart-sutra', 'EN'
    dump = Path(f'../original/5-translation/{file}_{trans_lang}.txt').read_text().strip()
    parsed = parse_text(dump)
    print('')
