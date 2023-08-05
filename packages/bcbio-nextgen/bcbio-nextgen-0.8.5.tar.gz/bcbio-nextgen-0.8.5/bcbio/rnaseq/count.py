"""
count number of reads mapping to features of transcripts

"""
import os
import sys
import itertools

# soft imports
try:
    import HTSeq
    import pandas as pd
    import gffutils
except ImportError:
    HTSeq, pd, gffutils = None, None, None

from bcbio.utils import file_exists
from bcbio.distributed.transaction import file_transaction
from bcbio.log import logger
from bcbio import bam
import bcbio.pipeline.datadict as dd


def _get_files(data):
    mapped = bam.mapped(data["work_bam"], data["config"])
    in_file = bam.sort(mapped, data["config"], order="queryname")
    gtf_file = dd.get_gtf_file(data)
    work_dir = dd.get_work_dir(data)
    out_dir = os.path.join(work_dir, "htseq-count")
    sample_name = dd.get_sample_name(data)
    out_file = os.path.join(out_dir, sample_name + ".counts")
    stats_file = os.path.join(out_dir, sample_name + ".stats")
    return in_file, gtf_file, out_file, stats_file


def invert_strand(iv):
    iv2 = iv.copy()
    if iv2.strand == "+":
        iv2.strand = "-"
    elif iv2.strand == "-":
        iv2.strand = "+"
    else:
        raise ValueError("Illegal strand")
    return iv2


class UnknownChrom(Exception):
    pass

def _get_stranded_flag(data):
    strand_flag = {"unstranded": "no",
                   "firststrand": "reverse",
                   "secondstrand": "yes"}
    stranded = dd.get_strandedness(data, "unstranded").lower()
    assert stranded in strand_flag, ("%s is not a valid strandedness value. "
                                     "Valid values are 'firststrand', 'secondstrand', "
                                     "and 'unstranded")
    return strand_flag[stranded]


def htseq_count(data):
    """ adapted from Simon Anders htseq-count.py script
    http://www-huber.embl.de/users/anders/HTSeq/doc/count.html
    """

    sam_filename, gff_filename, out_file, stats_file = _get_files(data)
    stranded = _get_stranded_flag(data["config"])
    overlap_mode = "union"
    feature_type = "exon"
    id_attribute = "gene_id"
    minaqual = 0

    if file_exists(out_file):
        return out_file

    logger.info("Counting reads mapping to exons in %s using %s as the "
                "annotation and strandedness as %s." %
                (os.path.basename(sam_filename), os.path.basename(gff_filename), dd.get_strandedness(data)))

    features = HTSeq.GenomicArrayOfSets("auto", stranded != "no")
    counts = {}

    # Try to open samfile to fail early in case it is not there
    open(sam_filename).close()

    gff = HTSeq.GFF_Reader(gff_filename)
    i = 0
    try:
        for f in gff:
            if f.type == feature_type:
                try:
                    feature_id = f.attr[id_attribute]
                except KeyError:
                    sys.exit("Feature %s does not contain a '%s' attribute" %
                             (f.name, id_attribute))
                if stranded != "no" and f.iv.strand == ".":
                    sys.exit("Feature %s at %s does not have strand "
                             "information but you are running htseq-count "
                             "in stranded mode. Use '--stranded=no'." %
                             (f.name, f.iv))
                features[f.iv] += feature_id
                counts[f.attr[id_attribute]] = 0
            i += 1
            if i % 100000 == 0:
                sys.stderr.write("%d GFF lines processed.\n" % i)
    except:
        sys.stderr.write("Error occured in %s.\n"
                         % gff.get_line_number_string())
        raise

    sys.stderr.write("%d GFF lines processed.\n" % i)

    if len(counts) == 0:
        sys.stderr.write("Warning: No features of type '%s' found.\n"
                         % feature_type)

    try:
        align_reader = htseq_reader(sam_filename)
        first_read = iter(align_reader).next()
        pe_mode = first_read.paired_end
    except:
        sys.stderr.write("Error occured when reading first line of sam "
                         "file.\n")
        raise

    try:
        if pe_mode:
            read_seq_pe_file = align_reader
            read_seq = HTSeq.pair_SAM_alignments(align_reader)
        empty = 0
        ambiguous = 0
        notaligned = 0
        lowqual = 0
        nonunique = 0
        i = 0
        for r in read_seq:
            i += 1
            if not pe_mode:
                if not r.aligned:
                    notaligned += 1
                    continue
                try:
                    if r.optional_field("NH") > 1:
                        nonunique += 1
                        continue
                except KeyError:
                    pass
                if r.aQual < minaqual:
                    lowqual += 1
                    continue
                if stranded != "reverse":
                    iv_seq = (co.ref_iv for co in r.cigar if co.type == "M"
                              and co.size > 0)
                else:
                    iv_seq = (invert_strand(co.ref_iv) for co in r.cigar if
                              co.type == "M" and co.size > 0)
            else:
                if r[0] is not None and r[0].aligned:
                    if stranded != "reverse":
                        iv_seq = (co.ref_iv for co in r[0].cigar if
                                  co.type == "M" and co.size > 0)
                    else:
                        iv_seq = (invert_strand(co.ref_iv) for co in r[0].cigar if
                                  co.type == "M" and co.size > 0)
                else:
                    iv_seq = tuple()
                if r[1] is not None and r[1].aligned:
                    if stranded != "reverse":
                        iv_seq = itertools.chain(iv_seq,
                                                 (invert_strand(co.ref_iv) for co
                                                  in r[1].cigar if co.type == "M"
                                                  and co.size > 0))
                    else:
                        iv_seq = itertools.chain(iv_seq,
                                                 (co.ref_iv for co in r[1].cigar
                                                  if co.type == "M" and co.size
                                                  > 0))
                else:
                    if (r[0] is None) or not (r[0].aligned):
                        notaligned += 1
                        continue
                try:
                    if (r[0] is not None and r[0].optional_field("NH") > 1) or \
                       (r[1] is not None and r[1].optional_field("NH") > 1):
                        nonunique += 1
                        continue
                except KeyError:
                    pass
                if (r[0] and r[0].aQual < minaqual) or (r[1] and
                                                        r[1].aQual < minaqual):
                    lowqual += 1
                    continue

            try:
                if overlap_mode == "union":
                    fs = set()
                    for iv in iv_seq:
                        if iv.chrom not in features.chrom_vectors:
                            raise UnknownChrom
                        for iv2, fs2 in features[iv].steps():
                            fs = fs.union(fs2)
                elif (overlap_mode == "intersection-strict" or
                      overlap_mode == "intersection-nonempty"):
                    fs = None
                    for iv in iv_seq:
                        if iv.chrom not in features.chrom_vectors:
                            raise UnknownChrom
                        for iv2, fs2 in features[iv].steps():
                            if (len(fs2) > 0 or overlap_mode == "intersection-strict"):
                                if fs is None:
                                    fs = fs2.copy()
                                else:
                                    fs = fs.intersection(fs2)
                else:
                    sys.exit("Illegal overlap mode.")
                if fs is None or len(fs) == 0:
                    empty += 1
                elif len(fs) > 1:
                    ambiguous += 1
                else:
                    counts[list(fs)[0]] += 1
            except UnknownChrom:
                if not pe_mode:
                    rr = r
                else:
                    rr = r[0] if r[0] is not None else r[1]
                empty += 1

            if i % 100000 == 0:
                sys.stderr.write("%d sam %s processed.\n" %
                                 (i, "lines " if not pe_mode else "line pairs"))

    except:
        if not pe_mode:
            sys.stderr.write("Error occured in %s.\n"
                             % read_seq.get_line_number_string())
        else:
            sys.stderr.write("Error occured in %s.\n"
                             % read_seq_pe_file.get_line_number_string())
        raise

    sys.stderr.write("%d sam %s processed.\n" %
                     (i, "lines " if not pe_mode else "line pairs"))

    with file_transaction(data, out_file) as tmp_out_file:
        with open(tmp_out_file, "w") as out_handle:
            on_feature = 0
            for fn in sorted(counts.keys()):
                on_feature += counts[fn]
                out_handle.write("%s\t%d\n" % (fn, counts[fn]))

    with file_transaction(data, stats_file) as tmp_stats_file:
        with open(tmp_stats_file, "w") as out_handle:
            out_handle.write("on_feature\t%d\n" % on_feature)
            out_handle.write("no_feature\t%d\n" % empty)
            out_handle.write("ambiguous\t%d\n" % ambiguous)
            out_handle.write("too_low_aQual\t%d\n" % lowqual)
            out_handle.write("not_aligned\t%d\n" % notaligned)
            out_handle.write("alignment_not_unique\t%d\n" % nonunique)

    return out_file

def combine_count_files(files, out_file=None, ext=".fpkm"):
    """
    combine a set of count files into a single combined file
    """
    assert all([file_exists(x) for x in files]), \
        "Some count files in %s do not exist." % files
    for f in files:
        assert file_exists(f), "%s does not exist or is empty." % f
    col_names = [os.path.basename(x.split(ext)[0]) for x in files]
    if not out_file:
        out_dir = os.path.join(os.path.dirname(files[0]))
        out_file = os.path.join(out_dir, "combined.counts")

    if file_exists(out_file):
        return out_file

    df = pd.io.parsers.read_table(f, sep="\t", index_col=0, header=None,
                                  names=[col_names[0]])
    for i, f in enumerate(files):
        if i == 0:
            df = pd.io.parsers.read_table(f, sep="\t", index_col=0, header=None,
                                          names=[col_names[0]])
        else:
            df = df.join(pd.io.parsers.read_table(f, sep="\t", index_col=0,
                                                  header=None,
                                                  names=[col_names[i]]))

    df.to_csv(out_file, sep="\t", index_label="id")
    return out_file

def annotate_combined_count_file(count_file, gtf_file, out_file=None):
    dbfn = gtf_file + ".db"
    if not file_exists(dbfn):
        return None

    if not gffutils:
        return None

    db = gffutils.FeatureDB(dbfn, keep_order=True)

    if not out_file:
        out_dir = os.path.dirname(count_file)
        out_file = os.path.join(out_dir, "annotated_combined.counts")

    # if the genes don't have a gene_id or gene_name set, bail out
    try:
        symbol_lookup = {f['gene_id'][0]: f['gene_name'][0] for f in
                         db.features_of_type('exon')}
    except KeyError:
        return None

    df = pd.io.parsers.read_table(count_file, sep="\t", index_col=0, header=0)

    df['symbol'] = df.apply(lambda x: symbol_lookup.get(x.name, ""), axis=1)
    df.to_csv(out_file, sep="\t", index_label="id")
    return out_file


def htseq_reader(align_file):
    """
    returns a read-by-read sequence reader for a BAM or SAM file
    """
    if bam.is_sam(align_file):
        read_seq = HTSeq.SAM_Reader(align_file)
    elif bam.is_bam(align_file):
        read_seq = HTSeq.BAM_Reader(align_file)
    else:
        logger.error("%s is not a SAM or BAM file" % (align_file))
        sys.exit(1)
    return read_seq
