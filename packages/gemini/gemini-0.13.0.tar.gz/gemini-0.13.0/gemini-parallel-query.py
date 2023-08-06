"""
This is a simple script to parallelize gemini queries.
Users can have a long query like:

     gemini query "select chrom, start, end, (gts).(*) from variants" \
            --gt-filter "(gt_types).(phenotype == 1).(==HOM_REF).(all) \
            and ((gt_types).(phenotype==2).(==HET).(any) or (gt_types).(phenotype==2).(==HOM_ALT).(any)) \
         and (gt_ref_depths).(phenotype==1).(>=20).(any) and (gt_alt_depths).(phenotype==2).(>=20).(any)" $DB

and replace "gemini query" with "python gemini-parallel-query.py" to get the
same result sooner.

if --cores is not specified, it will use the number of availabel CPU's on the
current machine.

For this script, the database argument must be specified last.

For most intensive queries (those involving gt_* fields), this will result in
a speedup that is linear with the number of CPU's available.
"""
 
import sys
import subprocess
import multiprocessing
import atexit
import tempfile
import os
 
args = ["gemini", "query"] + sys.argv[1:]
 
query = args[args.index("-q") + 1]
if "--cores" in args:
    cores_i = args.index("--cores")
    cores = int(args.pop(cores_i + 1))
    args.pop(cores_i)
else:
    cores = multiprocessing.cpu_count()
 
db = args[-1]
assert not db.startswith("--")
 
if "where" in query.lower():
    query += " and variant_id >= {vmin}"
else:
    query += " where variant_id >= {vmin}"
 
query += " and variant_id < {vmax}"
 
rows = int(subprocess.check_output(['gemini', 'query', '-q',
                                  "select count(*) from variants", db]).strip())
 
# now split into chunks of even numbers of rows.
sizes = range(0, rows + 1, rows / cores )
 
chunks = []
for vmin, vmax in zip(sizes, sizes[1:]):
    chunks.append([vmin, vmax])
chunks[-1][1] = rows + 1
 
 
procs, tmps = [], []
for i, (vmin, vmax) in enumerate(chunks):
    args[args.index("-q") + 1] = '%s' % query.format(vmin=vmin, vmax=vmax)
    #print " ".join(args)
    tmps.append(open(tempfile.mktemp(suffix=str(i)), "w"))
    procs.append(subprocess.Popen(args, stderr=sys.stderr, stdout=tmps[-1], bufsize=-1))
    atexit.register(os.unlink, tmps[-1].name)
 
 
# keep track and only print header for the first chunk.
has_header = "--header" in args
for i, p in enumerate(procs):
    p.wait()
    tmps[i].close()
    for j, line in enumerate(open(tmps[i].name)):
        if has_header and j == 0 and i != 0: continue
        print line,

