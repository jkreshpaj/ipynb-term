import click
import json
import os
import re
from itertools import repeat
W, H = os.get_terminal_size()
PADDING_SPACE = 10
PADDING_START = ''.join(list(repeat(' ', PADDING_SPACE)))
CODE_BG_START = '\x1b[7;30;47m'
CODE_GREEN = '\x1b[7;30;42m'
CODE_PURPLE = '\x1b[7;30;45m'
CODE_YELLOW = '\x1b[7;30;43m'
CODE_END = '\x1b[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

def create_cell(cell):
    if cell['cell_type'] == 'code':
        content = create_cell_code(cell)
        print(CODE_BG_START + content + CODE_END)
    if cell['cell_type'] == 'markdown':
        print(read_md(create_cell_md(cell)))
        print('\n')

def create_cell_code(cell):
    lines = []
    for index, line in enumerate(cell['source']):
        trimmed = line.replace('\n', '')
        padding_start = PADDING_START
        if index == 0:
            exec_info = 'In [' + str(cell['execution_count']) + ']:'
            spaces = ''.join(list(repeat(' ', len(padding_start) - len(exec_info))))
            padding_start = exec_info + spaces
        fill_spaces = list(repeat(' ', W - len(trimmed) - len(padding_start)))
        code_line = trimmed + (''.join(fill_spaces))
        lines.append(CODE_END + padding_start + CODE_BG_START + code_line + CODE_END)
    if (len(cell['outputs'])) > 0:
        for out in cell['outputs']:
            lines.append(''.join(create_cell_out(out)))
    return ''.join(lines)

def create_cell_md(cell):
    lines = []
    for index, line in enumerate(cell['source']):
        if len(PADDING_START + line) > W:
            lines.append(''.join(make_multiline(line)))
        else:
            lines.append(PADDING_START + line)
    return ''.join(lines)

def create_cell_out(output):
    if output['output_type'] == 'stream':
        outs = []
        for txt in output['text']:
            outs.append(PADDING_START + txt)
        return outs
    elif output['output_type'] == 'display_data':
        return ''
    else:
        return ''

def make_multiline(line):
    lines = []
    c_line = 0
    for word in line.split():
        try:
            if (len(lines[c_line]) + len(word) + 1) > W:
                if len(lines[c_line]) < W:
                    padding_end = ''.join(list(repeat(' ', W - len(lines[c_line]))))
                    lines[c_line] = lines[c_line] + padding_end
                c_line = c_line + 1
                lines.insert(c_line, PADDING_START + word)
            else:
                lines[c_line] = lines[c_line] + ' ' + word
        except IndexError:
            lines.insert(c_line, PADDING_START + word)
    return lines

def read_md(text):
    rgxps = [
        r'(#|##|###) .+',
    ]
    for r in rgxps:
        for match in re.compile(r).finditer(text):
            text = re.sub(r, BOLD + UNDERLINE + ' '.join(match.group(0).split(' ')[1:]) + END, text)
    return text

@click.command()
@click.argument('file')
def main(file):
    with open(file, 'r') as filedata:
        data = filedata.read()
        parsed = json.loads(data)
        for cell in parsed['cells']:
            create_cell(cell)
if __name__ == "__main__":
    main()
