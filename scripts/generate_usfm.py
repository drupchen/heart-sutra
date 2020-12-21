from pathlib import Path
import re
from collections import defaultdict


class Usfm:
    def __init__(self, orig_path):
        self.paths = {}
        self.output = '../USFM'
        self.parse_path(orig_path)

    def parse_path(self, orig_folder):
        root = Path(orig_folder)
        for d in sorted(root.iterdir()):
            cat = d.stem[2:]
            for f in d.glob('*.*'):
                text, lang = f.stem.split('_')

                if text not in self.paths:
                    self.paths[text] = {}

                if cat == 'original':
                    if cat not in self.paths[text]:
                        self.paths[text][cat] = []

                    self.paths[text][cat].append(f)
                else:
                    if lang not in self.paths[text]:
                        self.paths[text][lang] = {}
                    if cat not in self.paths[text][lang]:
                        self.paths[text][lang][cat] = []

                    self.paths[text][lang][cat].append(f)

    def gen_usfm(self):
        for text, i in self.paths.items():
            folder = Path(self.output) / text
            folder.mkdir(exist_ok=True)

            for lang, j in i.items():
                if lang == 'original':
                    outfile = folder / (lang + '.usfm')
                    infile = j[0]  # one file per cat per lang is supported at the moment
                    out = self.gen_orig(infile)
                    if out:
                        outfile.write_text(out, encoding='utf-8')

                else:
                    for cat, k in j.items():
                        outfile = folder / f'{cat}_{lang}.usfm'
                        infile = k[0]  # one file per cat per lang is supported at the moment
                        if cat == 'phonetics':
                            out = self.gen_phon(infile, cat, lang)
                        elif cat == 'words':
                            out = self.gen_words(infile, cat, lang)
                        elif cat == 'word-for-word':
                            litfile = None
                            if 'literal' in self.paths[text][lang]:
                                litfile = self.paths[text][lang]['literal'][0]  # one file per cat per lang for now
                            out = self.gen_w4w(infile, cat, lang,  litfile)
                        elif cat == 'literal':
                            out = self.gen_lit(infile, cat, lang)
                        elif cat == 'translation':
                            out = self.gen_trans(infile, cat, lang)
                        else:
                            print(f'category "{cat}" is not implemented. moving on to next category.')
                            continue

                        if out:
                            outfile.write_text(out, encoding='utf-8')

    def gen_orig(self, infile):
        id = f'\id བོད་ཡིག\n'

        dump = infile.read_text(encoding='utf-8')

        parsed = self._parse_text(dump)
        usfm = self._format_usfm(parsed)

        return id + usfm

    def gen_phon(self, infile, cat, lang):
        id = f'\id {cat}_{lang}\n'
        dump = infile.read_text(encoding='utf-8')

        parsed = self._parse_text(dump)
        usfm = self._format_usfm(parsed)

        return id + usfm

    def gen_words(self, infile, cat, lang):
        id = f'\id {cat}_{lang}\n'
        dump = infile.read_text(encoding='utf-8')

        parsed = self._parse_text(dump)
        usfm = self._format_usfm(parsed)

        return id + usfm

    def gen_w4w(self, infile, cat, lang, lit=None):
        id = f'\id {lang}_{cat}\n'
        indump = infile.read_text(encoding='utf-8')
        if lit:
            litdump = lit.read_text(encoding='utf-8')
        else:
            litdump = None
        usfm = self._gen_tables(indump, litdump)
        return '\n'.join([id] + usfm)

    def gen_lit(self, infile, cat, lang):
        id = f'\id {cat}_{lang}\n'
        dump = infile.read_text(encoding='utf-8')

        parsed = self._parse_text(dump)
        usfm = self._format_usfm(parsed)

        return id + usfm

    def gen_trans(self, infile, cat, lang):
        id = f'\id {lang}_{cat}\n'

        dump = infile.read_text(encoding='utf-8')

        parsed = self._parse_text(dump)
        usfm = self._format_usfm(parsed)

        return id + usfm

    def _parse_text(self, dump, commentary=False):
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

                    if ('\\' in verse and verse[:verse.find(
                            '\\')].strip() == '') or ' \  ' in verse:  # check there are only spaces before \
                        if not commentary:
                            cur_line['nonverse'] = True
                            non_verse_idx = verse.find('\\')
                            if verse[non_verse_idx + 1] == ' ':
                                cur_line['text'] = verse[non_verse_idx + 1:].strip()
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

                if len(lines) > 1 and i < len(lines) - 1:
                    cur_line['line_break'] = True

        return document

    @staticmethod
    def _format_usfm(doc):
        par_break = '\n\p\n'
        line_break = '\\b'
        verse = '\\v'
        verse_mark = '\q1'

        usfm = []
        for par in list(doc.values()):
            paragr = []
            lines = list(par.values())
            for l in lines:
                begin = ''

                if 'poetry' in l and 'v_count' in l:
                    v = f'{verse} {l["v_count"]}'
                    begin = f'{verse_mark}\n{v}'
                elif 'poetry' in l:
                    begin = verse_mark
                elif 'v_count' in l:
                    begin = f'{verse} {l["v_count"]}'

                if begin:
                    line = f'{begin} {l["text"]}'
                else:
                    line = l['text']
                paragr.append(line)

                if 'line_break' in l:
                    paragr.append(line_break)
            usfm.append('\n'.join(paragr))
        usfm = par_break.join(usfm)

        return usfm

    def _gen_tables(self, csv, literal):
        line_len = 60  # chars in latin alphabet

        orig, phonetics, w2w = self.__parse_w2w(csv)
        if literal:
            literal = literal.strip().split('\n')
        else:
            literal = None

        tables = []
        for line in range(len(orig)):
            o_els, p_els, w_els = orig[line], phonetics[line], w2w[line]
            sub_tables = []
            sub_table = [['\\tr'], ['\\tr'], ['\\tr']]
            char_count = 0
            w = 0
            table_w_max = 9
            table_w_cur = 0
            while w <= len(o_els) - 1:
                o_word, p_word, w_word = o_els[w], p_els[w], w_els[w]
                if w == 0:
                    char_count += self.__update_char_count(p_word, w_word)

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
                    char_count += self.__update_char_count(p_word, w_word)
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

            table = '\n\\b\n'.join(['\n'.join([' '.join(a) for a in sub]) for sub in sub_tables])
            if literal:
                tables.append(f'\mi\n\\v {line + 1}\n{table}\n\iot {literal[line]}\n')
            else:
                tables.append(f'\mi\n\\v {line + 1}\n{table}\n')

        return tables

    @staticmethod
    def __update_char_count(word1, word2):
        if len(word1) > len(word2):
            return len(word1)
        return len(word2)

    @staticmethod
    def __parse_w2w(dump):
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


u = Usfm('../original')
u.gen_usfm()
print('')
