"""Perform validation of final calls against known reference materials.

Automates the process of checking pipeline results against known valid calls
to identify discordant variants. This provides a baseline for ensuring the
validity of pipeline updates and algorithm changes.
"""
import collections
import csv
import os

import yaml
import toolz as tz

from bcbio import broad, utils
from bcbio.bam import callable
from bcbio.distributed.transaction import file_transaction
from bcbio.pipeline import config_utils, shared
from bcbio.provenance import do
from bcbio.variation import validateplot, multi

# ## Individual sample comparisons

def _get_validate(data):
    """Retrieve items to validate, from single samples or from combined joint calls.
    """
    if data.get("vrn_file") and "validate" in data["config"]["algorithm"]:
        return data
    elif "group_orig" in data:
        for sub in multi.get_orig_items(data):
            if "validate" in sub["config"]["algorithm"]:
                sub_val = utils.deepish_copy(sub)
                sub_val["vrn_file"] = data["vrn_file"]
                return sub_val
    return None

def normalize_input_path(x, data):
    """Normalize path for input files, handling relative paths.
    Looks for non-absolute paths in local and fastq directories
    """
    if x is None:
        return None
    elif os.path.isabs(x):
        return os.path.normpath(x)
    else:
        for d in [data["dirs"].get("fastq"), data["dirs"].get("work")]:
            if d:
                cur_x = os.path.normpath(os.path.join(d, x))
                if os.path.exists(cur_x):
                    return cur_x
        raise IOError("Could not find validation file %s" % x)

def _gunzip(f, data):
    if f is None:
        return None
    elif f.endswith(".gz"):
        out_file = f.replace(".gz", "")
        if not utils.file_exists(out_file):
            with file_transaction(data, out_file) as tx_out_file:
                cmd = "gunzip -c {f} > {tx_out_file}"
                do.run(cmd.format(**locals()), "gunzip input file")
        return out_file
    else:
        return f

def _get_caller(data):
    callers = [tz.get_in(["config", "algorithm", "jointcaller"], data),
               tz.get_in(["config", "algorithm", "variantcaller"], data),
               "precalled"]
    return [c for c in callers if c][0]

def compare_to_rm(data):
    """Compare final variant calls against reference materials of known calls.
    """
    toval_data = _get_validate(data)
    if toval_data:
        if isinstance(toval_data["vrn_file"], (list, tuple)):
            vrn_file = [os.path.abspath(x) for x in toval_data["vrn_file"]]
        else:
            vrn_file = os.path.abspath(toval_data["vrn_file"])
        rm_file = normalize_input_path(toval_data["config"]["algorithm"]["validate"], toval_data)
        rm_interval_file = _gunzip(normalize_input_path(toval_data["config"]["algorithm"].get("validate_regions"),
                                                        toval_data),
                                   toval_data)
        rm_genome = toval_data["config"]["algorithm"].get("validate_genome_build")
        sample = toval_data["name"][-1].replace(" ", "_")
        caller = _get_caller(toval_data)
        base_dir = utils.safe_makedir(os.path.join(toval_data["dirs"]["work"], "validate", sample, caller))
        val_config_file = _create_validate_config_file(vrn_file, rm_file, rm_interval_file,
                                                       rm_genome, base_dir, toval_data)
        work_dir = os.path.join(base_dir, "work")
        out = {"summary": os.path.join(work_dir, "validate-summary.csv"),
               "grading": os.path.join(work_dir, "validate-grading.yaml"),
               "discordant": os.path.join(work_dir, "%s-eval-ref-discordance-annotate.vcf" % sample)}
        if not utils.file_exists(out["discordant"]) or not utils.file_exists(out["grading"]):
            bcbio_variation_comparison(val_config_file, base_dir, toval_data)
        out["concordant"] = filter(os.path.exists,
                                   [os.path.join(work_dir, "%s-%s-concordance.vcf" % (sample, x))
                                    for x in ["eval-ref", "ref-eval"]])[0]
        data["validate"] = out
    return [[data]]

def bcbio_variation_comparison(config_file, base_dir, data):
    """Run a variant comparison using the bcbio.variation toolkit, given an input configuration.
    """
    tmp_dir = utils.safe_makedir(os.path.join(base_dir, "tmp"))
    bv_jar = config_utils.get_jar("bcbio.variation",
                                  config_utils.get_program("bcbio_variation",
                                                           data["config"], "dir"))
    resources = config_utils.get_resources("bcbio_variation", data["config"])
    jvm_opts = resources.get("jvm_opts", ["-Xms750m", "-Xmx2g"])
    cmd = ["java"] + jvm_opts + broad.get_default_jvm_opts(tmp_dir) + \
          ["-jar", bv_jar, "variant-compare", config_file]
    do.run(cmd, "Comparing variant calls using bcbio.variation", data)

def _create_validate_config_file(vrn_file, rm_file, rm_interval_file, rm_genome,
                                 base_dir, data):
    config_dir = utils.safe_makedir(os.path.join(base_dir, "config"))
    config_file = os.path.join(config_dir, "validate.yaml")
    with open(config_file, "w") as out_handle:
        out = _create_validate_config(vrn_file, rm_file, rm_interval_file, rm_genome,
                                      base_dir, data)
        yaml.safe_dump(out, out_handle, default_flow_style=False, allow_unicode=False)
    return config_file

def _create_validate_config(vrn_file, rm_file, rm_interval_file, rm_genome,
                            base_dir, data):
    """Create a bcbio.variation configuration input for validation.
    """
    if rm_genome:
        rm_genome = utils.get_in(data, ("reference", "alt", rm_genome, "base"))
    if rm_genome and rm_genome != utils.get_in(data, ("reference", "fasta", "base")):
        eval_genome = utils.get_in(data, ("reference", "fasta", "base"))
    else:
        rm_genome = utils.get_in(data, ("reference", "fasta", "base"))
        eval_genome = None
    ref_call = {"file": str(rm_file), "name": "ref", "type": "grading-ref",
                "preclean": True, "prep": True, "remove-refcalls": True}
    a_intervals = get_analysis_intervals(data)
    if a_intervals:
        a_intervals = shared.remove_lcr_regions(a_intervals, [data])
    if rm_interval_file:
        ref_call["intervals"] = rm_interval_file
    eval_call = {"file": vrn_file, "name": "eval", "remove-refcalls": True}
    if eval_genome:
        eval_call["ref"] = eval_genome
        eval_call["preclean"] = True
        eval_call["prep"] = True
    if a_intervals and eval_genome:
        eval_call["intervals"] = os.path.abspath(a_intervals)
    exp = {"sample": data["name"][-1],
           "ref": rm_genome,
           "approach": "grade",
           "calls": [ref_call, eval_call]}
    if a_intervals and not eval_genome:
        exp["intervals"] = os.path.abspath(a_intervals)
    if data.get("align_bam") and not eval_genome:
        exp["align"] = data["align_bam"]
    elif data.get("work_bam") and not eval_genome:
        exp["align"] = data["work_bam"]
    return {"dir": {"base": base_dir, "out": "work", "prep": "work/prep"},
            "experiments": [exp]}

def get_analysis_intervals(data):
    """Retrieve analysis regions for the current variant calling pipeline.
    """
    if data.get("ensemble_bed"):
        return data["ensemble_bed"]
    elif data.get("align_bam"):
        return callable.sample_callable_bed(data["align_bam"],
                                            utils.get_in(data, ("reference", "fasta", "base")), data["config"])
    elif data.get("work_bam"):
        return callable.sample_callable_bed(data["work_bam"],
                                            utils.get_in(data, ("reference", "fasta", "base")), data["config"])
    elif data.get("work_bam_callable"):
        return callable.sample_callable_bed(data["work_bam_callable"],
                                            utils.get_in(data, ("reference", "fasta", "base")), data["config"])
    else:
        for key in ["callable_regions", "variant_regions"]:
            intervals = data["config"]["algorithm"].get(key)
            if intervals:
                return intervals

# ## Summarize comparisons

def _flatten_grading(stats):
    vtypes = ["snp", "indel"]
    cat = "concordant"
    for vtype in vtypes:
        yield vtype, cat, stats[cat][cat].get(vtype, 0)
    for vtype in vtypes:
        for vclass, vitems in sorted(stats["discordant"].get(vtype, {}).iteritems()):
            for vreason, val in sorted(vitems.iteritems()):
                yield vtype, "discordant-%s-%s" % (vclass, vreason), val
            yield vtype, "discordant-%s-total" % vclass, sum(vitems.itervalues())

def _has_grading_info(samples):
    for data in (x[0] for x in samples):
        for variant in data.get("variants", []):
            if variant.get("validate"):
                return True
    return False

def _group_validate_samples(samples):
    extras = []
    validated = collections.defaultdict(list)
    for data in (x[0] for x in samples):
        is_v = False
        for variant in data.get("variants", []):
            if variant.get("validate"):
                is_v = True
        if is_v:
            vname = tz.get_in(["metadata", "batch"], data, data["description"])
            if isinstance(vname, (list, tuple)):
                vname = vname[0]
            validated[vname].append(data)
        else:
            extras.append([data])
    return validated, extras

def summarize_grading(samples):
    """Provide summaries of grading results across all samples.
    """
    if not _has_grading_info(samples):
        return samples
    validate_dir = utils.safe_makedir(os.path.join(samples[0][0]["dirs"]["work"], "validate"))
    header = ["sample", "caller", "variant.type", "category", "value"]
    validated, out = _group_validate_samples(samples)
    for vname, vitems in validated.iteritems():
        out_csv = os.path.join(validate_dir, "grading-summary-%s.csv" % vname)
        with open(out_csv, "w") as out_handle:
            writer = csv.writer(out_handle)
            writer.writerow(header)
            plot_data = []
            for data in vitems:
                for variant in data.get("variants", []):
                    if variant.get("validate"):
                        variant["validate"]["grading_summary"] = out_csv
                        with open(variant["validate"]["grading"]) as in_handle:
                            grade_stats = yaml.load(in_handle)
                        for sample_stats in grade_stats:
                            sample = sample_stats["sample"]
                            for vtype, cat, val in _flatten_grading(sample_stats):
                                row = [sample, variant.get("variantcaller", ""),
                                       vtype, cat, val]
                                writer.writerow(row)
                                plot_data.append(row)
            plots = (validateplot.create(plot_data, header, 0, data["config"],
                                         os.path.splitext(out_csv)[0])
                     if plot_data else None)
            for data in vitems:
                for variant in data.get("variants", []):
                    if variant.get("validate"):
                        variant["validate"]["grading_plots"] = plots
                out.append([data])
    return out
