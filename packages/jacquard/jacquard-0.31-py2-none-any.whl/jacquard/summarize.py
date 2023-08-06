"""Adds summary tags/fields to a merged VCF file.

Collaborates with two summary "callers" to add INFO and FORMAT tags to each
variant record based on the presence of previously translated tags.
"""
from __future__ import print_function, absolute_import
import jacquard.logger as logger
import jacquard.variant_callers.summarize_caller as summarize_caller
import jacquard.variant_callers.zscore_caller as zscore_caller
import jacquard.vcf as vcf
import os


def _write_metaheaders(caller,
                       vcf_reader,
                       file_writer,
                       execution_context=None,
                       new_meta_headers=None):

    new_headers = list(vcf_reader.metaheaders)

    if execution_context:
        new_headers.extend(execution_context)
        new_headers.extend(caller.get_metaheaders())
    if new_meta_headers:
        new_headers.append(new_meta_headers)

    new_headers.append(vcf_reader.column_header)
    file_writer.write("\n".join(new_headers) +"\n")

def _write_to_tmp_file(caller, vcf_reader, tmp_writer):
    vcf_reader.open()
    tmp_writer.open()

    try:
        _write_metaheaders(caller, vcf_reader, tmp_writer)
        logger.info("Adding summary tags for [{}]", vcf_reader.file_name)
        _add_tags(caller, vcf_reader, tmp_writer)

    finally:
        vcf_reader.close()
        tmp_writer.close()


def _write_zscores(caller,
                   metaheaders,
                   vcf_reader,
                   file_writer):

    try:
        file_writer.open()
        headers = list(metaheaders)
        headers.extend(vcf_reader.metaheaders)
        headers.extend(caller.metaheaders)
        headers.append(vcf_reader.column_header)
        file_writer.write("\n".join(headers) +"\n")

        vcf_reader.open()
        for vcf_record in vcf_reader.vcf_records():
            line = caller.add_tags(vcf_record)
            file_writer.write(line)
    finally:
        vcf_reader.close()
        file_writer.close()

def _add_tags(caller, vcf_reader, file_writer):
    for vcf_record in vcf_reader.vcf_records():
        caller.add_tags(vcf_record)
        file_writer.write(vcf_record.text())

def add_subparser(subparser):
    # pylint: disable=line-too-long
    parser = subparser.add_parser("summarize", help="Accepts a Jacquard-merged VCF file and creates a new file, adding summary fields.")
    parser.add_argument("input", help="Path to Jacquard-merged VCF (or any VCF with Jacquard tags; e.g. JQ_SOM_MT)")
    parser.add_argument("output", help="Path to output VCf")
    parser.add_argument("-v", "--verbose", action='store_true')
    parser.add_argument("--force", action='store_true', help="Overwrite contents of output directory")

def report_prediction(args):
    return set([os.path.basename(args.output)])

def get_required_input_output_types():
    return ("file", "file")

#TODO (cgates): Validate should actually validate
def validate_args(dummy):
    pass

def execute(args, execution_context):
    input_file = os.path.abspath(args.input)
    output = os.path.abspath(args.output)

    summary_caller = summarize_caller.SummarizeCaller()

    vcf_reader = vcf.VcfReader(vcf.FileReader(input_file))
    tmp_output_file = output + ".tmp"
    tmp_writer = vcf.FileWriter(tmp_output_file)

    _write_to_tmp_file(summary_caller, vcf_reader, tmp_writer)

    tmp_reader = vcf.VcfReader(vcf.FileReader(tmp_output_file))
    file_writer = vcf.FileWriter(output)

    logger.info("Calculating zscores")
    caller = zscore_caller.ZScoreCaller(tmp_reader)
    metaheaders = execution_context + summary_caller.get_metaheaders()
    _write_zscores(caller, metaheaders, tmp_reader, file_writer)

    os.remove(tmp_output_file)
