import os
import copy
from operator import itemgetter
import sys
import shutil
import pysam
import operator
import pyfastaq
import pymummer
from ariba import common, mapping, bam_parse, flag, faidx

class Error (Exception): pass


class Cluster:
    def __init__(self,
      root_dir,
      name,
      assembly_kmer=0,
      assembler='velvet',
      max_insert=1000,
      min_scaff_depth=10,
      nucmer_min_id=90,
      nucmer_min_len=50,
      nucmer_breaklen=50,
      sspace_k=20,
      reads_insert=500,
      sspace_sd=0.4,
      threads=1,
      bcf_min_dp=10,
      bcf_min_dv=5,
      bcf_min_dv_over_dp=0.3,
      bcf_min_qual=20,
      assembled_threshold=0.95,
      unique_threshold=0.03,
      verbose=False,
      bcftools_exe='bcftools',
      gapfiller_exe='GapFiller.pl',
      samtools_exe='samtools',
      bowtie2_exe='bowtie2',
      bowtie2_preset='very-sensitive-local',
      smalt_exe='smalt',
      spades_exe='spades.py',
      sspace_exe='SSPACE_Basic_v2.0.pl',
      velvet_exe='velvet', # prefix of velvet{g,h}
      spades_other=None,
      clean=1,
    ):

        self.root_dir = os.path.abspath(root_dir)
        if not os.path.exists(self.root_dir):
            raise Error('Directory ' + self.root_dir + ' not found. Cannot continue')

        self.name = name
        self.reads1 = os.path.join(self.root_dir, 'reads_1.fq')
        self.reads2 = os.path.join(self.root_dir, 'reads_2.fq')
        self.gene_fa = os.path.join(self.root_dir, 'gene.fa')
        self.genes_fa = os.path.join(self.root_dir, 'genes.fa')
        self.gene_bam = os.path.join(self.root_dir, 'gene.reads_mapped.bam')

        for fname in [self.reads1, self.reads2, self.genes_fa]:
            if not os.path.exists(fname):
                raise Error('File ' + fname + ' not found. Cannot continue')


        self.max_insert = max_insert
        self.min_scaff_depth = min_scaff_depth

        self.nucmer_min_id = nucmer_min_id
        self.nucmer_min_len = nucmer_min_len
        self.nucmer_breaklen = nucmer_breaklen
        self.assembly_vs_gene_coords = os.path.join(self.root_dir, 'assembly_vs_gene.coords')

        self.bcf_min_dp = bcf_min_dp
        self.bcf_min_dv = bcf_min_dv
        self.bcf_min_dv_over_dp = bcf_min_dv_over_dp
        self.bcf_min_qual = bcf_min_qual

        self._set_assembly_kmer(assembly_kmer)
        self.assembler = assembler
        assert self.assembler in ['velvet', 'spades']
        self.spades_exe = spades_exe
        self.spades_other = spades_other

        self.bcftools_exe = bcftools_exe

        self.sspace_exe = shutil.which(sspace_exe)
        if self.sspace_exe is None:
            self.gapfiller_exe = None
        else:
            self.sspace_exe = os.path.realpath(self.sspace_exe) # otherwise sspace dies loading packages
            self.gapfiller_exe = shutil.which(gapfiller_exe)
            if self.gapfiller_exe is not None:
                self.gapfiller_exe = os.path.realpath(self.gapfiller_exe) # otherwise gapfiller dies loading packages

        self.samtools_exe = samtools_exe
        self.smalt_exe = smalt_exe
        self.bowtie2_exe = bowtie2_exe
        self.bowtie2_preset = bowtie2_preset

        if self.assembler == 'velvet':
            self.velveth = velvet_exe + 'h'
            self.velvetg = velvet_exe + 'g'

        self.sspace_k = sspace_k
        self.reads_insert = reads_insert
        self.sspace_sd = sspace_sd

        self.threads = threads
        self.verbose = verbose
        self.assembled_threshold = assembled_threshold
        self.unique_threshold = unique_threshold
        self.status_flag = flag.Flag()
        self.flag_file = os.path.join(self.root_dir, 'flag')
        self.clean = clean

        self.assembly_dir = os.path.join(self.root_dir, 'Assembly')
        try:
            os.mkdir(self.assembly_dir)
        except:
            raise Error('Error mkdir ' + self.assembly_dir)
        self.assembler_dir = os.path.join(self.assembly_dir, 'Assemble')
        self.assembly_contigs = os.path.join(self.assembly_dir, 'contigs.fa')
        self.scaffold_dir = os.path.join(self.assembly_dir, 'Scaffold')
        self.scaffolder_scaffolds = os.path.join(self.assembly_dir, 'scaffolds.fa')
        self.gapfill_dir = os.path.join(self.assembly_dir, 'Gapfill')
        self.gapfilled_scaffolds = os.path.join(self.assembly_dir, 'scaffolds.gapfilled.fa')
        self.final_assembly_fa = os.path.join(self.root_dir, 'assembly.fa')
        self.final_assembly_bam = os.path.join(self.root_dir, 'assembly.reads_mapped.bam')
        self.final_assembly_read_depths = os.path.join(self.root_dir, 'assembly.reads_mapped.bam.read_depths.gz')
        self.final_assembly_vcf = os.path.join(self.root_dir, 'assembly.reads_mapped.bam.vcf')
        self.final_assembly = {}
        self.mummer_variants = {}
        self.variant_depths = {}
        self.percent_identities = {}


    def _get_read_counts(self):
        count1 = pyfastaq.tasks.count_sequences(self.reads1) 
        count2 = pyfastaq.tasks.count_sequences(self.reads2) 
        if count1 == count2:
            return count1 + count2
        else:
            raise Error('Different number of fwd/rev reads in cluster ' + self.name + '! Cannot continue')


    def _get_total_alignment_score(self, gene_name):
        tmp_bam = os.path.join(self.root_dir, 'tmp.get_total_alignment_score.bam')
        assert not os.path.exists(tmp_bam)
        tmp_fa = os.path.join(self.root_dir, 'tmp.get_total_alignment_score.ref.fa')
        assert not os.path.exists(tmp_fa)
        faidx.write_fa_subset([gene_name], self.genes_fa, tmp_fa, samtools_exe=self.samtools_exe, verbose=self.verbose)
        mapping.run_bowtie2(
            self.reads1,
            self.reads2,
            tmp_fa,
            tmp_bam[:-4],
            threads=self.threads,
            samtools=self.samtools_exe,
            bowtie2=self.bowtie2_exe,
            bowtie2_preset=self.bowtie2_preset,
            verbose=self.verbose,
        ) 

        score = mapping.get_total_alignment_score(tmp_bam)
        os.unlink(tmp_bam)
        os.unlink(tmp_fa)
        os.unlink(tmp_fa + '.fai')
        return score


    def _get_best_gene_by_alignment_score(self):
        cluster_size = pyfastaq.tasks.count_sequences(self.genes_fa)
        if cluster_size == 1:
            seqs = {}
            pyfastaq.tasks.file_to_dict(self.genes_fa, seqs)
            assert len(seqs) == 1
            gene_name = list(seqs.values())[0].id
            if self.verbose:
                print('No need to choose gene for this cluster because only has one gene:', gene_name)
            return gene_name

        if self.verbose:
            print('\nChoosing best gene from cluster of', cluster_size, 'genes...')
        file_reader = pyfastaq.sequences.file_reader(self.genes_fa)
        best_score = 0
        best_gene_name = None
        for seq in file_reader:
            score = self._get_total_alignment_score(seq.id)
            if self.verbose:
                print('Total alignment score for gene', seq.id, 'is', score)
            if score > best_score:
                best_score = score
                best_gene_name = seq.id

        if self.verbose:
            print('Best gene is', best_gene_name, 'with total alignment score of', best_score)
            print()

        return best_gene_name


    def _choose_best_gene(self):
        gene_name = self._get_best_gene_by_alignment_score()
        faidx.write_fa_subset([gene_name], self.genes_fa, self.gene_fa, samtools_exe=self.samtools_exe, verbose=self.verbose)
        seqs = {}
        pyfastaq.tasks.file_to_dict(self.gene_fa, seqs)
        assert len(seqs) == 1
        return list(seqs.values())[0]


    def _set_assembly_kmer(self, k):
        '''If the kmer not given, uses 2/3 of the mean read length (using first 1000 forward and first 1000 reverse reads)'''
        if k == 0:
            read_length1 = pyfastaq.tasks.mean_length(self.reads1, limit=1000)
            read_length2 = pyfastaq.tasks.mean_length(self.reads2, limit=1000)
            self.assembly_kmer = round( (read_length1 + read_length2) / 3)
            if self.assembly_kmer % 2 == 0:
                self.assembly_kmer += 1
        else:
            self.assembly_kmer = k


    def _assemble_with_velvet(self):
        # map reads to reference gene to make BAM input to velvet columbus
        mapping.run_bowtie2(
            self.reads1,
            self.reads2,
            self.gene_fa,
            self.gene_bam[:-4],
            threads=self.threads,
            sort=True,
            samtools=self.samtools_exe,
            bowtie2=self.bowtie2_exe,
            bowtie2_preset=self.bowtie2_preset,
            verbose=self.verbose,
        )

        cmd = ' '.join([
            self.velveth,
            self.assembler_dir,
            str(self.assembly_kmer),
            '-reference', self.gene_fa,
            '-shortPaired -bam', self.gene_bam[:-4] + '.unsorted.bam'
        ])

        cwd = os.getcwd()
        os.chdir(self.assembly_dir)
        velvet_contigs = os.path.join(os.path.split(self.assembler_dir)[1], 'contigs.fa')

        self.velveth_ok, err = common.syscall(cmd, verbose=self.verbose, allow_fail=True)
        if not self.velveth_ok:
            with open('velveth_errors', 'w') as f:
                print(err, file=f)
                f.close()
            self.status_flag.add('assembly_fail')
            os.chdir(cwd)
            return

        cmd = ' '.join([
            self.velvetg,
            self.assembler_dir,
            '-ins_length', str(int(self.reads_insert)),
            '-scaffolding no',
            '-exp_cov auto',
            '-very_clean yes',
            '-cov_cutoff auto',
        ])

        self.assembled_ok, err = common.syscall(cmd, verbose=self.verbose, allow_fail=True)
        if self.assembled_ok:
            os.symlink(velvet_contigs, os.path.basename(self.assembly_contigs))
        else:
            with open('velvetg_errors', 'w') as f:
                print(err, file=f)
                f.close()
            self.status_flag.add('assembly_fail')

        os.chdir(cwd)


    def _assemble_with_spades(self, unittest=False):
        cmd = ' '.join([
            self.spades_exe,
            '-1', self.reads1,
            '-2', self.reads2,
            '-o', self.assembler_dir,
            '-k', str(self.assembly_kmer),
            '--threads', str(self.threads),
            '--trusted-contigs', self.gene_fa,
        ])
        if self.spades_other is not None:
            cmd += ' ' + self.spades_other

        cwd = os.getcwd()
        os.chdir(self.assembly_dir)
        spades_contigs = os.path.join(os.path.split(self.assembler_dir)[1], 'scaffolds.fasta')

        if unittest:
            os.mkdir(self.assembler_dir)
            open(spades_contigs, 'w').close()
            self.assembled_ok = True
        else:
            self.assembled_ok, err = common.syscall(cmd, verbose=self.verbose, allow_fail=True)
        if self.assembled_ok:
            os.symlink(spades_contigs, os.path.basename(self.assembly_contigs))
        else:
            with open('spades_errors', 'w') as f:
                print(err, file=f)
            f.close()
            self.status_flag.add('assembly_fail')

        os.chdir(cwd)


    def _scaffold_with_sspace(self):
        if not os.path.exists(self.assembly_contigs):
            raise Error('Cannot scaffold because contigs file not found: ' + self.assembly_contigs)

        try:
            os.mkdir(self.scaffold_dir)
        except:
            raise Error('Error mkdir '+  self.scaffold_dir)

        cwd = os.getcwd()

        if self.sspace_exe is None:
            os.chdir(self.assembly_dir)
            os.symlink(os.path.basename(self.assembly_contigs), os.path.basename(self.scaffolder_scaffolds))
            os.chdir(cwd)
            return

        os.chdir(self.scaffold_dir)
        lib_file = 'lib'
        with open(lib_file, 'w') as f:
            print('LIB', self.reads1, self.reads2, int(self.reads_insert), self.sspace_sd, 'FR', file=f)

        cmd = ' '.join([
            'perl', self.sspace_exe,
            '-k', str(self.sspace_k),
            '-l', lib_file,
            '-s', self.assembly_contigs
        ])

        sspace_scaffolds = os.path.abspath('standard_output.final.scaffolds.fasta')
        common.syscall(cmd, verbose=self.verbose)
        os.chdir(self.assembly_dir)
        os.symlink(os.path.relpath(sspace_scaffolds), os.path.basename(self.scaffolder_scaffolds))
        os.chdir(cwd)


    def _has_gaps_to_fill(self, filename):
        seq_reader = pyfastaq.sequences.file_reader(filename)
        for seq in seq_reader:
            if 'n' in seq.seq or 'N' in seq.seq:
                return True
        return False


    def _gap_fill_with_gapfiller(self):
        if not os.path.exists(self.scaffolder_scaffolds):
            raise Error('Cannot gap fill because scaffolds file not found: ' + self.scaffolder_scaffolds)


        cwd = os.getcwd()

        if self.gapfiller_exe is None or not self._has_gaps_to_fill(self.scaffolder_scaffolds):
            self._rename_scaffolds(self.scaffolder_scaffolds, self.gapfilled_scaffolds)
            return

        try:
            os.mkdir(self.gapfill_dir)
        except:
            raise Error('Error mkdir '+  self.gapfill_dir)

        os.chdir(self.gapfill_dir)
        lib_file = 'lib'
        with open(lib_file, 'w') as f:
            print('LIB', 'bwa', self.reads1, self.reads2, self.reads_insert, self.sspace_sd, 'FR', file=f)

        cmd = ' '.join([
            'perl', self.gapfiller_exe,
            '-l', lib_file,
            '-s', self.scaffolder_scaffolds
        ])

        gapfilled_scaffolds = os.path.join(self.gapfill_dir, 'standard_output', 'standard_output.gapfilled.final.fa')
        common.syscall(cmd, verbose=self.verbose)
        self._rename_scaffolds(gapfilled_scaffolds, self.gapfilled_scaffolds)
        os.chdir(cwd)


    def _rename_scaffolds(self, infile, outfile):
        freader = pyfastaq.sequences.file_reader(infile)
        f_out = pyfastaq.utils.open_file_write(outfile)
        i = 1
        for scaff in freader:
            scaff.id = self.gene.id + '.scaffold.' + str(i)
            i += 1
            print(scaff, file=f_out)
        pyfastaq.utils.close(f_out)


    def _run_nucmer(self, qry, outfile, show_snps=False):
        pymummer.nucmer.Runner(
            self.gene_fa,
            qry,
            outfile,
            min_id=self.nucmer_min_id,
            min_length=self.nucmer_min_len,
            breaklen=self.nucmer_breaklen,
            show_snps=show_snps
        ).run()


    def _fix_contig_orientation(self):
        if not os.path.exists(self.gapfilled_scaffolds):
            raise Error('Cannot fix orientation of assembly contigs because file not found: ' + self.gapfilled_scaffolds)

        tmp_coords = os.path.join(self.root_dir, 'tmp.coords')
        self._run_nucmer(self.gapfilled_scaffolds, tmp_coords)

        to_revcomp = set()
        not_revcomp = set()
        file_reader = pymummer.coords_file.reader(tmp_coords)
        for hit in file_reader:
            if hit.on_same_strand():
                not_revcomp.add(hit.qry_name)
            else:
                to_revcomp.add(hit.qry_name)

        os.unlink(tmp_coords)
        in_both = to_revcomp.intersection(not_revcomp)
        for name in in_both:
            print('WARNING: hits to both strands of gene for scaffold. Interpretation of any variants cannot be trusted', name, file=sys.stderr)
            to_revcomp.remove(name)

        f = pyfastaq.utils.open_file_write(self.final_assembly_fa)
        seq_reader = pyfastaq.sequences.file_reader(self.gapfilled_scaffolds)
        for seq in seq_reader:
            if seq.id in to_revcomp:
                seq.revcomp()
            print(seq, file=f)
        pyfastaq.utils.close(f)


    def _load_final_contigs(self):
        if not os.path.exists(self.final_assembly_fa):
            raise Error('Cannot load final assembled contigs because file not found:' + self.final_assembly_fa)

        self.final_assembly = {}
        pyfastaq.tasks.file_to_dict(self.final_assembly_fa, self.final_assembly)


    def _parse_assembly_bam(self):
        if not os.path.exists(self.final_assembly_bam):
            raise Error('File not found: ' + self.final_assembly_bam)

        bam_parser = bam_parse.Parser(self.final_assembly_bam, self.final_assembly)
        bam_parser.parse()
        bam_parser.write_files(self.final_assembly_bam)
        if not bam_parser.scaff_graph_is_consistent(self.min_scaff_depth, self.max_insert):
            self.status_flag.add('scaffold_graph_bad')


    def _parse_assembly_vs_gene_coords(self):
        file_reader = pymummer.coords_file.reader(self.assembly_vs_gene_coords)
        self.nucmer_hits = {}
        for hit in file_reader:
            assert hit.ref_name == self.gene.id
            contig = hit.qry_name
            if contig not in self.nucmer_hits:
                self.nucmer_hits[contig] = []
            self.nucmer_hits[contig].append(copy.copy(hit))


    def _nucmer_hits_to_percent_identity(self):
        self.percent_identities = {}
        for contig in self.nucmer_hits:
            product_sum = 0
            length_sum = 0
            for hit in self.nucmer_hits[contig]:
                product_sum += hit.hit_length_qry * hit.percent_identity
                length_sum += hit.hit_length_qry
            assert length_sum > 0
            self.percent_identities[contig] = round(product_sum / length_sum, 2)


    def _nucmer_hits_to_scaff_coords(self):
        coords = {}
        for l in self.nucmer_hits.values():
            for hit in l:
                if hit.qry_name not in coords:
                    coords[hit.qry_name] = []
                coords[hit.qry_name].append(hit.qry_coords())

        for scaff in coords:
            pyfastaq.intervals.merge_overlapping_in_list(coords[scaff])

        return coords


    def _nucmer_hits_to_ref_coords(self, contig=None):
        coords = []
        if contig is None:
            keys = list(self.nucmer_hits.keys())
        else:
            keys = [contig]

        for key in keys:
            coords += [hit.ref_coords() for hit in self.nucmer_hits[key]]
        coords.sort()
        return coords


    def _nucmer_hits_to_gene_cov_per_contig(self):
        cov = {}
        for contig in self.nucmer_hits:
            coords = self._nucmer_hits_to_ref_coords(contig)
            pyfastaq.intervals.merge_overlapping_in_list(coords)
            cov[contig] = pyfastaq.intervals.length_sum_from_list(coords)
        return cov


    def _whole_gene_covered_by_nucmer_hits(self):
        covered = self._nucmer_hits_to_ref_coords()
        pyfastaq.intervals.merge_overlapping_in_list(covered)
        return pyfastaq.intervals.length_sum_from_list(covered) / len(self.gene) >= self.assembled_threshold


    def _gene_coverage_unique(self):
        covered = self._nucmer_hits_to_ref_coords()
        covered.sort()
        if len(covered) <= 1:
            return True

        coverage = {}
        for i in covered:
            for j in range(i.start, i.end + 1):
                coverage[j] = coverage.get(j, 0) + 1

        bases_depth_at_least_two = len([1 for x in coverage.values() if x > 1])
        return bases_depth_at_least_two / len(self.gene) <= self.unique_threshold


    def _gene_covered_by_complete_contig_with_orf(self):
        for l in self.nucmer_hits.values():
            for hit in l:
                if hit.hit_length_ref == len(self.gene):
                    start = min(hit.qry_start, hit.qry_end)
                    end = max(hit.qry_start, hit.qry_end)
                    assembled_gene = pyfastaq.sequences.Fasta('x', self.final_assembly[hit.qry_name][start:end+1])
                    if (hit.ref_start < hit.ref_end) != (hit.qry_start < hit.qry_end):
                        assembled_gene.revcomp()
                    assembled_gene_aa = assembled_gene.translate()
                    orfs = assembled_gene.orfs()
                    if len(orfs) == 0:
                        continue

                    max_orf = orfs[0]
                    for o in orfs:
                        if len(o) > len(max_orf):
                            max_orf = o

                    if len(max_orf) == len(assembled_gene):
                        return True
        return False


    def _gene_covered_by_at_least_one_full_length_contig(self):
        for l in self.nucmer_hits.values():
            for hit in l:
                if len(hit.ref_coords()) == len(self.gene):
                    return True
        return False


    def _update_flag_from_nucmer_file(self):
        if self._whole_gene_covered_by_nucmer_hits():
            self.status_flag.add('gene_assembled')

        if self._gene_covered_by_at_least_one_full_length_contig():
            self.status_flag.add('gene_assembled_into_one_contig')

        if not self._gene_coverage_unique():
            self.status_flag.add('gene_region_assembled_twice')

        if self._gene_covered_by_complete_contig_with_orf():
            self.status_flag.add('complete_orf')

        if len(self.nucmer_hits) == 1:
            self.status_flag.add('unique_contig')


    def _get_mummer_variants(self):
        snp_file = self.assembly_vs_gene_coords + '.snps'
        if not os.path.exists(snp_file):
            raise Error('File not found ' + snp_file)
        variants = pymummer.snp_file.get_all_variants(snp_file)
        self.mummer_variants = {}

        if len(variants) == 0:
            return

        variants.sort(key=operator.attrgetter('qry_name'))
        variants.sort(key=operator.attrgetter('ref_start'))

        for v in variants:
            if v.qry_name not in self.mummer_variants:
                self.mummer_variants[v.qry_name] = []
            self.mummer_variants[v.qry_name].append(v)

        for contig in self.mummer_variants:
            l = self.mummer_variants[contig]
            if len(l) > 1:
                new_l = [[l[0]]]
                previous_codon_start = self._get_codon_start(0, l[0].ref_start)
                for variant in l[1:]:
                    codon_start = self._get_codon_start(0, variant.ref_start)
                    if codon_start == previous_codon_start:
                        new_l[-1].append(variant)
                    else:
                        new_l.append([variant])
                        previous_codon_start = codon_start
                self.mummer_variants[contig] = new_l
            else:
                self.mummer_variants[contig] = [l]


    def _filter_mummer_variants(self):
        if len(self.mummer_variants) == 0:
            return

        for contig in self.mummer_variants:
            variants = self.mummer_variants[contig]
            for i in range(len(variants)):
                t = self._get_variant_effect(variants[i])
                if t is not None and t[0] in ['TRUNC', 'FSHIFT']:
                    break
            self.mummer_variants[contig] = variants[:i+1]


    def _get_codon_start(self, gene_start, position):
        assert position >= gene_start
        while  (position - gene_start) % 3 != 0:
            position -= 1
        return position


    def _get_variant_effect(self, variants):
        if len(variants) == 0:
            return None

        var_types = [x.var_type for x in variants]
        if len(set(var_types)) != 1:
            return None

        var_type = var_types[0]

        assert set([x.ref_name for x in variants]) == set([self.gene.id])
        codon_starts = [self._get_codon_start(0, x.ref_start) for x in variants]
        assert len(set(codon_starts)) == 1
        codon_start = codon_starts[0]
        aa_start = codon_start // 3
        ref_codon = pyfastaq.sequences.Fasta('codon', self.gene[codon_start:codon_start+3])
        ref_aa = ref_codon.translate()

        if var_type == pymummer.variant.SNP:
            new_codon = list(ref_codon.seq)
            for v in variants:
                new_codon[v.ref_start - codon_start] = v.qry_base
            new_codon = pyfastaq.sequences.Fasta('new', ''.join(new_codon))
            qry_aa = new_codon.translate()

            if ref_aa.seq == qry_aa.seq:
                return ('SYN', '.')
            elif qry_aa.seq == '*':
                return ('TRUNC', ref_aa.seq + str(aa_start + 1) + 'trunc')
            else:
                return ('NONSYN', ref_aa.seq + str(aa_start + 1) + qry_aa.seq)
        elif var_type in [pymummer.variant.INS, pymummer.variant.DEL]:
            if len(variants) > 1:
                print('More than one indel in same codon not yet implemented!', self.gene.id, file=sys.stderr)
                return None

            var = variants[0]

            if var_type == pymummer.variant.INS:
                new_seq = pyfastaq.sequences.Fasta('seq', var.qry_base)
            else:
                new_seq = pyfastaq.sequences.Fasta('seq', var.ref_base)

            if len(new_seq) % 3 != 0:
                return ('FSHIFT', ref_aa.seq + str(aa_start + 1) + 'fs')

            new_seq_aa = new_seq.translate()
            if '*' in new_seq_aa.seq:
                return ('TRUNC', ref_aa.seq + str(aa_start + 1) + 'trunc')
            elif var_type == pymummer.variant.INS:
                ref_codon_after_ins = pyfastaq.sequences.Fasta('codon', self.gene[codon_start+3:codon_start+6])
                aa_after_ins = ref_codon_after_ins.translate()
                return ('INS', ref_aa.seq + str(aa_start + 1) + '_' + aa_after_ins.seq + str(aa_start + 2) + 'ins' + new_seq_aa.seq )
            else:
                if len(new_seq) == 3:
                    return ('DEL', ref_aa.seq + str(aa_start + 1) + 'del')
                else:
                    assert len(new_seq) % 3 == 0
                    new_aa = new_seq.translate()
                    ref_codon_after_ins = pyfastaq.sequences.Fasta('codon', self.gene[codon_start+3:codon_start+6])
                    aa_after_ins = ref_codon_after_ins.translate()
                    return ('DEL', ref_aa.seq + str(aa_start + 1)+ '_' + aa_after_ins.seq + str(aa_start + 2) + 'del')

        else:
            return ('UNKNOWN', '.')


    def _make_assembly_vcf(self):
        tmp_vcf = self.final_assembly_vcf + '.tmp'
        cmd = ' '.join([
            self.samtools_exe, 'mpileup',
            '-t INFO/DPR,DV',
            '-A',
            '-f', self.final_assembly_fa,
            '-u',
            '-v',
            self.final_assembly_bam,
            '>',
            tmp_vcf
        ])

        common.syscall(cmd, verbose=self.verbose)

        cmd = ' '.join([
            self.bcftools_exe, 'call -m',
            tmp_vcf,
            '|',
            self.bcftools_exe, 'query',
            r'''-f '%CHROM\t%POS\t%REF\t%ALT\t%DP\t%DPR]\n' ''',
            '>',
            self.final_assembly_read_depths + '.tmp'
        ])

        common.syscall(cmd, verbose=self.verbose)
        pysam.tabix_compress(self.final_assembly_read_depths + '.tmp', self.final_assembly_read_depths)
        pysam.tabix_index(self.final_assembly_read_depths, seq_col=0, start_col=1, end_col=1)
        os.unlink(self.final_assembly_read_depths + '.tmp')

        cmd = ' '.join([
            self.bcftools_exe, 'call -m -v',
            tmp_vcf,
            '|',
            self.bcftools_exe, 'filter',
            '-i', '"MIN(DP)>=' + str(self.bcf_min_dp),
                  ' & MIN(DV)>=' + str(self.bcf_min_dv),
                  ' & MIN(DV/DP)>=' + str(self.bcf_min_dv_over_dp),
                  ' & QUAL >=', str(self.bcf_min_qual), '"',
            '-o', self.final_assembly_vcf
        ])

        common.syscall(cmd, verbose=self.verbose)
        os.unlink(tmp_vcf)


    def _get_assembly_read_depths(self, ref, position):
        '''Returns total read depth and depth of reads supporting alternative (if present)'''
        assert os.path.exists(self.final_assembly_read_depths)
        assert os.path.exists(self.final_assembly_read_depths + '.tbi')
        tbx = pysam.TabixFile(self.final_assembly_read_depths)
        try:
            rows = [x for x in tbx.fetch(ref, position, position + 1)]
        except:
            return None
        if len(rows) == 1:
            r, p, ref_base, alt_base, ref_counts, alt_counts = rows[0].rstrip().split()
            return ref_base, alt_base, int(ref_counts), alt_counts
        else:
            return None


    def _get_samtools_variant_positions(self):
        if not os.path.exists(self.final_assembly_vcf):
            return []
        f = pyfastaq.utils.open_file_read(self.final_assembly_vcf)
        positions = [l.rstrip().split('\t')[0:2] for l in f if not l.startswith('#')]
        positions = [(t[0], int(t[1]) - 1) for t in positions]
        pyfastaq.utils.close(f)
        return positions
        

    def _get_samtools_variants(self, positions=None):
        if positions is None:
            positions = self._get_samtools_variant_positions()
        variants = {}
        if len(positions) == 0:
            return variants
        if not (os.path.exists(self.final_assembly_vcf) and os.path.exists(self.final_assembly_read_depths)):
            return variants
        for t in positions:
            print(t)
            name, pos = t[0], t[1]
            depths = self._get_assembly_read_depths(name, pos)
            if depths is None:
                raise Error('Error getting read depths for sequence ' + name + ' at position ' + t[1])
            if name not in variants:
                variants[name] = {}
            variants[name][t[1]] = depths
        return variants


    def _get_vcf_variant_counts(self):
        scaff_coords = self._nucmer_hits_to_scaff_coords()
        self.vcf_variant_counts = {}
        f = pyfastaq.utils.open_file_read(self.final_assembly_vcf)
        for line in f:
            if line.startswith('#'):
                continue

            data = line.rstrip().split('\t')
            scaff = data[0]

            if scaff in scaff_coords:
                position = int(data[1]) - 1
                i = pyfastaq.intervals.Interval(position, position)
                intersects = len([x for x in scaff_coords[scaff] if x.intersects(i)]) > 0
                if intersects:
                    self.vcf_variant_counts[scaff] = self.vcf_variant_counts.get(scaff, 0) + 1

        pyfastaq.utils.close(f)
        total = sum(list(self.vcf_variant_counts.values()))
        if total >= 1:
            self.status_flag.add('variants_suggest_collapsed_repeat')


    def _make_report_lines(self):
        self.report_lines = []
        total_reads = self._get_read_counts()

        if not self.assembled_ok:
            self.report_lines.append([
                    self.gene.id,
                    self.status_flag.to_number(),
                    total_reads,
                    self.name,
                    len(self.gene),
                    '.',
                    '.',
                  ] + \
                  ['.'] * 14
            )
            return

        cov_per_contig = self._nucmer_hits_to_gene_cov_per_contig()
        samtools_variants = self._get_samtools_variants()


        for contig in self.mummer_variants:
            for variants in self.mummer_variants[contig]:
                t = self._get_variant_effect(variants)
                if t is not None:
                    effect, new_bases = t
                    for v in variants:
                        depths = self._get_assembly_read_depths(contig, v.qry_start) 
                        if depths is None:
                            raise Error('Error getting depth info on contig "' + contig + '" at position ' + str(v.qry_start + 1) + ' from file ' + self.final_assembly_read_depths)
                        else:
                            ref_base, alt_base, ref_counts, alt_counts = depths

                        self.report_lines.append([
                            self.gene.id,
                            self.status_flag.to_number(),
                            total_reads,
                            self.name,
                            len(self.gene),
                            cov_per_contig[contig],
                            self.percent_identities[contig],
                            pymummer.variant.var_types[v.var_type],
                            effect,
                            new_bases,
                            v.ref_start + 1,
                            v.ref_end + 1,
                            v.ref_base,
                            v.qry_name,
                            v.qry_length,
                            v.qry_start + 1,
                            v.qry_end + 1,
                            v.qry_base,
                            ref_counts,
                            alt_base,
                            alt_counts,
                        ])

                        if contig in samtools_variants and v.qry_start in samtools_variants[contig]:
                            del samtools_variants[contig][v.qry_start]
                            if len(samtools_variants[contig]) == 0: 
                                del samtools_variants[contig]

            if contig in samtools_variants: 
                for pos in samtools_variants[contig]:
                    ref_base, alt_base, ref_counts, alt_counts = samtools_variants[contig][pos]
                    self.report_lines.append(
                      [
                        self.gene.id,
                        self.status_flag.to_number(),
                        total_reads,
                        self.name,
                        len(self.gene),
                        cov_per_contig[contig],
                        self.percent_identities[contig],
                      ] + \
                      ['.'] * 6 + \
                      [
                        contig,
                        len(self.final_assembly[contig]),
                        pos + 1,
                        pos + 1,
                        ref_base,
                        ref_counts,
                        alt_base,
                        alt_counts
                      ]
                    )
                        
        if len(self.report_lines) == 0:
            for contig in self.percent_identities:
                self.report_lines.append([
                    self.gene.id,
                    self.status_flag.to_number(),
                    total_reads,
                    self.name,
                    len(self.gene),
                    cov_per_contig[contig],
                    self.percent_identities[contig],
                  ] + \
                  ['.'] * 6 + [contig, len(self.final_assembly[contig])] + ['.'] * 6
                )

        self.report_lines.sort(key=itemgetter(0, 14, 15))

    def _clean(self):
        if self.verbose:
            print('Cleaning', self.root_dir)

        if self.clean > 0:
            if self.verbose:
                print('  rm -r', self.assembly_dir)
            shutil.rmtree(self.assembly_dir)

        to_clean = [
            [
                'assembly.reads_mapped.unsorted.bam',
            ],
            [
                'assembly.fa.fai',
                'assembly.reads_mapped.bam.scaff',
                'assembly.reads_mapped.bam.soft_clipped',
                'assembly.reads_mapped.bam.unmapped_mates',
                'assembly_vs_gene.coords',
                'assembly_vs_gene.coords.snps',
                'genes.fa',
                'genes.fa.fai',
                'reads_1.fq',
                'reads_2.fq',
            ],
            [
                'assembly.fa.fai',
                'assembly.reads_mapped.bam',
                'assembly.reads_mapped.bam.vcf',
                'assembly_vs_gene.coords',
                'assembly_vs_gene.coords.snps',
            ]
        ]

        for i in range(self.clean + 1):
            for fname in to_clean[i]:
                fullname = os.path.join(self.root_dir, fname)
                if os.path.exists(fullname):
                    if self.verbose:
                        print('  rm', fname)
                    os.unlink(fullname)


    def run(self):
        self.gene = self._choose_best_gene()

        if self.assembler == 'velvet':
            self._assemble_with_velvet()
        elif self.assembler == 'spades':
            self._assemble_with_spades()

        # velvet can finish successfully, but make an empty contigs file
        if self.assembled_ok:
            number_of_contigs = pyfastaq.tasks.count_sequences(self.assembly_contigs)
            if number_of_contigs == 0:
                self.assembled_ok = False
                self.status_flag.add('assembly_fail')

        if self.assembled_ok:
            # finish the assembly
            self._scaffold_with_sspace()
            self._gap_fill_with_gapfiller()
            self._fix_contig_orientation()
            self._load_final_contigs()

            # map reads to assembly
            mapping.run_bowtie2(
                self.reads1,
                self.reads2,
                self.final_assembly_fa,
                self.final_assembly_bam[:-4],
                threads=self.threads,
                sort=True,
                samtools=self.samtools_exe,
                bowtie2=self.bowtie2_exe,
                bowtie2_preset=self.bowtie2_preset,
                verbose=self.verbose,
            )
            self._parse_assembly_bam()


            # compare gene and assembly
            self._run_nucmer(self.final_assembly_fa, self.assembly_vs_gene_coords, show_snps=True)
            self._parse_assembly_vs_gene_coords()
            self._nucmer_hits_to_percent_identity()
            self._get_mummer_variants()
            self._filter_mummer_variants()
            self._update_flag_from_nucmer_file()
            self._make_assembly_vcf()
            self._get_vcf_variant_counts()

        self._make_report_lines()
        self._clean()
