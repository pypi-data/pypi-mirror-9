"""Next gen sequence alignments with Bowtie2.

http://bowtie-bio.sourceforge.net/bowtie2/index.shtml
"""
import os
from itertools import ifilter
import pysam

from bcbio.pipeline import config_utils
from bcbio.utils import file_exists
from bcbio.distributed.transaction import file_transaction
from bcbio.provenance import do
from bcbio import bam
from bcbio.pipeline import datadict as dd
from bcbio.rnaseq import gtf

def _bowtie2_args_from_config(config):
    """Configurable high level options for bowtie2.
    """
    qual_format = config["algorithm"].get("quality_format", "")
    if qual_format.lower() == "illumina":
        qual_flags = ["--phred64-quals"]
    else:
        qual_flags = []
    num_cores = config["algorithm"].get("num_cores", 1)
    core_flags = ["-p", str(num_cores)] if num_cores > 1 else []
    return core_flags + qual_flags

def align(fastq_file, pair_file, ref_file, names, align_dir, data,
          extra_args=None):
    """Alignment with bowtie2.
    """
    config = data["config"]
    analysis_config = ANALYSIS.get(data["analysis"])
    assert analysis_config, "Analysis %s is not supported by bowtie2" % (data["analysis"])
    out_file = os.path.join(align_dir, "%s.sam" % names["lane"])
    if not file_exists(out_file):
        with file_transaction(data, out_file) as tx_out_file:
            cl = [config_utils.get_program("bowtie2", config)]
            cl += _bowtie2_args_from_config(config)
            cl += extra_args if extra_args is not None else []
            cl += ["-q",
                   "-x", ref_file]
            cl += analysis_config.get("params", [])
            if pair_file:
                cl += ["-1", fastq_file, "-2", pair_file]
            else:
                cl += ["-U", fastq_file]
            cl += ["-S", tx_out_file]
            if names and "rg" in names:
                cl += ["--rg-id", names["rg"]]
                for key, tag in [("sample", "SM"), ("pl", "PL"), ("pu", "PU")]:
                    if key in names:
                        cl += ["--rg", "%s:%s" % (tag, names[key])]
            cl = [str(i) for i in cl]
            do.run(cl, "Aligning %s and %s with Bowtie2." % (fastq_file, pair_file),
                   None)
    return out_file

# Optional galaxy location file. Falls back on remap_index_fn if not found
galaxy_location_file = "bowtie2_indices.loc"

def remap_index_fn(ref_file):
    """Map sequence references to equivalent bowtie2 indexes.
    """
    return os.path.splitext(ref_file)[0].replace("/seq/", "/bowtie2/")


def filter_multimappers(align_file):
    """
    It does not seem like bowtie2 has a corollary to the -m 1 flag in bowtie,
    there are some options that are close but don't do the same thing. Bowtie2
    sets the XS flag for reads mapping in more than one place, so we can just
    filter on that. This will not work for other aligners.
    """
    type_flag = "b" if bam.is_bam(align_file) else ""
    base, ext = os.path.splitext(align_file)
    align_handle = pysam.Samfile(align_file, "r" + type_flag)
    tmp_out_file = os.path.splitext(align_file)[0] + ".tmp"
    def keep_fn(read):
        return _is_properly_mapped(read) and _is_unique(read)
    keep = ifilter(keep_fn, align_handle)
    with pysam.Samfile(tmp_out_file, "w" + type_flag, template=align_handle) as out_handle:
        for read in keep:
            out_handle.write(read)
    align_handle.close()
    out_handle.close()
    os.rename(tmp_out_file, align_file)
    return align_file

def _is_properly_mapped(read):
    if read.is_paired and not read.is_proper_pair:
        return False
    if read.is_unmapped:
        return False
    return True

def _is_unique(read):
    tags = [x[0] for x in read.tags]
    return "XS" not in tags


ANALYSIS = {"chip-seq": {"params": ["-X", 2000]},
            "variant2": {"params": ["-X", 2000]},
            "Standard": {"params": ["-X", 2000]},
            "RNA-seq": {"params": ["--sensitive", "-X", 2000]}}

def index_transcriptome(gtf_file, ref_file, data):
    """
    use a GTF file and a reference FASTA file to index the transcriptome
    """
    gtf_fasta = gtf.gtf_to_fasta(gtf_file, ref_file)
    bowtie2_index = os.path.splitext(gtf_fasta)[0]
    bowtie2_build = config_utils.get_program("bowtie2", data["config"]) + "-build"
    cmd = "{bowtie2_build} --offrate 1 {gtf_fasta} {bowtie2_index}".format(**locals())
    message = "Creating transcriptome index of %s with bowtie2." % (gtf_fasta)
    do.run(cmd, message)
    return bowtie2_index


def align_transcriptome(fastq_file, pair_file, ref_file, data):
    """
    bowtie2 with settings for aligning to the transcriptome for eXpress/RSEM/etc
    """
    work_bam = dd.get_work_bam(data)
    base, ext = os.path.splitext(work_bam)
    out_file = base + ".transcriptome" + ext
    if file_exists(out_file):
        data = dd.set_transcriptome_bam(data, out_file)
        return data
    bowtie2 = config_utils.get_program("bowtie2", data["config"])
    gtf_file = dd.get_gtf_file(data)
    gtf_index = index_transcriptome(gtf_file, ref_file, data)
    num_cores = data["config"]["algorithm"].get("num_cores", 1)
    pair_cmd = "-2 %s " % pair_file if pair_file else ""
    cmd = ("{bowtie2} -p {num_cores} -a -X 600 --rdg 6,5 --rfg 6,5 --score-min L,-.6,-.4 --no-discordant --no-mixed -x {gtf_index} -1 {fastq_file} {pair_cmd} | samtools view -hbS - > {tx_out_file}")
    with file_transaction(out_file) as tx_out_file:
        message = "Aligning %s and %s to the transcriptome." % (fastq_file, pair_file)
        do.run(cmd.format(**locals()), message)
    data = dd.set_transcriptome_bam(data, out_file)
    return data
