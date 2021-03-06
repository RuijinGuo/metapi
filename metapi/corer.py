#!/usr/bin/env python

import argparse
import os
import sys
import subprocess
import textwrap
import metapi


WORKFLOWS_MAG = [
    "simulate_all",
    "prepare_reads_all",
    "raw_fastqc_all",
    "raw_report_all",
    "raw_all",
    "trimming_oas1_all",
    "trimming_sickle_all",
    "trimming_fastp_all",
    "trimming_report_all",
    "trimming_all",
    "rmhost_bwa_all",
    "rmhost_bowtie2_all",
    "rmhost_report_all",
    "rmhost_all",
    "qcreport_all",
    "assebmly_megahit_all",
    "assembly_idba_ud_all",
    "assembly_metaspades_all",
    "assembly_spades_all",
    "assembly_plass_all",
    "assembly_metaquast_all",
    "assembly_report_all",
    "assembly_all",
    "coassembly_megahit_all",
    "coassembly_all",
    "alignment_base_depth_all",
    "alignment_all",
    "binning_metabat2_coverage_all",
    "binning_metabat2_all",
    "binning_maxbin2_all",
    "binning_concoct_all",
    "binning_dastools_all",
    "binning_report_all",
    "binning_all",
    "cobinning_all",
    "predict_scaftigs_gene_prodigal_all",
    "predict_scaftigs_gene_prokka_all",
    "predict_bins_gene_prodigal_all",
    "predict_bins_gene_prokka_all",
    "predict_scafitgs_gene_all",
    "predict_bins_gene_all",
    "predict_all",
    "checkm_link_bins",
    "checkm_all",
    "dereplicate_mags_drep_all",
    "dereplicate_mags_all",
    "classify_short_reads_kraken2_all",
    "classify_hmq_bins_gtdbtk_all",
    "classify_all",
    "profiling_metaphlan2_all",
    "profiling_metaphlan3_all",
    "profiling_jgi_all",
    "profiling_bracken_all",
    "profiling_humann2_all",
    "profiling_all",
    "upload_sequencing_all",
    "upload_assembly_all",
    "upload_all",
    "all",
]

WORKFLOWS_GENE = [
    "simulate_all",
    "prepare_reads_all",
    "raw_fastqc_all",
    "raw_report_all",
    "raw_all",
    "trimming_oas1_all",
    "trimming_sickle_all",
    "trimming_fastp_all",
    "trimming_report_all",
    "trimming_all",
    "rmhost_bwa_all",
    "rmhost_bowtie2_all",
    "rmhost_report_all",
    "rmhost_all",
    "qcreport_all",
    "assebmly_megahit_all",
    "assembly_idba_ud_all",
    "assembly_metaspades_all",
    "assembly_spades_all",
    "assembly_plass_all",
    "assembly_metaquast_all",
    "assembly_report_all",
    "assembly_all",
    "coassembly_megahit_all",
    "coassembly_all",
    "predict_scaftigs_gene_prodigal_all",
    "predict_scaftigs_gene_prokka_all",
    "predict_scafitgs_gene_all",
    "predict_all",
    "dereplicate_gene_cdhit_all",
    "dereplicate_gene_all",
    "upload_sequencing_all",
    "upload_assembly_all",
    "upload_all",
    "all",
]


def run_snakemake(args, snakefile, workflow):
    config_file = os.path.join(args.workdir, "config.yaml")
    conf = metapi.parse_yaml(config_file)

    if not os.path.exists(conf["params"]["samples"]):
        print("Please specific samples list on init step or change config.yaml manualy")
        sys.exit(1)

    cmd = [
        "snakemake",
        "--snakefile",
        snakefile,
        "--configfile",
        args.config,
        "--cores",
        str(args.cores),
    ]

    if args.conda_create_envs_only:
        cmd += ["--use-conda", "--conda-create-envs-only"]
    else:
        cmd += [
            "--rerun-incomplete",
            "--keep-going",
            "--printshellcmds",
            "--reason",
            "--until",
            args.task,
        ]

        if args.use_conda:
            cmd += ["--use-conda"]

        if args.list:
            cmd += ["--list"]
        elif args.run:
            cmd += [""]
        elif args.debug:
            cmd += ["--debug-dag", "--dry-run"]
        elif args.dry_run:
            cmd += ["--dry-run"]
        elif args.qsub:
            cmd += [
                "--cluster-config",
                conf["clusterfile"],
                "--jobs",
                str(args.jobs),
                "--latency-wait",
                str(args.wait),
                '--cluster "qsub -S /bin/bash -cwd \
                -q {cluster.queue} -P {cluster.project} \
                -l vf={cluster.mem},p={cluster.cores} \
                -binding linear:{cluster.cores} \
                -o {cluster.output} -e {cluster.error}"',
            ]

    if not args.snake is None:
        cmd += ["--" + args.snake]

    cmd_str = " ".join(cmd).strip()
    print("Running metapi %s:\n%s" % (workflow, cmd_str))

    env = os.environ.copy()
    proc = subprocess.Popen(
        cmd_str, shell=True, stdout=sys.stdout, stderr=sys.stderr, env=env,
    )
    proc.communicate()


def init(args):
    if args.workdir:
        project = metapi.metaconfig(args.workdir)
        print(project.__str__())
        project.create_dirs()
        conf, cluster = project.get_config()

        conf["envs"]["bioenv3.7"] = os.path.join(
            os.path.realpath(args.workdir), "envs/bioenv3.7.yaml"
        )
        conf["envs"]["bioenv3.6"] = os.path.join(
            os.path.realpath(args.workdir), "envs/bioenv3.6.yaml"
        )
        conf["envs"]["bioenv2"] = os.path.join(
            os.path.realpath(args.workdir), "envs/bioenv2.yaml"
        )

        if args.begin:
            conf["params"]["begin"] = args.begin
            if args.begin == "simulate":
                conf["params"]["simulate"]["do"] = True
            elif args.begin == "trimming":
                conf["params"]["simulate"]["do"] = False
            elif args.begin == "rmhost":
                conf["params"]["simulate"]["do"] = False
                conf["params"]["trimming"]["oas1"]["do"] = False
                conf["params"]["trimming"]["sickle"]["do"] = False
                conf["params"]["trimming"]["fastp"]["do"] = False
            elif args.begin == "assembly":
                conf["params"]["simulate"]["do"] = False
                conf["params"]["trimming"]["oas1"]["do"] = False
                conf["params"]["trimming"]["sickle"]["do"] = False
                conf["params"]["trimming"]["fastp"]["do"] = False
                conf["params"]["rmhost"]["bwa"]["do"] = False
                conf["params"]["rmhost"]["bowtie2"]["do"] = False

        if args.samples:
            conf["params"]["samples"] = args.samples

        metapi.update_config(
            project.config_file, project.new_config_file, conf, remove=False
        )
        metapi.update_config(
            project.cluster_file, project.new_cluster_file, cluster, remove=False
        )
    else:
        print("Please supply a workdir!")
        sys.exit(-1)


def mag_wf(args):
    snakefile = os.path.join(os.path.dirname(__file__), "snakefiles/mag_wf.smk")
    run_snakemake(args, snakefile, "mag_wf")


def gene_wf(args):
    snakefile = os.path.join(os.path.dirname(__file__), "snakefiles/gene_wf.smk")
    run_snakemake(args, snakefile, "gene_wf")


def main():
    banner = """

  .___  ___.  _______ .___________.    ___      .______    __
  |   \/   | |   ____||           |   /   \     |   _  \  |  |
  |  \  /  | |  |__   `---|  |----`  /  ^  \    |  |_)  | |  |
  |  |\/|  | |   __|      |  |      /  /_\  \   |   ___/  |  |
  |  |  |  | |  |____     |  |     /  _____  \  |  |      |  |
  |__|  |__| |_______|    |__|    /__/     \__\ | _|      |__|

            Omics for All, Open Source for All

 A general metagenomics data mining system focus on robust microbiome research

"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(banner),
        prog="metapi",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print software version and exit",
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-d",
        "--workdir",
        metavar="WORKDIR",
        type=str,
        default="./",
        help="project workdir, default: ./",
    )

    run_parser = argparse.ArgumentParser(add_help=False)
    run_parser.add_argument(
        "--config",
        type=str,
        default="./config.yaml",
        help="config.yaml, default: ./config.yaml",
    )
    run_parser.add_argument(
        "--cores", type=int, default=8, help="CPU cores, default: 8"
    )
    run_parser.add_argument(
        "--jobs", type=int, default=80, help="qsub job numbers, default: 80"
    )
    run_parser.add_argument(
        "--list", default=False, action="store_true", help="list pipeline rules",
    )
    run_parser.add_argument(
        "--run", default=False, action="store_true", help="run pipeline",
    )
    run_parser.add_argument(
        "--debug", default=False, action="store_true", help="debug pipeline",
    )
    run_parser.add_argument(
        "--dry_run", default=False, action="store_true", help="dry run pipeline",
    )
    run_parser.add_argument(
        "--qsub", default=False, action="store_true", help="qsub pipeline",
    )
    run_parser.add_argument(
        "--wait", type=int, default=60, help="wait given seconds, default: 60"
    )
    run_parser.add_argument(
        "--use_conda", default=False, action="store_true", help="use conda environment"
    )
    run_parser.add_argument(
        "--conda_create_envs_only",
        default=False,
        action="store_true",
        help="conda create environments only",
    )
    run_parser.add_argument(
        "--snake",
        metavar="SNAKEMAKEARGS",
        nargs="?",
        type=str,
        default=None,
        help="other snakemake command options(sankemake -h), if want --touch, just --snake touch",
    )

    subparsers = parser.add_subparsers(title="available subcommands", metavar="")
    parser_init = subparsers.add_parser(
        "init",
        formatter_class=metapi.custom_help_formatter,
        parents=[common_parser],
        prog="metapi init",
        help="init project",
    )
    parser_mag_wf = subparsers.add_parser(
        "mag_wf",
        formatter_class=metapi.custom_help_formatter,
        parents=[common_parser, run_parser],
        prog="metapi mag_wf",
        help="metagenome-assembly-genome pipeline",
    )
    parser_gene_wf = subparsers.add_parser(
        "gene_wf",
        formatter_class=metapi.custom_help_formatter,
        parents=[common_parser, run_parser],
        prog="metapi gene_wf",
        help="metagenome-assembly-gene pipeline",
    )

    parser_init.add_argument(
        "-s",
        "--samples",
        type=str,
        default=None,
        help="""desired input:
samples list, tsv format required.

if begin from trimming, rmhost, or assembly:
    if it is fastq:
        the header is: [id, fq1, fq2]
    if it is sra:
        the header is: [id, sra]

if begin from simulate:
        the header is: [id, genome, abundance, reads_num, model]

""",
    )
    parser_init.add_argument(
        "-b",
        "--begin",
        type=str,
        default="trimming",
        choices=["simulate", "trimming", "rmhost", "assembly"],
        help="pipeline starting point",
    )
    parser_init.set_defaults(func=init)

    parser_mag_wf.add_argument(
        "task",
        metavar="TASK",
        nargs="?",
        type=str,
        default="all",
        choices=WORKFLOWS_MAG,
        help="pipeline end point. Allowed values are " + ", ".join(WORKFLOWS_MAG),
    )
    parser_mag_wf.set_defaults(func=mag_wf)

    parser_gene_wf.add_argument(
        "task",
        metavar="TASK",
        nargs="?",
        type=str,
        default="all",
        choices=WORKFLOWS_GENE,
        help="pipeline end point. Allowed values are " + ", ".join(WORKFLOWS_GENE),
    )
    parser_gene_wf.set_defaults(func=gene_wf)

    args = parser.parse_args()
    try:
        if args.version:
            print("metapi version %s" % metapi.__version__)
            sys.exit(0)
        args.func(args)
    except AttributeError as e:
        print(e)
        parser.print_help()


if __name__ == "__main__":
    main()
