#!/usr/bin/env python
import os
import plot_contact_map

path = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-1])
seq = path + os.sep + 'sequence.fasta'
c = path + os.sep + 'predicted.contacts'
c2 = path + os.sep + 'predicted.contacts2'
pp = path + os.sep + 'psipred.horiz'
pdb = path + os.sep + 'native_structure.pdb'
factor = 1.0
sep = sep2 = ''

plot_contact_map.plot_map(seq, c, factor, sep=sep, outfilename='cm_simple.pdf')
plot_contact_map.plot_map(seq, c, factor, psipred_filename=pp, pdb_filename=pdb, sep=sep, outfilename='cm_pdb.pdf')
plot_contact_map.plot_map(seq, c, factor, c2_filename=c2, psipred_filename=pp, sep=sep, sep2=sep2, outfilename='cm_compare.pdf')
plot_contact_map.plot_map(seq, c, factor, c2_filename=c2, psipred_filename=pp, pdb_filename=pdb, sep=sep, sep2=sep2, outfilename='cm_compare_pdb.pdf')

