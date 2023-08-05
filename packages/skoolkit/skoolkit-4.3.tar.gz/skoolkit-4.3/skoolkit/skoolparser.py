# -*- coding: utf-8 -*-

# Copyright 2008-2015 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of SkoolKit.
#
# SkoolKit is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# SkoolKit is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# SkoolKit. If not, see <http://www.gnu.org/licenses/>.

import cgi
import re

from . import warn, wrap, get_int_param, parse_int, open_file, SkoolParsingError
from .skoolmacro import DELIMITERS

DIRECTIVES = 'bcgistuw'

TABLE_MARKER = '#TABLE'
TABLE_END_MARKER = 'TABLE#'
COLUMN_WRAP_MARKER = ':w'

LIST_MARKER = '#LIST'
LIST_END_MARKER = 'LIST#'

#: Force upper case.
CASE_UPPER = 0
#: Force lower case.
CASE_LOWER = 1
#: Force decimal.
BASE_10 = 10
#: Force hexadecimal.
BASE_16 = 16

FORMAT_NO_BASE = {
    'b': 'b{}',
    'd': '{}',
    'h': '{}'
}

FORMAT_DEFM_NO_BASE = {
    'b': 'b{}',
    'd': 'B{}',
    'h': 'B{}'
}

FORMAT_PRESERVE_BASE = {
    'b': 'b{}',
    'd': 'd{}',
    'h': 'h{}'
}

def get_address(operation, check_prefix=True):
    if check_prefix:
        prefixes = '[ ,(+-]'
    else:
        prefixes = ''
    search = re.search('{}\$[0-9A-Fa-f]+'.format(prefixes), operation)
    if not search:
        search = re.search('{}%[01]+'.format(prefixes), operation)
    if not search:
        search = re.search('{}[0-9]+'.format(prefixes), operation)
    if search:
        if check_prefix:
            index = 1
        else:
            index = 0
        return search.group()[index:]

def get_instruction_ctl(op):
    op = op.upper()
    if op.startswith('DEFB'):
        return 'B'
    if op.startswith('DEFW'):
        return 'W'
    if op.startswith('DEFM'):
        return 'T'
    if op.startswith('DEFS'):
        return 'S'
    return 'C'

def _get_base(item, preserve_base):
    if item.startswith('%'):
        return 'b'
    if item.startswith('$') and preserve_base:
        return 'h'
    return 'd'

def get_defb_length(item_str, preserve_base, defb=True):
    if defb:
        byte_fmt = FORMAT_NO_BASE
        text_fmt = 'T{}'
    else:
        byte_fmt = FORMAT_DEFM_NO_BASE
        text_fmt = '{}'
    if preserve_base:
        byte_fmt = FORMAT_PRESERVE_BASE
    full_length = 0
    lengths = []
    length = 0
    prev_base = None
    for item in get_defb_item_list(item_str) + ['""']:
        if item.startswith('"'):
            if length:
                lengths.append(byte_fmt[prev_base].format(length))
                full_length += length
                length = 0
                prev_base = None
            i = 1
            while i < len(item) - 1:
                if item[i] == '\\':
                    i += 1
                i += 1
                length += 1
            if length:
                lengths.append(text_fmt.format(length))
                full_length += length
                length = 0
        else:
            cur_base = _get_base(item, preserve_base)
            if prev_base != cur_base and length:
                lengths.append(byte_fmt[prev_base].format(length))
                full_length += length
                length = 0
            length += 1
            prev_base = cur_base
    return full_length, ':'.join(lengths)

def get_defm_length(item_str, preserve_base):
    return get_defb_length(item_str, preserve_base, False)

def get_defb_item_list(item_str):
    items = []
    i = 0
    while i < len(item_str):
        char = item_str[i]
        if char.isspace() or char == ',':
            i += 1
        elif char == '"':
            item = char
            i += 1
            while i < len(item_str):
                msg_char = item_str[i]
                item += msg_char
                if msg_char == '\\':
                    item += item_str[i + 1]
                    i += 2
                elif msg_char == '"':
                    items.append(item)
                    i += 1
                    break
                else:
                    i += 1
        else:
            end = item_str.find(',', i + 1)
            if end < 0:
                end = len(item_str)
            items.append(item_str[i:end])
            i = end + 1
    return items

def get_defw_length(item_str, preserve_base):
    if preserve_base:
        word_fmt = FORMAT_PRESERVE_BASE
    else:
        word_fmt = FORMAT_NO_BASE
    full_length = 0
    lengths = []
    length = 0
    prev_base = None
    for item in item_str.split(','):
        item = item.strip()
        cur_base = _get_base(item, preserve_base)
        if prev_base != cur_base and length:
            lengths.append(word_fmt[prev_base].format(length))
            full_length += length
            length = 0
        length += 2
        prev_base = cur_base
    lengths.append(word_fmt[prev_base].format(length))
    full_length += length
    return full_length, ':'.join(lengths)

def get_defs_length(item_str, preserve_base):
    if preserve_base:
        fmt = FORMAT_PRESERVE_BASE
    else:
        fmt = FORMAT_NO_BASE
    size = None
    lengths = []
    for item in item_str.split(',', 1):
        if size is None:
            size = get_int_param(item)
        base = _get_base(item, preserve_base)
        lengths.append(fmt[base].format(item))
    return size, ':'.join(lengths)

def set_bytes(snapshot, address, operation):
    directive = operation[:4].upper()

    if directive in ('DEFB', 'DEFM'):
        for item in get_defb_item_list(operation[5:]):
            if item.startswith('"'):
                i = 1
                while i < len(item) - 1:
                    if item[i] == '\\':
                        i += 1
                    snapshot[address] = ord(item[i])
                    i += 1
                    address += 1
            else:
                snapshot[address] = parse_int(item, 0)
                address += 1
        return

    args = [parse_int(v, 0) for v in operation[5:].split(',')]
    if directive == 'DEFS':
        span = args[0]
        if len(args) > 1:
            value = args[1]
        else:
            value = 0
        snapshot[address:address + span] = [value] * span
    elif directive == 'DEFW':
        for arg in args:
            snapshot[address:address + 2] = [arg % 256, arg // 256]
            address += 2

def parse_asm_block_directive(directive, stack):
    prefix = directive[:4]
    infix = directive[len(prefix):len(prefix) + 1]
    suffix = directive[len(prefix) + len(infix):].rstrip()
    if prefix in ('ofix', 'bfix', 'rfix', 'isub', 'rsub') and infix in '+-' and suffix in ('begin', 'else', 'end'):
        if stack:
            cur_op = stack[-1]
        else:
            cur_op = (None, None)
        if suffix == 'begin':
            if prefix == cur_op[0]:
                raise SkoolParsingError('{0} inside {1}{2} block'.format(directive, cur_op[0], cur_op[1]))
            stack.append((prefix, infix))
        elif suffix == 'else':
            if cur_op[0] is None:
                raise SkoolParsingError('{0} not inside block'.format(directive))
            if prefix != cur_op[0] or infix == cur_op[1]:
                raise SkoolParsingError('{0} inside {1}{2} block'.format(directive, cur_op[0], cur_op[1]))
            stack[-1] = (prefix, infix)
        elif suffix == 'end':
            if cur_op[0] is None:
                raise SkoolParsingError('{0} has no matching start directive'.format(directive))
            if (prefix, infix) != cur_op:
                raise SkoolParsingError('{0} cannot end {1}{2} block'.format(directive, cur_op[0], cur_op[1]))
            stack.pop()
        return True
    return False

def _html_escape(text):
    chunks = []
    while 1:
        search = re.search('(#HTML[^A-Z]|#FONT:.)', text)
        if not search:
            break
        start, index = search.span()
        delim1 = search.group()[-1]
        delim2 = DELIMITERS.get(delim1, delim1)
        end = text.find(delim2, index) + 1
        if end < index:
            end = len(text)
        chunks.append(cgi.escape(text[:start]))
        chunks.append(text[start:end])
        text = text[end:]
    chunks.append(cgi.escape(text))
    return ''.join(chunks)

def join_comments(comments, split=False, html=False):
    sections = [[]]
    for line in comments:
        s_line = line.strip()
        if split and s_line == '.':
            sections.append([])
        elif s_line:
            sections[-1].append(s_line)
    paragraphs = [" ".join(section) for section in sections if section]
    if html:
        paragraphs = [_html_escape(p) for p in paragraphs]
    if split:
        return paragraphs
    if paragraphs:
        return paragraphs[0]
    return ''

def _apply_ignores(ignores, section_ignores, index, line_no):
    for i in ignores:
        if i < line_no:
            ignores.remove(i)
            section_ignores[index] = True
            return

def _parse_registers(lines, mode):
    registers = []
    desc_lines = []
    for line in lines:
        s_line = line.strip()
        if s_line == '.':
            continue
        if desc_lines and s_line.startswith('.'):
            desc_lines.append(s_line[1:].lstrip())
            continue
        if desc_lines:
            desc = ' '.join(desc_lines).lstrip()
            registers.append((prefix, reg, desc))
            desc_lines[:] = []
        prefix = ''
        elements = s_line.split(None, 1)
        reg = elements[0]
        if len(elements) > 1:
            desc_lines.append(elements[1])
        else:
            desc_lines.append('')
        if ':' in reg:
            prefix, reg = reg.split(':', 1)
        if mode.lower:
            reg = reg.lower()
        elif mode.upper:
            reg = reg.upper()
    if desc_lines:
        desc = ' '.join(desc_lines).lstrip()
        registers.append((prefix, reg, desc))
    if mode.html:
        return [(prefix, reg, _html_escape(desc)) for prefix, reg, desc in registers]
    return registers

def parse_comment_block(comments, ignores, mode):
    sections = [[], [], [], []]
    section_ignores = [False] * len(sections)
    line_no = 0
    index = 0
    last_line = ""
    for line in comments:
        if line:
            sections[index].append(line)
            last_line = line
        elif last_line:
            _apply_ignores(ignores, section_ignores, index, line_no)
            index = min(index + 1, len(sections) - 1)
        line_no += 1
    _apply_ignores(ignores, section_ignores, index, line_no)
    mode.entry_ignoreua['t'] = section_ignores[0]
    mode.entry_ignoreua['d'] = section_ignores[1]
    mode.entry_ignoreua['r'] = section_ignores[2]
    mode.ignoremrcua = section_ignores[3]
    title = join_comments(sections[0], html=mode.html)
    description = join_comments(sections[1], split=True, html=mode.html)
    registers = _parse_registers(sections[2], mode)
    start_comment = join_comments(sections[3], split=True, html=mode.html)
    return start_comment, title, description, registers

def parse_instruction(line):
    ctl = line[0]
    addr_str = line[1:6]
    comment_index = line.find(';')
    if comment_index < 0:
        comment_index = len(line)
    operation = line[7:comment_index].strip()
    comment = line[comment_index + 1:].strip()
    return ctl, addr_str, operation, comment

def parse_address_comments(comments, html=False):
    i = 0
    while i < len(comments):
        instruction, comment = comments[i]
        comment_lines = []
        if comment and comment.strip()[0] == '{':
            nesting = comment.count('{') - comment.count('}')
            while nesting > 0:
                comment_lines.append(comments[i][1])
                i += 1
                nesting += comments[i][1].count('{') - comments[i][1].count('}')
            comment_lines.append(comments[i][1].strip('}'))
            comment_lines[0] = comment_lines[0].strip('{')
        else:
            comment_lines.append(comment)
        rowspan = len(comment_lines)
        address_comment = join_comments(comment_lines, html=html).strip()
        instruction.set_comment(rowspan, address_comment)
        i += 1

class SkoolParser:
    """Parses a `skool` file.

    :param skoolfile: The name of the `skool` file to parse.
    :param case: :data:`~skoolkit.skoolparser.CASE_UPPER` to force upper case,
                 :data:`~skoolkit.skoolparser.CASE_LOWER` to force lower case,
                 or `None` to leave case unchanged.
    :param base: :data:`~skoolkit.skoolparser.BASE_10` to force decimal,
                 :data:`~skoolkit.skoolparser.BASE_16` to force hexadecimal, or
                 `None` to leave number bases unchanged.
    :param asm_mode: 0 to ignore ASM directives, 1 to parse them in `@isub`
                     mode, 2 to parse them in `@ssub` mode, or 3 to parse them
                     in `@rsub` mode.
    :param warnings: Whether to show warnings.
    :param fix_mode: 0 to apply no fixes, 1 to parse `@ofix` directives, 2 to
                     parse `@ofix` and `@bfix` directives, and 3 to parse
                     `@ofix`, `@bfix` and `@rfix` directives.
    :param html: Whether to escape HTML characters.
    :param create_labels: Whether to create default labels for unlabelled
                          instructions.
    :param asm_labels: Whether to parse `@label` directives.
    """
    def __init__(self, skoolfile, case=None, base=None, asm_mode=0, warnings=False, fix_mode=0, html=False, create_labels=False, asm_labels=True):
        self.skoolfile = skoolfile
        self.mode = Mode(case, base, asm_mode, warnings, fix_mode, html, create_labels, asm_labels)
        self.case = case
        self.base = base

        self.snapshot = [0] * 65536  # 64K of Spectrum memory
        self.instructions = {}       # address -> [Instructions]
        self.entries = {}            # address -> SkoolEntry
        self.memory_map = []         # SkoolEntry instances
        self.base_address = 65536
        self.header = []
        self.stack = []
        self.comments = []
        self.ignores = []
        self.asm_writer_class = None
        self.properties = {}

        with open_file(skoolfile) as f:
            self._parse_skool(f)

    def clone(self, skoolfile):
        return SkoolParser(
            skoolfile,
            self.case,
            self.base,
            self.mode.asm_mode,
            self.mode.warn,
            self.mode.fix_mode,
            self.mode.html,
            self.mode.create_labels,
            self.mode.asm_labels
        )

    def get_entry(self, address):
        """Return the routine or data block that starts at `address`."""
        return self.entries.get(address)

    def get_instruction(self, address, asm_id=''):
        """Return the instruction at `address`."""
        for instruction in self.instructions.get(address, []):
            if instruction.container.asm_id.lower() == asm_id.lower():
                return instruction

    def get_container(self, address, asm_id):
        """Return the routine or data block that contains `address`."""
        instruction = self.get_instruction(address, asm_id)
        if instruction:
            return instruction.container

    def get_entry_point_refs(self, address):
        """Return the addresses of the routines and data blocks that contain
        instructions that refer to `address`.
        """
        return [referrer.address for referrer in self.get_instruction(address).referrers]

    def get_asm_label(self, address):
        instruction = self.get_instruction(address)
        if instruction:
            return instruction.asm_label

    def get_instruction_addr_str(self, address, asm_id=''):
        instruction = self.get_instruction(address, asm_id)
        if instruction:
            return instruction.get_addr_str(self.base)
        if asm_id:
            return self.mode.get_addr_str(address)

    def convert_address_operand(self, operand):
        return self.mode.convert_address_operand(operand)

    def _parse_skool(self, skoolfile):
        map_entry = None
        instruction = None
        address_comments = []
        for line in skoolfile:
            if line[0] == ';':
                comment = line[2:].rstrip()
                if comment.startswith('@'):
                    self._parse_asm_directive(comment[1:])
                else:
                    if self.mode.started and self.mode.include:
                        self.comments.append(comment)
                        self.mode.ignoreua = False
                    instruction = None
                continue

            if line.startswith('@'):
                self._parse_asm_directive(line[1:].rstrip())
                continue

            if not self.mode.include:
                continue

            s_line = line.strip()
            if not s_line:
                instruction = None
                if self.comments:
                    if map_entry:
                        self._add_end_comment(map_entry)
                    else:
                        self.header += self.comments
                self.comments[:] = []
                self.ignores[:] = []
                map_entry = None
                continue

            if s_line[0] == ';' and map_entry and instruction:
                # This is an instruction comment continuation line
                address_comments[-1][1] = '{0} {1}'.format(address_comments[-1][1], s_line[1:].lstrip())
                continue

            # This line contains an instruction
            instruction, address_comment = self._parse_instruction(line)
            address = instruction.address
            addr_str = instruction.addr_str
            ctl = instruction.ctl
            if ctl in DIRECTIVES:
                start_comment, desc, details, registers = parse_comment_block(self.comments, self.ignores, self.mode)
                map_entry = SkoolEntry(address, addr_str, ctl, desc, details, registers)
                map_entry.add_mid_routine_comment(instruction.label, start_comment)
                map_entry.ignoreua.update(self.mode.entry_ignoreua)
                self.mode.reset_entry_ignoreua()
                self.entries[address] = map_entry
                self.memory_map.append(map_entry)
                self.comments[:] = []
                self.base_address = min((address, self.base_address))
            elif ctl == 'd':
                # This is a data definition entry
                map_entry = None
            elif ctl == 'r':
                # This is a remote entry
                map_entry = RemoteEntry(instruction.operation, address)

            if map_entry:
                address_comments.append([instruction, address_comment])
                instructions = self.instructions.setdefault(address, [])
                instructions.append(instruction)
                map_entry.add_instruction(instruction)
                if self.comments:
                    mid_routine_comment = join_comments(self.comments, split=True, html=self.mode.html)
                    map_entry.add_mid_routine_comment(instruction.label, mid_routine_comment)
                    self.comments[:] = []
                    self.mode.ignoremrcua = 0 in self.ignores

            self.mode.apply_asm_attributes(instruction)
            self.ignores[:] = []

            # Set bytes in the snapshot if the instruction is DEF{B,M,S,W}
            if address is not None:
                operation = instruction.operation
                if operation[:4].upper() in ('DEFB', 'DEFM', 'DEFS', 'DEFW'):
                    set_bytes(self.snapshot, address, operation)
        if self.comments and map_entry:
            self._add_end_comment(map_entry)

        # Do some post-processing
        parse_address_comments(address_comments, self.mode.html)
        self._calculate_references()
        if self.mode.asm_labels:
            self._generate_labels()
        if self.mode.html:
            self._calculate_entry_sizes()
            self._escape_instructions()
        else:
            self._substitute_labels()

    def _add_end_comment(self, map_entry):
        map_entry.end_comment = join_comments(self.comments, split=True, html=self.mode.html)
        map_entry.ignoreua['e'] = len(self.ignores) > 0

    def _parse_asm_directive(self, directive):
        if self.mode.started:
            if directive.startswith('end'):
                self.mode.end()
                return

            if parse_asm_block_directive(directive, self.stack):
                include = True
                for p, i in self.stack:
                    if p == 'ofix':
                        do_op = self.mode.do_ofixes
                    elif p == 'bfix':
                        do_op = self.mode.do_bfixes
                    elif p == 'rfix':
                        do_op = self.mode.do_rfixes
                    elif p == 'isub':
                        do_op = self.mode.asm
                    elif p == 'rsub':
                        do_op = self.mode.do_rsubs
                    if do_op:
                        include = i == '+'
                    else:
                        include = i == '-'
                    if not include:
                        break
                self.mode.include = include
                return

            if not self.mode.include:
                return

            if directive.startswith('label='):
                self.mode.label = directive[6:].rstrip()
            elif directive.startswith('keep'):
                self.mode.keep = True

            if self.mode.asm:
                if directive.startswith('rsub='):
                    self.mode.rsub = directive[5:].rstrip()
                elif directive.startswith('ssub='):
                    self.mode.ssub = directive[5:].rstrip()
                elif directive.startswith('isub='):
                    self.mode.isub = directive[5:].rstrip()
                elif directive.startswith('bfix='):
                    self.mode.bfix = directive[5:].rstrip()
                elif directive.startswith('ofix='):
                    self.mode.ofix = directive[5:].rstrip()
                elif directive.startswith('nolabel'):
                    self.mode.nolabel = True
                elif directive.startswith('nowarn'):
                    self.mode.nowarn = True
                elif directive.startswith('ignoreua'):
                    self.mode.ignoreua = True
                    self.ignores.append(len(self.comments))
                elif directive.startswith('org='):
                    self.mode.org = directive[4:].rstrip()
                elif directive.startswith('writer='):
                    self.asm_writer_class = directive[7:].rstrip()
                elif directive.startswith('set-'):
                    name, sep, value = directive[4:].partition('=')
                    if sep:
                        self.properties[name.lower()] = value
        elif directive.startswith('start'):
            self.mode.start()

    def _parse_instruction(self, line):
        ctl, addr_str, operation, comment = parse_instruction(line)
        addr_str, operation = self.mode.apply_case(addr_str, operation)
        addr_str, operation = self.mode.apply_base(addr_str, operation)
        instruction = Instruction(ctl, addr_str, operation)
        return instruction, comment

    def _calculate_entry_sizes(self):
        for i, entry in enumerate(self.memory_map[:-1]):
            entry.size = int(self.memory_map[i + 1].address) - int(entry.address)
        if self.memory_map:
            last_entry = self.memory_map[-1]
            last_entry.size = 65536 - int(last_entry.address)

    def _is_8_bit_ld_instruction(self, operation):
        if operation.startswith('LD '):
            ld_args = [arg.strip() for arg in operation[3:].split(',', 1)]
            if not set(ld_args) & {'A', 'BC', 'DE', 'HL', 'SP', 'IX', 'IY'}:
                return True
            if 'A' in ld_args:
                other_arg = ld_args[ld_args.index('A') - 1]
                if not other_arg.startswith('('):
                    return True
                other_arg = other_arg[1:].lstrip()
                if other_arg and other_arg[0] not in '$%0123456789':
                    return True
        return False

    def _calculate_references(self):
        # Parse operations for routine/data addresses
        for entry in self.memory_map:
            for instruction in entry.instructions:
                if instruction.keep:
                    continue
                operation = instruction.operation.upper()
                if not operation.startswith(('CALL', 'DEFW', 'DJNZ', 'JP', 'JR', 'LD ', 'RST')) or self._is_8_bit_ld_instruction(operation):
                    continue
                addr_str = get_address(operation)
                if not addr_str:
                    continue
                address = parse_int(addr_str)
                other_instructions = self.instructions.get(address)
                if other_instructions:
                    other_entry = other_instructions[0].container
                    if other_entry.is_ignored():
                        continue
                    if other_entry.is_remote() or operation.startswith(('DEFW', 'LD ')) or other_entry.is_routine():
                        instruction.set_reference(other_entry, address, addr_str)
                        if operation.startswith(('CALL', 'DJNZ', 'JP', 'JR', 'RST')):
                            other_instructions[0].add_referrer(entry)

    def _escape_instructions(self):
        for entry in self.memory_map:
            for instruction in entry.instructions:
                instruction.html_escape()

    def warn(self, s):
        if self.mode.warn:
            warn(s)

    def _substitute_labels(self):
        for entry in self.memory_map:
            for instruction in entry.instructions:
                if instruction.sub or not instruction.keep:
                    self._label_operand(instruction)

    def _generate_labels(self):
        """Generate labels for mid-routine entry points (based on the label of
           the main entry point)."""
        for entry in self.entries.values():
            instructions = entry.instructions
            if instructions:
                main_label = instructions[0].asm_label
                if not main_label and self.mode.create_labels:
                    main_label = instructions[0].asm_label = 'L{0}'.format(entry.addr_str)
                if main_label:
                    index = 0
                    for instruction in instructions[1:]:
                        if instruction.ctl in '!*' and not instruction.asm_label and not instruction.nolabel:
                            instruction.asm_label = '{0}_{1}'.format(main_label, index)
                            index += 1

    def _label_operand(self, instruction):
        label_warn = instruction.sub is None and instruction.warn
        operation = instruction.operation
        operation_u = operation.upper()
        if operation_u.startswith('RST'):
            return
        operand = get_address(operation)
        if operand is None:
            return
        operand_int = get_int_param(operand)
        if operand_int < 256 and (not operation_u.startswith(('CALL', 'DEFW', 'DJNZ', 'JP', 'JR', 'LD '))
                                  or self._is_8_bit_ld_instruction(operation_u)):
            return
        instructions = self.instructions.get(operand_int)
        if instructions:
            reference = instructions[0]
            if reference.asm_label:
                rep = operation.replace(operand, reference.asm_label)
                if reference.is_in_routine() and label_warn and operation_u.startswith('LD '):
                    # Warn if a LD operand is replaced with a routine label in
                    # an unsubbed operation (will need @keep to retain operand,
                    # or @nowarn if the replacement is OK)
                    self.warn('LD operand replaced with routine label in unsubbed operation:\n  {0} {1} -> {2}'.format(instruction.address, operation, rep))
                instruction.operation = rep
            elif instruction.warn and instruction.is_in_routine():
                # Warn if we cannot find a label to replace the operand of this
                # routine instruction (will need @nowarn if this is OK)
                self.warn('Found no label for operand: {0} {1}'.format(instruction.address, operation))
        elif label_warn and self.mode.do_ssubs and operand_int >= self.base_address:
            # Warn if the operand is at or above the base address of the
            # disassembly (where code might be) but doesn't refer to the
            # address of an instruction (will need @nowarn if this is OK)
            self.warn('Unreplaced operand: {0} {1}'.format(instruction.address, operation))

class Mode:
    def __init__(self, case, base, asm_mode, warnings, fix_mode, html, create_labels, asm_labels):
        self.lower = case == CASE_LOWER
        self.upper = case == CASE_UPPER
        self.decimal = base == BASE_10
        self.hexadecimal = base == BASE_16
        self.html = html
        self.asm_mode = asm_mode
        self.asm = asm_mode > 0
        self.warn = warnings
        self.started = asm_mode == 0
        self.include = self.started
        self.fix_mode = fix_mode
        self.do_rfixes = fix_mode >= 3
        self.do_rsubs = asm_mode >= 3 or self.do_rfixes
        self.do_ssubs = asm_mode >= 2
        self.do_ofixes = fix_mode >= 1 or self.do_rsubs
        self.do_bfixes = fix_mode >= 2
        self.labels = []
        self.create_labels = create_labels
        self.asm_labels = asm_labels
        self.entry_ignoreua = {}
        if self.lower:
            self.hex2fmt = '${0:02x}'
            self.hex4fmt = '${0:04x}'
            self.addr_fmt = '{0:04x}'
        else:
            self.hex2fmt = '${0:02X}'
            self.hex4fmt = '${0:04X}'
            self.addr_fmt = '{0:04X}'
        self.reset()
        self.reset_entry_ignoreua()

    def reset(self):
        self.label = None
        self.isub = None
        self.ofix = None
        self.bfix = None
        self.ssub = None
        self.rsub = None
        self.keep = False
        self.nowarn = False
        self.nolabel = False
        self.ignoreua = False
        self.ignoremrcua = False
        self.org = None

    def reset_entry_ignoreua(self):
        for section in 'tdr':
            self.entry_ignoreua[section] = False

    def start(self):
        self.started = True
        self.include = True

    def end(self):
        if self.asm:
            self.started = False
            self.include = False

    def apply_asm_attributes(self, instruction):
        instruction.keep = self.keep

        if self.asm_labels and self.label:
            if self.label in self.labels:
                raise SkoolParsingError('Duplicate label {0} at {1}'.format(self.label, instruction.address))
            self.labels.append(self.label)
            instruction.asm_label = self.label

        if not self.html:
            sub = self.isub
            if self.bfix is not None and self.do_bfixes:
                sub = self.bfix
            elif self.ofix is not None and self.do_ofixes:
                sub = self.ofix
            elif self.rsub is not None and self.do_rsubs:
                sub = self.rsub
            elif self.ssub is not None and self.do_ssubs:
                sub = self.ssub
            if sub is not None:
                _, sub = self.apply_case('', sub)
                _, sub = self.apply_base('', sub)
                instruction.apply_sub(sub)

            instruction.warn = not self.nowarn
            instruction.nolabel = self.nolabel
            instruction.ignoreua = self.ignoreua
            instruction.ignoremrcua = self.ignoremrcua
            instruction.org = self.org

        self.reset()

    def get_addr_str(self, address):
        if self.hexadecimal:
            return self.addr_fmt.format(address)
        return str(address)

    def convert_address_operand(self, operand):
        if self.decimal:
            return str(parse_int(operand))
        if self.hexadecimal:
            return self.hex4fmt.format(parse_int(operand))
        return operand

    def apply_case(self, addr_str, operation):
        if self.lower:
            addr_str = addr_str.lower()
            if operation.lower().startswith(('defb', 'defm')):
                items = []
                for item in get_defb_item_list(operation[4:]):
                    if item.startswith('"'):
                        items.append(item)
                    else:
                        items.append(item.lower())
                operation = '{0} {1}'.format(operation[:4].lower(), ','.join(items))
            else:
                operation = operation.lower()
        elif self.upper:
            addr_str = addr_str.upper()
            if operation.upper().startswith(('DEFB', 'DEFM')):
                items = []
                for item in get_defb_item_list(operation[4:]):
                    if item.startswith('"'):
                        items.append(item)
                    else:
                        items.append(item.upper())
                operation = '{0} {1}'.format(operation[:4].upper(), ','.join(items))
            else:
                operation = operation.upper()
        return addr_str, operation

    def apply_base(self, addr_str, operation):
        address = parse_int(addr_str)
        if self.decimal:
            if address is not None:
                addr_str = '{:05d}'.format(address)
            if operation:
                operation = self.convert(operation)
        elif self.hexadecimal:
            if address is not None:
                addr_str = self.hex4fmt.format(address)
            if operation:
                operation = self.convert(operation)
        return addr_str, operation

    def convert(self, operation):
        ops = operation.upper().split(None, 1)
        if len(ops) > 1:
            ops[1:] = ops[1].split(',')
        ops = [op.strip() for op in ops]

        index = byte = None
        if len(ops) == 2:
            # RL/RR/RRC/RLC/SLA/SRA/SLL/SRL/INC/DEC/AND/OR/XOR/SUB/CP (I[XY]+d)
            index = self.get_index(operation)
        elif len(ops) == 3:
            index = self.get_index(operation)
            if index:
                # LD (I[XY]+d),n; LD (I[XY]+d),r
                byte = parse_int(ops[2])
            else:
                # LD r,(I[XY]+d); BIT/SET/RES n,(I[XY]+d);
                # ADD/ADC/SBC A,(I[XY]+d)
                index = self.get_index(operation)
        if index:
            return self.replace_index(operation, index, byte)

        if ops[0] in ('DEFB', 'DEFM'):
            directive, item_str = operation.split(None, 1)
            items = []
            for item in get_defb_item_list(item_str):
                if item.startswith('"'):
                    items.append(item)
                else:
                    items.append(self.replace_byte(item, False))
            return '{0} {1}'.format(directive, ','.join(items))

        if ops[0] == 'DEFS':
            directive = operation.split(None, 1)[0]
            data = [self.replace_byte(b, False) for b in ops[1:]]
            return '{0} {1}'.format(directive, ','.join(data))

        if ops[0] == 'DEFW':
            directive = operation.split(None, 1)[0]
            words = [self.replace_address(w, False) for w in ops[1:]]
            return '{0} {1}'.format(directive, ','.join(words))

        if ops[0] in ('CALL', 'DJNZ', 'JP', 'JR'):
            # CALL [*,]nn, DJNZ nn, JP [*,]nn, JR [*,]nn
            return self.replace_address(operation)

        if ops[0] in ('AND', 'OR', 'XOR', 'SUB', 'CP', 'IN', 'OUT', 'ADD', 'ADC', 'SBC', 'RST'):
            # AND n; OR n; XOR n; SUB n; CP n; IN (n),A; OUT (n),A; ADD A,n;
            # ADC A,n; SBC A,n; RST n
            return self.replace_byte(operation)

        if ops[0] == 'LD':
            if ops[1] in ('A', 'B', 'C', 'D', 'E', 'H', 'L', 'IXL', 'IXH', 'IYL', 'IYH', '(HL)') and not ops[2].startswith('('):
                # LD r,n; LD (HL),n
                return self.replace_byte(operation)
            addr_ld_reg = ('A', 'BC', 'DE', 'HL', 'IX', 'IY', 'SP')
            if ops[1] in addr_ld_reg or ops[2] in addr_ld_reg:
                # LD A,(nn); LD (nn),A; LD rr,nn; LD rr,(nn); LD (nn),rr
                return self.replace_address(operation)

        return operation

    def get_index(self, op):
        return re.search('\([Ii][XYxy] *[\+-].*\)', op)

    def replace_index(self, operation, index, byte):
        match = index.group()
        marker = '_'
        operation = operation.replace(match, marker)
        if byte is not None:
            operation = self.replace_byte(operation)
        return operation.replace(marker, self.replace_byte(match))

    def replace_byte(self, text, check_prefix=True):
        return self.replace_number(text, 2, check_prefix)

    def replace_address(self, text, check_prefix=True):
        return self.replace_number(text, 4, check_prefix)

    def replace_number(self, text, digits, check_prefix):
        num_str = get_address(text, check_prefix)
        if num_str is None or num_str.startswith('%'):
            return text
        num = parse_int(num_str)
        if self.decimal:
            return text.replace(num_str, str(num))
        if self.hexadecimal:
            if digits <= 2 and num < 256:
                hex_fmt = self.hex2fmt
            else:
                hex_fmt = self.hex4fmt
            return text.replace(num_str, hex_fmt.format(num))

class Instruction:
    def __init__(self, ctl, addr_str, operation):
        self.ctl = ctl
        if addr_str[0].isdigit():
            self.addr_str = addr_str
        else:
            self.addr_str = addr_str[1:]
        self.address = parse_int(addr_str)
        self.label = ctl + addr_str
        self.operation = operation
        self.container = None
        self.reference = None
        self.comment = None
        self.referrers = []
        self.asm_label = None
        self.nolabel = False
        self.org = None
        # If this instruction has no address, it was inserted between
        # @rsub+begin and @rsub+end; in that case, mark it as a subbed
        # instruction already
        if self.address is None:
            self.sub = operation
        else:
            self.sub = None
        self.keep = False
        self.warn = True
        self.ignoreua = False
        self.ignoremrcua = False

    def set_comment(self, rowspan, text):
        self.comment = Comment(rowspan, text)

    def set_reference(self, entry, address, addr_str):
        self.reference = Reference(entry, address, addr_str)

    def add_referrer(self, routine):
        if routine not in self.referrers:
            self.referrers.append(routine)
        self.container.add_referrer(routine)

    def apply_sub(self, sub):
        self.sub = sub
        self.operation = sub

    def is_in_routine(self):
        return self.container.is_routine()

    def get_mid_routine_comment(self):
        return self.container.get_mid_routine_comment(self.label)

    def html_escape(self):
        self.operation = cgi.escape(self.operation)

    def get_addr_str(self, base):
        if (base is None and self.label[1].isdigit()) or base == BASE_10:
            return re.sub('^0{1,4}', '', self.addr_str)
        return self.addr_str

class Reference:
    def __init__(self, entry, address, addr_str):
        self.entry = entry
        self.address = address
        self.addr_str = addr_str

class Comment:
    def __init__(self, rowspan, text):
        self.rowspan = rowspan
        self.text = text

class SkoolEntry:
    def __init__(self, address, addr_str=None, ctl=None, description=None, details=(), registers=()):
        self.asm_id = ''
        self.address = address
        self.addr_str = addr_str
        self.ctl = ctl
        self.description = description
        self.details = details
        self.registers = [Register(prefix, name, contents) for prefix, name, contents in registers]
        self.instructions = []
        self.mid_routine_comments = {}
        self.end_comment = ()
        self.referrers = []
        self.size = None
        self.ignoreua = {'t': False, 'd': False, 'r': False, 'e': False}

    def is_routine(self):
        """Return whether the entry is a routine (code block)."""
        return self.ctl == 'c'

    def is_remote(self):
        """Return whether the entry is a remote entry."""
        return False

    def is_ignored(self):
        return self.ctl == 'i'

    def add_instruction(self, instruction):
        instruction.container = self
        self.instructions.append(instruction)

    def get_mid_routine_comment(self, address):
        return self.mid_routine_comments.get(address, ())

    def add_mid_routine_comment(self, address, text):
        self.mid_routine_comments[address] = text

    def add_referrer(self, routine):
        if routine not in self.referrers:
            self.referrers.append(routine)

class RemoteEntry(SkoolEntry):
    def __init__(self, asm_id, address):
        SkoolEntry.__init__(self, address)
        self.asm_id = asm_id

    def is_remote(self):
        return True

class Register:
    def __init__(self, prefix, name, contents):
        self.prefix = prefix
        self.name = name
        self.contents = contents

class TableParser:
    def parse_text(self, text, index):
        try:
            end = text.index(TABLE_END_MARKER, index) + len(TABLE_END_MARKER)
        except ValueError:
            marker = text[text.rindex('#', 0, index):index]
            raise SkoolParsingError("Missing table end marker: {}{}...".format(marker, text[index:index + 15]))
        return end, self.parse_table(text[index:end])

    def parse_table(self, table_def):
        text = table_def
        for ws_char in '\n\r\t':
            text = text.replace(ws_char, ' ')

        index = 0
        classes = []
        if text[index] == '(':
            end = text.find(')', index)
            if end < 0:
                raise SkoolParsingError("Cannot find closing ')' in table CSS class list:\n{0}".format(table_def))
            classes = [c.strip() for c in text[index + 1:end].split(',')]
            index = end + 1
        if classes:
            table_class = classes[0]
        else:
            table_class = ''
        column_classes = classes[1:]
        wrap_columns = []
        for i, column_class in enumerate(column_classes):
            if column_class.endswith(COLUMN_WRAP_MARKER):
                column_classes[i] = column_class[:-len(COLUMN_WRAP_MARKER)]
                wrap_columns.append(i)
        table = Table(table_class, wrap_columns)

        prev_spans = {}
        while text.find('{', index) >= 0:
            row = []
            row_start = text.find('{ ', index)
            if row_start < 0:
                raise SkoolParsingError("Cannot find opening '{{ ' in table row:\n{0}".format(table_def))
            row_end = text.find(' }', row_start)
            if row_end < 0:
                raise SkoolParsingError("Cannot find closing ' }}' in table row:\n{0}".format(table_def))
            col_index = 0
            for cell in text[row_start + 1:row_end + 1].split(' | '):
                prev_rowspan, prev_colspan = prev_spans.get(col_index, (1, 1))
                while prev_rowspan > 1:
                    prev_spans[col_index] = (prev_rowspan - 1, prev_colspan)
                    col_index += prev_colspan
                    prev_rowspan, prev_colspan = prev_spans.get(col_index, (1, 1))
                header, transparent = False, False
                rowspan, colspan = 1, 1
                if len(column_classes) > col_index:
                    cell_class = column_classes[col_index]
                else:
                    cell_class = ''
                cell = cell.strip()
                if cell.startswith('='):
                    end = cell.find(' ')
                    if end < 0:
                        end = len(cell)
                    for span in cell[1:end].split(','):
                        if span[0] == 'c':
                            colspan = int(span[1:])
                        elif span[0] == 'r':
                            rowspan = int(span[1:])
                        elif span[0] == 'h':
                            header = True
                        elif span[0] == 't':
                            transparent = True
                    cell = cell[end:].lstrip()
                row.append(Cell(cell, transparent, colspan, rowspan, header, cell_class))
                prev_spans[col_index] = (rowspan, colspan)
                col_index += colspan

            # Deal with the case where the previous row contains one or more
            # cells at the end with rowspan > 1
            while col_index in prev_spans:
                prev_rowspan, prev_colspan = prev_spans[col_index]
                if prev_rowspan > 1:
                    prev_spans[col_index] = (prev_rowspan - 1, prev_colspan)
                col_index += prev_colspan

            table.add_row(row)
            index = row_end + 1

        return table

class Table:
    def __init__(self, table_class, wrap_columns):
        self.table_class = table_class
        self.wrap_columns = wrap_columns
        self.rows = []
        self.cells = []
        self.col_widths = None
        self.cell_padding = None
        self.num_cols = None

    def add_row(self, cells):
        self.rows.append(cells)
        self.cells.extend(cells)

    def prepare_cells(self):
        # For each cell, set row_index and col_index, and convert the contents
        # to a 1-item list. Also calculate num_cols and col_widths.
        prev_spans = {}
        for row_index, row in enumerate(self.rows):
            col_index = 0
            for cell in row:
                while True:
                    prev_rowspan, prev_colspan = prev_spans.get(col_index, (1, 1))
                    if prev_rowspan == 1:
                        break
                    prev_spans[col_index] = (prev_rowspan - 1, prev_colspan)
                    col_index += prev_colspan
                cell.row_index, cell.col_index = row_index, col_index
                cell.contents = [cell.contents]
                prev_spans[col_index] = (cell.rowspan, cell.colspan)
                col_index += cell.colspan

            # Deal with cells at the end of the previous row that have rowspan
            # greater than 1
            while col_index in prev_spans:
                prev_rowspan, prev_colspan = prev_spans[col_index]
                if prev_rowspan > 1:
                    prev_spans[col_index] = (prev_rowspan - 1, prev_colspan)
                col_index += prev_colspan

        if self.rows:
            self.num_cols = 1 + max([cell.col_index for cell in [row[-1] for row in self.rows]])
        else:
            self.num_cols = 0
        self._calculate_col_widths()

    def get_header_rows(self):
        headers = []
        for i, row in enumerate(self.rows):
            if len([c for c in row if not (c.transparent or c.header)]) == 0:
                headers.append(i)
        return headers

    def get_cell_width(self, col_index, colspan):
        return sum(self.col_widths[col_index:col_index + colspan]) + self.cell_padding * (colspan - 1)

    def _calculate_col_widths(self):
        # Loop over the cells to collect their widths (considering only those
        # cells with colspan=1 on this pass)
        cell_widths = [[0] * self.num_cols for row in self.rows]
        for cell in [c for c in self.cells if c.colspan == 1]:
            cell_widths[cell.row_index][cell.col_index] = cell.get_width()

        # Scan each column to find the widest cell; the width of that cell will
        # be the width of the column
        self.col_widths = [max([row[i] for row in cell_widths]) for i in range(self.num_cols)]

        # Scan the cells again to make sure that those with colspan > 1 have
        # enough space
        for cell in [c for c in self.cells if c.colspan > 1]:
            col_index, colspan = cell.col_index, cell.colspan
            space_needed = cell.get_width() - self.get_cell_width(col_index, colspan)
            while space_needed > 0:
                for j in range(colspan):
                    if space_needed > 0:
                        self.col_widths[col_index + j] += 1
                        space_needed -= 1

    def reduce_width(self, max_table_width, min_col_width):
        # Reduce the width of the wrappable columns until either the table is
        # narrow enough or all the wrappable columns are the minimum width
        done = False
        while self.get_width() > max_table_width and not done:
            done = True
            for wrap_col in self.wrap_columns:
                if self.col_widths[wrap_col] > min_col_width:
                    self.col_widths[wrap_col] -= 1
                    done = False

        # Wrap the contents of the cells in the wrappable columns
        for cell in [c for c in self.cells if c.col_index in self.wrap_columns]:
            width = self.get_cell_width(cell.col_index, cell.colspan)
            cell.contents = wrap(cell.contents[0], width) or ['']

        # The column widths need to be recalculated now
        self._calculate_col_widths()

    def get_width(self):
        padding = self.cell_padding * (self.num_cols + 1) - 2
        return padding + sum(self.col_widths)

class Cell:
    def __init__(self, contents, transparent, colspan, rowspan, header, cell_class):
        self.contents = contents
        self.colspan = colspan
        self.rowspan = rowspan
        self.header = header
        self.transparent = transparent
        self.cell_class = cell_class
        self.row_index = None
        self.col_index = None

    def get_width(self):
        return max([len(line) for line in self.contents])

class ListParser:
    def parse_text(self, text, index):
        try:
            end = text.index(LIST_END_MARKER, index) + len(LIST_END_MARKER)
        except ValueError:
            raise SkoolParsingError("No end marker: #LIST{}...".format(text[index:index + 15]))
        return end, self.parse_list(text[index:end])

    def parse_list(self, list_def):
        text = list_def
        for ws_char in '\n\r\t':
            text = text.replace(ws_char, ' ')

        index = 0
        css_class = ''
        if text[index] == '(':
            end = text.find(')', index)
            if end < 0:
                raise SkoolParsingError("Cannot find closing ')' in parameter list:\n{0}".format(list_def))
            css_class = text[index + 1:end].strip()
            index = end + 1
        list_obj = List(css_class)

        while text.find('{', index) >= 0:
            item_start = text.find('{ ', index)
            if item_start < 0:
                raise SkoolParsingError("Cannot find opening '{{ ' in list item:\n{0}".format(list_def))
            item_end = text.find(' }', item_start)
            if item_end < 0:
                raise SkoolParsingError("Cannot find closing ' }}' in list item:\n{0}".format(list_def))
            list_obj.add_item(text[item_start + 1:item_end].strip())
            index = item_end + 2

        return list_obj

class List:
    def __init__(self, css_class):
        self.css_class = css_class
        self.items = []

    def add_item(self, text):
        self.items.append(text)
