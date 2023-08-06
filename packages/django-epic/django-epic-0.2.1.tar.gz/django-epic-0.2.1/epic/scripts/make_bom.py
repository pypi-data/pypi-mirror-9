#
#   Copyright (c) 2014-2015 eGauge Systems LLC
# 	4730 Walnut St, Suite 110
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
"""This is a KiCad Eeschema plugin that uses EPIC parts information to:

	1) generate a BOM as a text file
	2) generate a Cmp file to associate a footprint to each component
	3) create an EPIC assembly ("PCB") consisting of the BOM components

The EPIC assembly created by this tool will have it's manufacturer set
to epic.MANUFACTURER and the manufacturer's part-number will be set to
'bom:' with the name of the schematic appended.  If an assembly with
that part-number already exists, it will be update UNLESS the BOM was
edited manually inside EPIC.  In the latter case, you can force
overwriting the manually edited BOM pass passing this scrit the
--force-overwrite command-line option.

"""

from __future__ import print_function

import argparse
import os
import sys
import xml.etree.ElementTree as ET

# Please replace 'epic-sample' with the name of your Django project:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epic-sample.epic-sample.settings')

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from epic import MANUFACTURER
from epic.models import Part, format_part_number, Assembly_Item, strchoice

from os import path

MY_TOOL_NAME = 'make-bom'

class Component:
    def __init__(self, part_id=None, refdes=None, value=None, footprint=None,
                 mfg=None, mfg_pn=None):
        self.part_id = part_id
        self.part = None
        self.refdes = refdes
        self.value = value
        self.footprint = footprint
        self.mfg = mfg
        self.mfg_pn = mfg_pn

    def __str__(self):
        res = 'Component('
        sep = ''
        for f in dir(self):
            if f[0] == '_':
                continue
            val = self.__dict__[f]
            if val != None:
                res += '%s%s=%s' % (sep, f, val)
                sep = ','
        res += ')'
        return res

def quote(str):
    str.replace('"', '\"')
    return '"' + str + '"'

@transaction.atomic
def save_assembly(assembly_part, bom):
    created = assembly_part.id is None

    assembly_part.last_bom_mod_type = Part.LAST_MOD_TYPE_TOOL
    assembly_part.last_bom_mod_name = MY_TOOL_NAME
    assembly_part.save()

    Assembly_Item.objects.filter(assy_id=assembly_part.id).delete()

    for components in bom:
        comp = components[0]
        refdes = ','.join(c.refdes for c in components)
        item = Assembly_Item(assy_id=assembly_part.id,
                             comp_id=comp.part_id,
                             qty=len(components),
                             refdes=refdes)
        item.save()
    print('%s: %s part %s (%s %s) with %d components' \
          % (MY_TOOL_NAME, 'created' if created else 'updated',
             format_part_number(assembly_part.id),
             assembly_part.mfg, assembly_part.mfg_pn, len(bom)))

parser = argparse.ArgumentParser(description =
                                 'Create BOM from eeschema XML file.')
parser.add_argument('input-file', nargs = 1)
parser.add_argument('output-file', nargs = 1)
parser.add_argument('cmp-file', nargs = '?')
parser.add_argument('-f', '--force-overwrite', action='store_true',
                    help='Force overwriting of existing BOM (assembly) '
                    'part even if the part appears to have been modified '
                    'manually.')
args = parser.parse_args()

output_filename = args.__dict__['output-file'][0]

xml = ET.parse(args.__dict__['input-file'][0])

schematic_name = 'unknown'
design = xml.find('design')
if design is not None:
    source = design.find('source')
    if source is not None:
        schematic_name = path.splitext(path.basename(source.text))[0]

assembly_name = 'bom:' + schematic_name
qs = Part.objects.filter(mfg=MANUFACTURER).filter(mfg_pn=assembly_name)
if qs.exists():
    assembly_part = qs[0]
    if assembly_part.last_bom_mod_type != Part.LAST_MOD_TYPE_TOOL \
       or assembly_part.last_bom_mod_name != MY_TOOL_NAME:
        print('%s: part %s %s was last modified by %s %s' %
              (MY_TOOL_NAME, MANUFACTURER, assembly_name,
               strchoice(Part.LAST_MOD_CHOICES,
                         assembly_part.last_bom_mod_type),
               assembly_part.last_bom_mod_name), file=sys.stderr)
        if args.force_overwrite:
            print('%s: overwriting existing part due to --force-overwrite' \
                  % MY_TOOL_NAME, file=sys.stderr)
        else:
            print('%s: refusing to overwrite part %s; '
                  'use --force-overwrite if desired' \
                  % (MY_TOOL_NAME, format_part_number(assembly_part.id)),
                  file=sys.stderr)
            sys.exit(1)
else:
    assembly_part = Part(descr='BOM for %s' % schematic_name,
                         mfg=MANUFACTURER, mfg_pn=assembly_name,
                         mounting=Part.MOUNTING_CHASSIS,
                         target_price=1000,
                         overage=1, spq=1, lead_time=4,
                         status=Part.STATUS_PREVIEW)

cmp_out = None
if args.__dict__['cmp-file'] is not None:
    cmp_out = open(args.__dict__['cmp-file'], 'w')
    print('Cmp-Mod V01 Created by make-bom', file=cmp_out)

bom = {}
for comp in xml.find('components'):
    part_id = None
    fields = comp.find('fields')
    if fields is not None:
        for field in fields:
            if field.attrib['name'] == 'EP':
                part_id = int(field.text)
    c = Component(part_id, refdes=comp.attrib.get('ref'),
                  value=comp.findtext('value', default='n/a'))
    if part_id is None:
        print('%s: warning: skipping refdes %s due to missing '
              'EPIC Part Number (EP field)' % (MY_TOOL_NAME, c.refdes),
              file=sys.stderr)
        continue
    else:
        try:
            c.part = Part.objects.get(pk=part_id)
            if c.value != c.part.val:
                print('%s: warning: %s has value %s but part %s has '
                      'value %s' % (MY_TOOL_NAME, c.refdes, c.value,
                                    format_part_number(part_id), c.part.val),
                      file=sys.stderr)
            c.footprint = c.part.footprint
            c.mfg = c.part.mfg
            c.mfg_pn = c.part.mfg_pn
        except ObjectDoesNotExist:
            print('%s: warning: part %s not found in database',
                  MY_TOOL_NAME, format_part_number(part_id), file=sys.stderr)
    if c.part_id not in bom:
        bom[c.part_id] = []
    bom[c.part_id].append(c)

    if cmp_out and c.footprint is not None:
        print('\nBeginCmp\nReference = %s;\nValeurCmp = %s;\n'
              'IdModule = %s;\nEndCmp' %
              (c.refdes, c.value, c.footprint), file=cmp_out)

if cmp_out:
    print('\nEndListe', file=cmp_out)
    cmp_out.close()
    cmp_out = None

bom_list = []
for part_id in bom:
    bom_list.append(bom[part_id])
bom_list.sort(key=lambda x: x[0].part_id)

out = open(output_filename, 'w')
print(('Qty,Value,Footprint,%s PN,Mfg,Mfg PN,Approved Substitutes,Refdes'
       % MANUFACTURER),
      file=out)
for components in bom_list:
    qty = len(components)
    refdes = ','.join(c.refdes for c in components)
    c = components[0]

    substitutes = ''
    if c.part:
        sep = ''
        for sub in c.part.equivalent_parts():
            if sub == c.part:
                continue
            substitutes += sep
            substitutes += '%s (%s %s)' % (format_part_number(sub.id),
                                           sub.mfg, sub.mfg_pn)
            sep = ', '

    print('%s,%s,%s,%s,%s,%s,%s,%s' \
          % (str(qty), str(c.value), str(format_part_number(part_id)),
             str(c.footprint),
             str(c.mfg), str(c.mfg_pn),
             str(quote(substitutes)),
             str(quote(refdes))), file=out)
save_assembly(assembly_part, bom_list)
