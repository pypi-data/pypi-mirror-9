import os
from bcbio.rnaseq import (featureCounts, cufflinks, oncofuse, count, dexseq,
                          express, variation, gtf)
from bcbio.ngsalign import bwa, bowtie2
import bcbio.pipeline.datadict as dd
from bcbio.utils import filter_missing
from bcbio.log import logger

def rnaseq_variant_calling(samples, run_parallel):
    """
    run RNA-seq variant calling using GATK
    """
    samples = run_parallel("run_rnaseq_variant_calling", samples)
    samples = run_parallel("run_rnaseq_joint_genotyping", [samples])
    return samples

def run_rnaseq_variant_calling(data):
    variantcaller = dd.get_variantcaller(data)
    if variantcaller and "gatk" in variantcaller:
        data = variation.rnaseq_gatk_variant_calling(data)
    return [[data]]

def run_rnaseq_joint_genotyping(*samples):
    data = samples[0][0]
    variantcaller = dd.get_variantcaller(data)
    ref_file = dd.get_ref_file(data)
    out_file = os.path.join(dd.get_work_dir(data, "."), "variation", "combined.vcf")
    if variantcaller and "gatk" in variantcaller:
        vrn_files = [dd.get_vrn_file(d) for d in dd.sample_data_iterator(samples)]
        out_file = variation.gatk_joint_calling(data, vrn_files, ref_file, out_file)
        updated_samples = []
        for data in dd.sample_data_iterator(samples):
            data = dd.set_square_vcf(data, out_file)
            updated_samples.append([data])
        return updated_samples
    return samples

def quantitate_expression_parallel(samples, run_parallel):
    """
    quantitate expression, all programs run here should be multithreaded to
    take advantage of the threaded run_parallel environment
    """
    samples = run_parallel("generate_transcript_counts", samples)
    samples = run_parallel("run_cufflinks", samples)
    return samples

def quantitate_expression_noparallel(samples, run_parallel):
    """
    run transcript quantitation for algorithms that don't run in parallel
    """
    samples = run_parallel("run_express", samples)
    samples = run_parallel("run_dexseq", samples)
    return samples

def generate_transcript_counts(data):
    """Generate counts per transcript and per exon from an alignment"""
    data["count_file"] = featureCounts.count(data)
    if dd.get_fusion_mode(data, False):
        oncofuse_file = oncofuse.run(data)
        if oncofuse_file:
            data = dd.set_oncofuse_file(data, oncofuse_file)
    # if RSEM set to run, but the aligner didn't create the transcriptome BAM
    # file, make one with bwa
    if dd.get_rsem(data) and not dd.get_transcriptome_bam(data):
        file1, file2 = dd.get_input_sequence_files(data)
        ref_file = dd.get_ref_file(data)
        logger.info("RSEM was flagged to run, but the transcriptome BAM file "
                    "was not found. Aligning to the transcriptome with bowtie2.")
        data = bowtie2.align_transcriptome(file1, file2, ref_file, data)
    return [[data]]

def run_dexseq(data):
    """Quantitate exon-level counts with DEXSeq"""
    if dd.get_dexseq_gff(data, None):
        data = dexseq.bcbio_run(data)
    return [[data]]

def run_express(data):
    """Quantitative isoform expression by eXpress"""
    data = express.run(data)
    return [[data]]

def combine_express(samples, combined):
    """Combine tpm, effective counts and fpkm from express results"""
    to_combine = [dd.get_express_counts(x) for x in
                  dd.sample_data_iterator(samples) if dd.get_express_counts(x)]
    gtf_file = dd.get_gtf_file(samples[0][0])
    isoform_to_gene_file = os.path.join(os.path.dirname(combined), "isoform_to_gene.txt")
    isoform_to_gene_file = express.isoform_to_gene_name(gtf_file, isoform_to_gene_file)
    if len(to_combine) > 0:
        eff_counts_combined_file = os.path.splitext(combined)[0] + ".isoform.express_counts"
        eff_counts_combined = count.combine_count_files(to_combine, eff_counts_combined_file)
        to_combine = [dd.get_express_tpm(x) for x in
                      dd.sample_data_iterator(samples) if dd.get_express_tpm(x)]
        tpm_counts_combined_file = os.path.splitext(combined)[0] + ".isoform.express_tpm"
        tpm_counts_combined = count.combine_count_files(to_combine, tpm_counts_combined_file)
        to_combine = [dd.get_express_fpkm(x) for x in dd.sample_data_iterator(samples)
                      if dd.get_express_fpkm(x)]
        fpkm_counts_combined_file = os.path.splitext(combined)[0] + ".isoform.express_fpkm"
        fpkm_counts_combined = count.combine_count_files(to_combine, fpkm_counts_combined_file)
        return {'counts': eff_counts_combined, 'tpm': tpm_counts_combined,
                'fpkm': fpkm_counts_combined, 'isoform_to_gene': isoform_to_gene_file}
    return {}

def run_cufflinks(data):
    """Quantitate transcript expression with Cufflinks"""
    work_bam = dd.get_work_bam(data)
    ref_file = dd.get_sam_ref(data)
    out_dir, fpkm_file, fpkm_isoform_file = cufflinks.run(work_bam, ref_file, data)
    data = dd.set_cufflinks_dir(data, out_dir)
    data = dd.set_fpkm(data, fpkm_file)
    data = dd.set_fpkm_isoform(data, fpkm_isoform_file)
    return [[data]]

def cufflinks_assemble(data):
    bam_file = dd.get_work_bam(data)
    ref_file = dd.get_sam_ref(data)
    out_dir = os.path.join(dd.get_work_dir(data), "assembly")
    num_cores = dd.get_num_cores(data)
    assembled_gtf = cufflinks.assemble(bam_file, ref_file, num_cores, out_dir, data)
    data = dd.set_assembled_gtf(data, assembled_gtf)
    return [[data]]

def cufflinks_merge(*samples):
    to_merge = filter_missing([dd.get_assembled_gtf(data) for data in
                            dd.sample_data_iterator(samples)])
    data = samples[0][0]
    bam_file = dd.get_work_bam(data)
    ref_file = dd.get_sam_ref(data)
    gtf_file = dd.get_gtf_file(data)
    out_dir = os.path.join(dd.get_work_dir(data), "assembly")
    num_cores = dd.get_num_cores(data)
    merged_gtf = cufflinks.merge(to_merge, ref_file, gtf_file, num_cores, samples[0][0])
    updated_samples = []
    for data in dd.sample_data_iterator(samples):
        data = dd.set_assembled_gtf(data, merged_gtf)
        updated_samples.append([data])
    return updated_samples

def assemble_transcripts(run_parallel, samples):
    """
    assembly strategy rationale implemented as suggested in
    http://www.nature.com/nprot/journal/v7/n3/full/nprot.2012.016.html

    run Cufflinks in without a reference GTF for each individual sample
    merge the assemblies with Cuffmerge using a reference GTF
    """
    if dd.get_assemble_transcripts(samples[0][0]):
        samples = run_parallel("cufflinks_assemble", samples)
        samples = run_parallel("cufflinks_merge", [samples])
    return samples

def combine_files(samples):
    """
    after quantitation, combine the counts/FPKM/TPM/etc into a single table with
    all samples
    """
    gtf_file = dd.get_gtf_file(samples[0][0], None)
    # combine featureCount files
    count_files = filter_missing([dd.get_count_file(x[0]) for x in samples])
    combined = count.combine_count_files(count_files)
    annotated = count.annotate_combined_count_file(combined, gtf_file)

    # combine eXpress files
    express_counts_combined = combine_express(samples, combined)

    # combine Cufflinks files
    fpkm_combined_file = os.path.splitext(combined)[0] + ".fpkm"
    fpkm_files = filter_missing([dd.get_fpkm(x[0]) for x in samples])
    fpkm_combined = count.combine_count_files(fpkm_files, fpkm_combined_file)
    fpkm_isoform_combined_file = os.path.splitext(combined)[0] + ".isoform.fpkm"
    isoform_files = filter_missing([dd.get_fpkm_isoform(x[0]) for x in samples])
    fpkm_isoform_combined = count.combine_count_files(isoform_files,
                                                      fpkm_isoform_combined_file,
                                                      ".isoform.fpkm")

    # combine DEXseq files
    dexseq_combined_file = os.path.splitext(combined)[0] + ".dexseq"
    to_combine_dexseq = filter_missing([dd.get_dexseq_counts(data[0]) for data in samples])
    if to_combine_dexseq:
        dexseq_combined = count.combine_count_files(to_combine_dexseq,
                                                    dexseq_combined_file, ".dexseq")
    else:
        dexseq_combined = None
    updated_samples = []
    for data in dd.sample_data_iterator(samples):
        data = dd.set_combined_counts(data, combined)
        if annotated:
            data = dd.set_annotated_combined_counts(data, annotated)
        if fpkm_combined:
            data = dd.set_combined_fpkm(data, fpkm_combined)
        if fpkm_isoform_combined:
            data = dd.set_combined_fpkm_isoform(data, fpkm_combined)
        if express_counts_combined:
            data = dd.set_express_counts(data, express_counts_combined['counts'])
            data = dd.set_express_tpm(data, express_counts_combined['tpm'])
            data = dd.set_express_fpkm(data, express_counts_combined['fpkm'])
            data = dd.set_isoform_to_gene(data, express_counts_combined['isoform_to_gene'])
        if dexseq_combined:
            data = dd.set_dexseq_counts(data, dexseq_combined_file)
        updated_samples.append([data])
    return updated_samples
