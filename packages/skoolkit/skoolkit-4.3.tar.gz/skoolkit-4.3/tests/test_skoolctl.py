# -*- coding: utf-8 -*-
import unittest

from skoolkittest import SkoolKitTestCase
from skoolkit.skoolctl import CtlWriter

DIRECTIVES = 'bcgistuw'

TEST_SKOOL = r"""; Dangling comment not associated with any entry

; Data definition entry (ignored)
d49153 DEFW 0       ; A comment over two lines
                    ; (also ignored)

; Remote entry (ignored)
r24576 start

; Address 0
; @label=START0
c00000 RET

; Address with 1 digit
@label=START1
c00001 RET

; Address with 2 digits
; @label=START33
c00033 RET

; Address with 3 digits
@label=START555
c00555 RET

; Address with 4 digits
; @label=START7890
c07890 RET

; @start
@writer=package.module.classname
; @set-bullet=+
@org=32768
; Routine
;
; Routine description
;
; A Some value
; B Another value
;
; Start comment
@label=START
c32768 NOP          ; Do nothing
; @bfix=DEFB 2,3
 32769 DEFB 1,2     ; 1-line B sub-block
@nowarn
 32771 defb 3       ; {2-line B sub-block
; @isub=DEFB 0,1
 32772 DEFB 4,5     ; }
; Mid-block comment
 32774 DEFM "Hello" ; T sub-block
@keep
 32779 DEFW 12345   ; W sub-block
 32781 defs 2       ; S sub-block
; @nolabel
 32783 LD A,5       ; {Sub-block with instructions of various types
; @ofix=DEFB 2
 32785 DEFB 0       ;
@rsub=DEFW 0,1,2
 32786 DEFW 0,1     ; and blank lines
@ssub=DEFM "Lo"
 32790 defm "H",105 ;
 32792 DEFS 3       ; in the comment}
 $801B RET          ; Instruction with a
                    ; comment continuation line
; End comment paragraph 1.
; .
; End comment paragraph 2.

; Ignore block
i32796

; Data block
; @rem=Hello!
b49152 DEFB 0

; Game status buffer entry
g49153 defw 0

; Message
t49155 DEFM "Lo"

; Unused block
u49157 DEFB 128

; Word block
w49158 DEFW 2
 49160 DEFW 4

; Data block beginning with a 1-byte sub-block
b49162 DEFB 0
 49163 RET

; Text block beginning with a 1-byte sub-block
t49164 DEFM "a"
 49165 RET

; Word block beginning with a 2-byte sub-block
w49166 DEFW 23
 49168 RET

; Zero block
s49169 DEFS 9
 49178 RET

; Data block with sub-block lengths amenable to abbreviation (2*3,3*2,1)
b49179 DEFB 0,0
 49181 DEFB 0,0
 49183 DEFB 0,0
 49185 DEFB 0,0,0
 49188 DEFB 0,0,0
 49191 DEFB 0
 49192 DEFB 0

; ASM block directives
@bfix-begin
b49193 DEFB 7
; @bfix+else
c49193 NOP
@bfix+end

; Zero block
s49194 DEFS 128
 49322 DEFS 128
 49450 DEFS 128
; @end

; Complex DEFB statements
b49578 DEFB 1,2,3,"Hello",5,6
 49588 DEFB "Goodbye",7,8,9

; Complex DEFM statements
t49598 DEFM "\"Hi!\"",1,2,3,4,5
 49608 DEFM 6,"C:\\DOS>",7,8

; Data block with sequences of complex DEFB statements amenable to abbreviation
b49618 DEFB 1,"Hi"
 49621 DEFB 4,"Lo"
 49624 DEFB 7
 49625 DEFB 8,9,"A"
 49628 DEFB 10,11,"B"
 49631 DEFB 12,13,"C"

; Routine with an empty block description and a register section
;
; .
;
; BC 0
c49634 RET

; Routine with an empty multi-instruction comment and instruction comments that
; start with a '.'
c49635 XOR B ; {
 49636 XOR C ; }
 49637 XOR D ; {...and so on
 49638 XOR E ; }
 49639 XOR H ; {...
 49640 XOR L ; }
 49641 XOR A ; ...
 49642 RET   ; ...until the end

; Another ignore block
i49643
; End comment on the final block.
"""

TEST_CTL = """c 00000 Address 0
@ 00000 label=START0
c 00001 Address with 1 digit
@ 00001 label=START1
c 00033 Address with 2 digits
@ 00033 label=START33
c 00555 Address with 3 digits
@ 00555 label=START555
c 07890 Address with 4 digits
@ 07890 label=START7890
@ 32768 start
@ 32768 writer=package.module.classname
@ 32768 set-bullet=+
@ 32768 org=32768
c 32768 Routine
D 32768 Routine description
R 32768 A Some value
R 32768 B Another value
N 32768 Start comment
@ 32768 label=START
  32768,1 Do nothing
@ 32769 bfix=DEFB 2,3
B 32769,2,2 1-line B sub-block
@ 32771 nowarn
@ 32772 isub=DEFB 0,1
B 32771,3,1,2 2-line B sub-block
N 32774 Mid-block comment
T 32774,5,5 T sub-block
@ 32779 keep
W 32779,2,2 W sub-block
S 32781,2,2 S sub-block
M 32783,12 Sub-block with instructions of various types and blank lines in the comment
@ 32783 nolabel
@ 32785 ofix=DEFB 2
B 32785,1,1
@ 32786 rsub=DEFW 0,1,2
W 32786,4,4
@ 32790 ssub=DEFM "Lo"
T 32790,2,1:B1
S 32792,3,3
  32795 Instruction with a comment continuation line
E 32768 End comment paragraph 1.
E 32768 End comment paragraph 2.
i 32796 Ignore block
b 49152 Data block
@ 49152 rem=Hello!
  49152,1,1
g 49153 Game status buffer entry
W 49153,2,2
t 49155 Message
  49155,2,2
u 49157 Unused block
  49157,1,1
w 49158 Word block
  49158,4,2
b 49162 Data block beginning with a 1-byte sub-block
  49162,1,1
C 49163
t 49164 Text block beginning with a 1-byte sub-block
  49164,1,1
C 49165
w 49166 Word block beginning with a 2-byte sub-block
  49166,2,2
C 49168
s 49169 Zero block
  49169,9,9
C 49178
b 49179 Data block with sub-block lengths amenable to abbreviation (2*3,3*2,1)
  49179,14,2*3,3*2,1
b 49193 ASM block directives
  49193,1,1
s 49194 Zero block
  49194,384,128
@ 49194 end
b 49578 Complex DEFB statements
  49578,20,3:T5:2,T7:3
t 49598 Complex DEFM statements
  49598,20,5:B5,B1:7:B2
b 49618 Data block with sequences of complex DEFB statements amenable to abbreviation
  49618,16,1:T2*2,1,2:T1
c 49634 Routine with an empty block description and a register section
R 49634 BC 0
c 49635 Routine with an empty multi-instruction comment and instruction comments that start with a '.'
  49635,2 .
  49637,2 ...and so on
  49639,2 ....
  49641,1 ...
  49642 ...until the end
i 49643 Another ignore block
E 49643 End comment on the final block.""".split('\n')

TEST_CTL_HEX = """c $0000 Address 0
@ $0000 label=START0
c $0001 Address with 1 digit
@ $0001 label=START1
c $0021 Address with 2 digits
@ $0021 label=START33
c $022B Address with 3 digits
@ $022B label=START555
c $1ED2 Address with 4 digits
@ $1ED2 label=START7890
@ $8000 start
@ $8000 writer=package.module.classname
@ $8000 set-bullet=+
@ $8000 org=32768
c $8000 Routine
D $8000 Routine description
R $8000 A Some value
R $8000 B Another value
N $8000 Start comment
@ $8000 label=START
  $8000,1 Do nothing
@ $8001 bfix=DEFB 2,3
B $8001,2,2 1-line B sub-block
@ $8003 nowarn
@ $8004 isub=DEFB 0,1
B $8003,3,1,2 2-line B sub-block
N $8006 Mid-block comment
T $8006,5,5 T sub-block
@ $800B keep
W $800B,2,2 W sub-block
S $800D,2,2 S sub-block
M $800F,12 Sub-block with instructions of various types and blank lines in the comment
@ $800F nolabel
@ $8011 ofix=DEFB 2
B $8011,1,1
@ $8012 rsub=DEFW 0,1,2
W $8012,4,4
@ $8016 ssub=DEFM "Lo"
T $8016,2,1:B1
S $8018,3,3
  $801B Instruction with a comment continuation line
E $8000 End comment paragraph 1.
E $8000 End comment paragraph 2.
i $801C Ignore block
b $C000 Data block
@ $C000 rem=Hello!
  $C000,1,1
g $C001 Game status buffer entry
W $C001,2,2
t $C003 Message
  $C003,2,2
u $C005 Unused block
  $C005,1,1
w $C006 Word block
  $C006,4,2
b $C00A Data block beginning with a 1-byte sub-block
  $C00A,1,1
C $C00B
t $C00C Text block beginning with a 1-byte sub-block
  $C00C,1,1
C $C00D
w $C00E Word block beginning with a 2-byte sub-block
  $C00E,2,2
C $C010
s $C011 Zero block
  $C011,9,9
C $C01A
b $C01B Data block with sub-block lengths amenable to abbreviation (2*3,3*2,1)
  $C01B,14,2*3,3*2,1
b $C029 ASM block directives
  $C029,1,1
s $C02A Zero block
  $C02A,384,128
@ $C02A end
b $C1AA Complex DEFB statements
  $C1AA,20,3:T5:2,T7:3
t $C1BE Complex DEFM statements
  $C1BE,20,5:B5,B1:7:B2
b $C1D2 Data block with sequences of complex DEFB statements amenable to abbreviation
  $C1D2,16,1:T2*2,1,2:T1
c $C1E2 Routine with an empty block description and a register section
R $C1E2 BC 0
c $C1E3 Routine with an empty multi-instruction comment and instruction comments that start with a '.'
  $C1E3,2 .
  $C1E5,2 ...and so on
  $C1E7,2 ....
  $C1E9,1 ...
  $C1EA ...until the end
i $C1EB Another ignore block
E $C1EB End comment on the final block.""".split('\n')

TEST_CTL_BS = """c 00000
c 00001
c 00033
c 00555
c 07890
c 32768
B 32769,2,2
B 32771,3,1,2
T 32774,5,5
W 32779,2,2
S 32781,2,2
B 32785,1,1
W 32786,4,4
T 32790,2,1:B1
S 32792,3,3
i 32796
b 49152
  49152,1,1
g 49153
W 49153,2,2
t 49155
  49155,2,2
u 49157
  49157,1,1
w 49158
  49158,4,2
b 49162
  49162,1,1
C 49163
t 49164
  49164,1,1
C 49165
w 49166
  49166,2,2
C 49168
s 49169
  49169,9,9
C 49178
b 49179
  49179,14,2*3,3*2,1
b 49193
  49193,1,1
s 49194
  49194,384,128
b 49578
  49578,20,3:T5:2,T7:3
t 49598
  49598,20,5:B5,B1:7:B2
b 49618
  49618,16,1:T2*2,1,2:T1
c 49634
c 49635
i 49643""".split('\n')

TEST_CTL_BSC = """c 00000
c 00001
c 00033
c 00555
c 07890
c 32768
  32768,1 Do nothing
B 32769,2,2 1-line B sub-block
B 32771,3,1,2 2-line B sub-block
T 32774,5,5 T sub-block
W 32779,2,2 W sub-block
S 32781,2,2 S sub-block
M 32783,12 Sub-block with instructions of various types and blank lines in the comment
B 32785,1,1
W 32786,4,4
T 32790,2,1:B1
S 32792,3,3
  32795 Instruction with a comment continuation line
i 32796
b 49152
  49152,1,1
g 49153
W 49153,2,2
t 49155
  49155,2,2
u 49157
  49157,1,1
w 49158
  49158,4,2
b 49162
  49162,1,1
C 49163
t 49164
  49164,1,1
C 49165
w 49166
  49166,2,2
C 49168
s 49169
  49169,9,9
C 49178
b 49179
  49179,14,2*3,3*2,1
b 49193
  49193,1,1
s 49194
  49194,384,128
b 49578
  49578,20,3:T5:2,T7:3
t 49598
  49598,20,5:B5,B1:7:B2
b 49618
  49618,16,1:T2*2,1,2:T1
c 49634
c 49635
  49635,2 .
  49637,2 ...and so on
  49639,2 ....
  49641,1 ...
  49642 ...until the end
i 49643""".split('\n')

TEST_BYTE_FORMATS_SKOOL = """; Binary and mixed-base DEFB/DEFM statements
b30000 DEFB %10111101,$42,26
 30003 DEFB $38,$39,%11110000,%00001111,24,25,26
 30010 DEFB %11111111,%10000001
 30012 DEFB 47,34,56
 30015 DEFB $1A,$00,$00,$00,$A2
 30020 DEFB "hello"
 30025 DEFB %10101010,"hi",24,$56
 30030 DEFM %10111101,$42,26
 30033 DEFM $38,$39,%11110000,%00001111,24,25,26
 30040 DEFM %11111111,%10000001
 30042 DEFM 47,34,56
 30045 DEFM $1A,$00,$00,$00,$A2
 30050 DEFM "hello"
 30055 DEFM %10101010,"hi",24,$56
"""

TEST_WORD_FORMATS_SKOOL = """; Binary and mixed-base DEFW statements
w40000 DEFW %1111000000001111,%1111000000001111
 40004 DEFW 12345,12345,12345
 40010 DEFW $AB0C,$CD32,$102F,$0000
 40018 DEFW 54321,%1010101010101010,$F001
 40024 DEFW $1234,$543C,%1111111100000000,2345,9876
 40034 DEFW $2345,$876D,%1001001010001011,3456,8765
 40044 DEFW 65535,65534
 40048 DEFW 1,2
 40052 DEFW $0000,$FFFF
 40056 DEFW $1000,$2FFF
 40060 DEFW %0101010111110101,%1111111111111111
 40064 DEFW %1101010111110101,%0000000000000001
"""

TEST_S_DIRECTIVES_SKOOL = """; DEFS statements in various bases
s50000 DEFS %0000000111110100
 50500 DEFS 1000
 51500 DEFS $07D0
 53500 DEFS 500,%10101010
 54000 DEFS $0100,170
"""

class CtlWriterTest(SkoolKitTestCase):
    def _get_ctl(self, elements='btdrmsc', write_hex=False, write_asm_dirs=True, skool=TEST_SKOOL, preserve_base=False):
        skoolfile = self.write_text_file(skool, suffix='.skool')
        writer = CtlWriter(skoolfile, elements, write_hex, write_asm_dirs, preserve_base)
        writer.write()
        return self.out.getvalue().split('\n')[:-1]

    def test_default_elements(self):
        self.assertEqual(TEST_CTL, self._get_ctl())

    def test_default_elements_hex(self):
        self.assertEqual(TEST_CTL_HEX, self._get_ctl(write_hex=True))

    def test_default_elements_no_asm_dirs(self):
        ctl = self._get_ctl(write_asm_dirs=False)
        test_ctl = [line for line in TEST_CTL if not line.startswith('@')]
        self.assertEqual(test_ctl, ctl)

    def test_wb(self):
        ctl = self._get_ctl('b', write_asm_dirs=False)
        test_ctl = [line[:7] for line in TEST_CTL if line[0] in DIRECTIVES]
        self.assertEqual(test_ctl, ctl)

    def test_wbd(self):
        ctl = self._get_ctl('bd', write_asm_dirs=False)
        test_ctl = []
        for line in TEST_CTL:
            if line[0] in DIRECTIVES:
                test_ctl.append(line[:7])
            elif line.startswith('D 32768'):
                test_ctl.append(line)
        self.assertEqual(test_ctl, ctl)

    def test_wbm(self):
        ctl = self._get_ctl('bm', write_asm_dirs=False)
        test_ctl = []
        for line in TEST_CTL:
            if line[0] in DIRECTIVES:
                test_ctl.append(line[:7])
            elif line[0] in 'NE':
                test_ctl.append(line)
        self.assertEqual(test_ctl, ctl)

    def test_wbr(self):
        ctl = self._get_ctl('br', write_asm_dirs=False)
        test_ctl = []
        for line in TEST_CTL:
            if line[0] in DIRECTIVES:
                test_ctl.append(line[:7])
            elif line[0] == 'R':
                test_ctl.append(line)
        self.assertEqual(test_ctl, ctl)

    def test_wbs(self):
        ctl = self._get_ctl('bs', write_asm_dirs=False)
        self.assertEqual(TEST_CTL_BS, ctl)

    def test_wbsc(self):
        ctl = self._get_ctl('bsc', write_asm_dirs=False)
        self.assertEqual(TEST_CTL_BSC, ctl)

    def test_wbt(self):
        ctl = self._get_ctl('bt', write_asm_dirs=False)
        test_ctl = [line for line in TEST_CTL if line[0] in DIRECTIVES]
        self.assertEqual(test_ctl, ctl)

    def test_byte_formats_no_base(self):
        ctl = self._get_ctl(skool=TEST_BYTE_FORMATS_SKOOL, preserve_base=False)
        exp_ctl = [
            'b 30000 Binary and mixed-base DEFB/DEFM statements',
            '  30000,30,b1:2,2:b2:3,b2,3,5,T5,b1:T2:2',
            'T 30030,30,b1:B2,B2:b2:B3,b2,B3,B5,5,b1:2:B2'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_byte_formats_preserve_base(self):
        ctl = self._get_ctl(skool=TEST_BYTE_FORMATS_SKOOL, preserve_base=True)
        exp_ctl = [
            'b 30000 Binary and mixed-base DEFB/DEFM statements',
            '  30000,30,b1:h1:d1,h2:b2:d3,b2,d3,h5,T5,b1:T2:d1:h1',
            'T 30030,30,b1:h1:d1,h2:b2:d3,b2,d3,h5,5,b1:2:d1:h1'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_word_formats_no_base(self):
        ctl = self._get_ctl(skool=TEST_WORD_FORMATS_SKOOL, preserve_base=False)
        exp_ctl = [
            'w 40000 Binary and mixed-base DEFW statements',
            '  40000,68,b4,6,8,2:b2:2,4:b2:4*2,4*4,b4'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_word_formats_preserve_base(self):
        ctl = self._get_ctl(skool=TEST_WORD_FORMATS_SKOOL, preserve_base=True)
        exp_ctl = [
            'w 40000 Binary and mixed-base DEFW statements',
            '  40000,68,b4,d6,h8,d2:b2:h2,h4:b2:d4*2,d4*2,h4*2,b4'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_s_directives_no_base(self):
        ctl = self._get_ctl(skool=TEST_S_DIRECTIVES_SKOOL, preserve_base=False)
        exp_ctl = [
            's 50000 DEFS statements in various bases',
            '  50000,4256,b%0000000111110100,1000,$07D0,500:b%10101010,$0100:170'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_s_directives_preserve_base(self):
        ctl = self._get_ctl(skool=TEST_S_DIRECTIVES_SKOOL, preserve_base=True)
        exp_ctl = [
            's 50000 DEFS statements in various bases',
            '  50000,4256,b%0000000111110100,d1000,h$07D0,d500:b%10101010,h$0100:d170'
        ]
        self.assertEqual(exp_ctl, ctl)

    def test_ignoreua_directives(self):
        skool = '\n'.join((
            '; @ignoreua',
            '; Routine at 30000',
            'c30000 RET',
            '',
            '; Routine',
            ';',
            '@ignoreua',
            '; Description of the routine at 30001',
            ';',
            '; @ignoreua',
            '; HL 30001',
            '@ignoreua',
            'c30001 RET    ; Instruction-level comment at 30001',
            '',
            '; Routine',
            'c30002 LD A,B',
            '; @ignoreua',
            '; Mid-block comment above 30003.',
            '@ignoreua',
            ' 30003 RET    ; Instruction-level comment at 30003',
            '',
            '; Routine',
            '; @ignoreua',
            'c30004 LD A,C ; Instruction-level comment at 30004',
            '@ignoreua',
            '; Mid-block comment above 30005.',
            ' 30005 RET',
            '; @ignoreua',
            '; End comment for the routine at 30004.'
        ))
        exp_ctl = [
            '@ 30000 ignoreua:t',
            'c 30000 Routine at 30000',
            'c 30001 Routine',
            '@ 30001 ignoreua:d',
            'D 30001 Description of the routine at 30001',
            '@ 30001 ignoreua:r',
            'R 30001 HL 30001',
            '@ 30001 ignoreua:i',
            '  30001 Instruction-level comment at 30001',
            'c 30002 Routine',
            '@ 30003 ignoreua:m',
            'N 30003 Mid-block comment above 30003.',
            '@ 30003 ignoreua:i',
            '  30003 Instruction-level comment at 30003',
            'c 30004 Routine',
            '@ 30004 ignoreua:i',
            '  30004,1 Instruction-level comment at 30004',
            '@ 30005 ignoreua:m',
            'N 30005 Mid-block comment above 30005.',
            '@ 30004 ignoreua:e',
            'E 30004 End comment for the routine at 30004.'
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_ignoreua_directive_on_start_comment(self):
        skool = '\n'.join((
            '; Routine',
            ';',
            '; .',
            ';',
            '; .',
            ';',
            '; @ignoreua',
            '; Start comment above 30000.',
            'c30000 RET'
        ))
        exp_ctl = [
            'c 30000 Routine',
            '@ 30000 ignoreua:m',
            'N 30000 Start comment above 30000.'
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_ignoreua_directives_hex(self):
        skool = '\n'.join((
            '; @ignoreua',
            '; Routine at 40000',
            ';',
            '; @ignoreua',
            '; Description of the routine at 40000',
            ';',
            '; @ignoreua',
            '; HL 40000',
            '; @ignoreua',
            'c40000 LD A,B ; Instruction-level comment at 40000',
            '; @ignoreua',
            '; Mid-block comment above 40001.',
            ' 40001 RET',
            '; @ignoreua',
            '; End comment for the routine at 40000.'
        ))
        exp_ctl = [
            '@ $9C40 ignoreua:t',
            'c $9C40 Routine at 40000',
            '@ $9C40 ignoreua:d',
            'D $9C40 Description of the routine at 40000',
            '@ $9C40 ignoreua:r',
            'R $9C40 HL 40000',
            '@ $9C40 ignoreua:i',
            '  $9C40,1 Instruction-level comment at 40000',
            '@ $9C41 ignoreua:m',
            'N $9C41 Mid-block comment above 40001.',
            '@ $9C40 ignoreua:e',
            'E $9C40 End comment for the routine at 40000.'
        ]
        ctl = self._get_ctl(write_hex=True, skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_registers(self):
        skool = '\n'.join((
            '; Routine',
            ';',
            '; .',
            ';',
            '; BC This register description is long enough that it needs to be',
            ';   .split over two lines',
            '; DE Short register description',
            '; HL Another register description that is long enough to need',
            '; .  splitting over two lines',
            '; IX',
            'c40000 RET'
        ))
        exp_ctl = [
            'c 40000 Routine',
            'R 40000 BC This register description is long enough that it needs to be split over two lines',
            'R 40000 DE Short register description',
            'R 40000 HL Another register description that is long enough to need splitting over two lines',
            'R 40000 IX'
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_register_prefixes(self):
        skool = '\n'.join((
            '; Test registers with prefixes',
            ';',
            '; .',
            ';',
            '; Input:A Some value',
            ';       B Some other value',
            '; Output:HL The result',
            'c24576 RET'
        ))
        exp_ctl = [
            'c 24576 Test registers with prefixes',
            'R 24576 Input:A Some value',
            'R 24576 B Some other value',
            'R 24576 Output:HL The result'
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_start_comment(self):
        start_comment = 'This is a start comment.'
        skool = '\n'.join((
            '; Routine',
            ';',
            '; Description',
            ';',
            '; .',
            ';',
            '; {}'.format(start_comment),
            'c50000 RET'
        ))
        exp_ctl = [
            'c 50000 Routine',
            'D 50000 Description',
            'N 50000 {}'.format(start_comment)
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

    def test_multi_paragraph_start_comment(self):
        start_comment = ('Start comment paragraph 1.', 'Paragraph 2.')
        skool = '\n'.join((
            '; Routine',
            ';',
            '; .',
            ';',
            '; .',
            ';',
            '; {}',
            '; .',
            '; {}',
            'c60000 RET'
        )).format(*start_comment)
        exp_ctl = [
            'c 60000 Routine',
            'N 60000 {}'.format(start_comment[0]),
            'N 60000 {}'.format(start_comment[1])
        ]
        ctl = self._get_ctl(skool=skool)
        self.assertEqual(exp_ctl, ctl)

if __name__ == '__main__':
    unittest.main()
