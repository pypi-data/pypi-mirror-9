#!/usr/bin/python
# -*- coding: latin-1 -*-

import gr

gr.selntran(0)
gr.settextfontprec(2, 0)
gr.setcharheight(0.024)

gr.text(0.05, 0.85, ' !"#$%&\'()*+,-./')
gr.text(0.05, 0.80, '0123456789:;<=>?')
gr.text(0.05, 0.75, '@ABCDEFGHIJKLMNO')
gr.text(0.05, 0.70, 'PQRSTUVWXYZ[\]^_')
gr.text(0.05, 0.65, '`abcdefghijklmno')
gr.text(0.05, 0.60, '"pqrstuvwxyz{|}~')

gr.text(0.5, 0.85, '����������������')
gr.text(0.5, 0.80, '����������������')
gr.text(0.5, 0.75, '����������������')
gr.text(0.5, 0.70, '����������������')
gr.text(0.5, 0.65, '����������������')
gr.text(0.5, 0.60, '����������������')

gr.updatews()

