#!/usr/bin/env python
import sys

from gemini import GeminiQuery
from gemini import gemini_constants as const
from gemini import gemini_subjects as subjects


gq = GeminiQuery.GeminiQueryPostgres(database)
query = "SELECT variant_id, chrom, start, end, \
                    ref, alt, gene, impact, gts, gt_types, \
                    gt_ref_depths, gt_alt_depths \
         FROM variants"

families = subjects.get_families(database)

gq.run(query, gt_filter="(gt_types).(*).(==HOM_ALT).(any)")

for row in gq:
    print row

