"""

Tools to do with variant calling.


TODO:

test-variant-call should use vcf-patch-in

"""


import random, os, re, sys, collections, math, fractions, urllib

import nesoni
from nesoni import config, legion, io, bio, workspace, working_directory, \
                   reference_directory, workflows, bowtie, sam, reporting, \
                   statistics, grace, selection
from nesoni.third_party import vcf

MAX_QUALITY = 100.0 #One in ten billion. IGV doesn't like inf


def get_variants(record):
    variants = [ record.REF ]
    if isinstance(record.ALT,list):
        variants.extend(str(item) for item in record.ALT)
    else:
        variants.append(str(record.ALT))
    return variants

def get_variant_counts(sample):
    AO = sample.data.AO
    if not isinstance(AO,list):
        AO = [AO]
    return [ sample.data.RO ] + AO

def get_genotype(call):
    if call.data.GT is None or '.' in call.data.GT:
        return None
    assert re.match('[0-9]+(/[0-9]+)*$', call.data.GT), 'Unsupported genotype format: '%call.data.GT        
    return sorted(int(item) for item in call.data.GT.split('/'))

def genotypes_equal(gt1, gt2):
    if gt1 is None or gt2 is None:
        return False
    if len(gt1) == len(gt2):
        return gt1 == gt2
    n = fractions.gcd(len(gt1),len(gt2))
    gt1 = sorted(gt1 * (n//len(gt1)))
    gt2 = sorted(gt2 * (n//len(gt2)))
    return gt1 == gt2

def describe_genotype(gt, variants):
    if gt is None:
        return '?'
    return '/'.join(variants[item] for item in gt)

def describe_counts(counts, variants):
    if any(item is None for item in counts):
        return ''

    result = [ ]
    for i in sorted(xrange(len(counts)), key=lambda i: (-counts[i],i)):
        if counts[i]:
            result.append( '%dx%s' % (counts[i],variants[i]) )
    return ' '.join(result)


SNPEFF_FIELDS = ['Effect_Impact','Functional_Class','Codon_Change','Amino_Acid_change','Amino_Acid_length',
                 'Gene_Name','Gene_BioType','Coding','Transcript','Exon','ERRORS','WARNINGS']
SNPEFF_PRIORITIES = ['HIGH','MODERATE','LOW','MODIFIER']

def snpeff_describe(text):
    if not text: return []
    
    items = text.split(',')
    result = [ ]
    for item in items:
        head, tail = item.split('(')
        assert tail.endswith(')')
        tail = tail[:-1]
        parts = tail.split('|')
        parts = map(urllib.unquote, parts)
        priority = SNPEFF_PRIORITIES.index(parts[0])
        
        desc = head
        for part, name in zip(parts, SNPEFF_FIELDS):
            if part:
                desc += ' '+name+'='+part
        
        tags = [ head, parts[0] ]
        if parts[1]: tags.append(parts[1])
        
        result.append((priority, desc, tags))
    result.sort(key=lambda item: item[0])
    return [ item[1:] for item in result ]


def index_vcf(filename):
    """ IGV index a VCF file. 
        Don't fail if igvtools fails (eg not installed).
    """
    try:
        io.execute('igvtools index FILENAME',FILENAME=filename)
    except (OSError, AssertionError):
        print >> sys.stderr, 'Failed to index VCF file with igvtools. Continuing.'

    

@config.help("""
Run FreeBayes on a set of samples.

For high quality variant calling in bacteria, \
we suggest setting --ploidy greater than 1 here, \
then reducing the ploidy to 1 using "nesoni vcf-filter".
""")
@config.Main_section('samples', 
    'Working directories or BAM files. '
    'The read group should be set '
    '(nesoni\'s wrappers of read aligners do this as of version 0.87).'
    )
@config.Int_flag('depth_limit', 'Limit depth of coverage of BAM files to this before running freebayes. Use 0 for unlimited.')
@config.Int_flag('ploidy', 'Ploidy of genotype calls.')
@config.Float_flag('pvar', 'Probability of polymorphism.')
@config.Section('freebayes_options', 'Flags to pass to FreeBayes.', allow_flags=True, append=False)
class Freebayes(config.Action_with_prefix):
    depth_limit = 100
    ploidy = 4
    pvar = 0.9
    samples = [ ]
    freebayes_options = [ '--min-alternate-total', '2', '--genotype-qualities' ]

    def run(self):
        bams = [ ]
        reference = None
        reference2 = None
        
        extra = [ ]
        
        for sample in self.samples:
            if sam.is_bam(sample):
                bams.append(sample)
            elif os.path.isdir(sample):
                working = working_directory.Working(sample,True)
                bams.append( working.get_filtered_sorted_bam() )
                extra.append( '##sampleTags=' + ','.join(working.get_tags()) )
                if reference2 is None:
                    reference2 = working.get_reference().reference_fasta_filename()
            elif io.is_sequence_file(sample):
                assert reference is None, 'Only one reference FASTA file allowed.'
                reference = sample
        
        if reference is None:
            reference = reference2
        if reference is None:
            raise grace.Error('No reference FASTA file given.')
        
        with nesoni.Stage() as stage:
            tempspace = stage.enter( workspace.tempspace() )
            if self.depth_limit:
                with nesoni.Stage() as stage2:
                    for i in xrange(len(bams)):
                        sam.Bam_depth_limit(
                            tempspace/('%d'%i), 
                            bams[i], 
                            depth=self.depth_limit
                            ).process_make(stage2)
                        bams[i] = tempspace/('%d.bam'%i)
            
            # FreeBayes claims to handle multiple bams, but it doesn't actually work
            if len(bams) > 1:
                sam.Bam_merge(tempspace/'merged', bams=bams, index=False).run()
                bams = [ tempspace/'merged.bam' ]
        
            command = [ 
                'freebayes',
                '-f', reference,
                '--ploidy',str(self.ploidy),
                '--pvar',str(self.pvar),
                ] + self.freebayes_options + bams
            
            self.log.log('Running: '+' '.join(command)+'\n')
        
            f_out = stage.enter( open(self.prefix+'.vcf','wb') )
            f_in  = stage.enter( io.pipe_from(command) )
            done_extra = False
            for line in f_in:
                if not done_extra and not line.startswith('##'):
                    for extra_line in extra:
                        f_out.write(extra_line+'\n')
                    done_extra = True
                f_out.write(line)

        index_vcf(self.prefix+'.vcf')


class _Filter(Exception): pass

@config.help("""\
Filter a VCF file, eg as produced by "nesoni freebayes:".

Ploidy reduction:

- reduce ploidy of genotype calls
  eg reducing ploidy from 4 to 2 would
     1/1/1/1 -> 1/1
     1/1/2/2 -> 1/2
     1/2/2/2 -> ./. (fail)

Dirichlet qualities:

- genome qualities (GQ) are replaced with qualities calculated using the Dirichlet model

- this currently reduces the ploidy to one

Filtering:

- genotype calls that don't pass filters (eg genotype quality) are failed

- variants in which genotyping failed in all samples are removed

- variants in which all genotypes match the reference are removed

Note that phased VCF files are not supported.

""")
@config.Bool_flag('dirichlet',
    'Replace existing genotype qualities (GQ) with dirichlet distribution derived qualities. '
    )
@config.Float_flag('dirichlet_prior',
    'Prior weight given to the reference and each variant.'
    )
@config.Float_flag('dirichlet_total_prior',
    'Minimum total prior. '
    'Allows that there might be further unobserved variants. '
    'Note that in the simple case of a SNP '
    ' --dirichlet yes --dirichlet-prior 0.2 --dirichlet-total-prior 1.0 '
    'yields prior beliefs as though there was a single observation of '
    'that may have been A, C, G, T, or something else (indel/MNP).'
    )
@config.Float_flag('dirichlet_majority',
    'A mixture of variants is genotyped as being a particular variant if it makes up at least this '
    'proportion of the mixture.'
    )
@config.Float_flag('min_gq', 
    'Genotype quality cutoff, based on GQ as produced by the Dirichlet model if Dirichlet is enabled, '
    'or as originally listed in the file if not. This is a phred-style scale.'
    )
@config.Int_flag('ploidy', 
    'Reduce to this polidy. Should be a divisor of the ploidy of the input. '
    'If the genotype does not have an exact representation at the reduced ploidy, it is filtered.')
@config.Positional('vcf', 'VCF file, eg as produced by "nesoni freebayes:"')
class Vcf_filter(config.Action_with_prefix):
    vcf = None
    
    dirichlet = True
    dirichlet_prior = 0.2
    dirichlet_total_prior = 1.0
    dirichlet_majority = 0.5

    min_gq = 20.0
    ploidy = 1
    
    def _blank_gt(self):
        return '/'.join(['.']*self.ploidy)
    
    def _reference_gt(self):
        return '/'.join(['0']*self.ploidy)

    def _make_sample_dirichlet(self, variants, sample):
        counts = get_variant_counts(sample)
        
        if any(item is None for item in counts):
            GT = '.'
            p = 0.0
        else:
            GT = max(xrange(len(counts)), key=lambda i:counts[i])
            p = statistics.probability_of_proportion_at_least(
                counts[GT]+self.dirichlet_prior,
                sum(counts)+max(self.dirichlet_total_prior, self.dirichlet_prior*len(counts)),
                self.dirichlet_majority)

        if p >= 1.0:
           GQ = float('inf')
        elif p <= 0.0:
           GQ = 0.0
        else:
           GQ = math.log10(1-p) * -10.0 
        sample.data = sample.data._replace(
            GT=str(GT),
            GQ=min(MAX_QUALITY, GQ),
            )

            
    def _modify_sample(self, variants, sample):
        if self.dirichlet:
            self._make_sample_dirichlet(variants, sample)
        
        try:
            if sample.data.GT is None or '.' in sample.data.GT: 
                raise _Filter()

            if self.min_gq is not None and (math.isnan(sample.data.GQ) or sample.data.GQ < self.min_gq):
                raise _Filter()
        
            gt = get_genotype(sample)            
            assert len(gt) % self.ploidy == 0, 'Can\'t reduce ploidy from %d to %d' % (len(gt),self.ploidy)
            stride = len(gt) // self.ploidy
        
            new_gt = [ ]
            for i in xrange(0,len(gt),stride):
                if len(set(gt[i:i+stride])) != 1:
                    raise _Filter()
                new_gt.append(gt[i])        

            new_gt = '/'.join(str(item) for item in new_gt)        
        except _Filter:
            new_gt = self._blank_gt()
        sample.data = sample.data._replace(GT=new_gt)
            
    
    def run(self):
        if self.dirichlet:
            assert self.ploidy == 1, 'Dirichlet mode is not available for ploidy > 1'
        
        reader_f = io.open_possibly_compressed_file(self.vcf)
        reader = vcf.Reader(reader_f)
        
        writer = vcf.Writer(open(self.prefix + '.vcf','wb'), reader)
        
        #print dir(reader)
        #print reader.formats
        #print 
        #print reader.infos
        #print 
        
        n = 0
        n_kept = 0
        
        for record in reader:
            n += 1
            variants = get_variants(record)
            
            any = False
            
            for sample in record.samples:
                self._modify_sample(variants, sample)
                
                any = any or (sample.data.GT != self._blank_gt() and sample.data.GT != self._reference_gt())

                #print call.sample
                #for key in call.data._fields:
                #    print key, getattr(call.data,key), reader.formats[key].desc
                #    
                #counts = [ call.data.RO ]
                #if isinstance(call.data.QA,list):
                #    counts.extend(call.data.QA)
                #else:
                #    counts.append(call.data.QA)
                #print variants, counts
                #
                #
                #if self.min_gq is not None and call.data.GQ < self.min_gq:
                #    call.data = call.data._replace(GT='.')
                #    print call.data
                #else:
                #    any = True
            
            if self.dirichlet:
                record.QUAL = min(MAX_QUALITY, sum(sample.data.GQ for sample in record.samples))
            
            if any:
                writer.write_record(record)
                n_kept += 1
                
        writer.close()
        reader_f.close()
        
        self.log.datum('variants','input', n)
        self.log.datum('variants','kept',  n_kept)
        
        index_vcf(self.prefix+'.vcf')


@config.help("""\
Run SnpEff to annotate variants with their effects.
""")
@config.Positional('reference', 'Reference directory')
@config.Positional('vcf', 'VCF file')
class Snpeff(config.Action_with_prefix):
    reference = None
    vcf = None
    
    def run(self):
        reference = reference_directory.Reference(self.reference, must_exist=True)
        
        jar = io.find_jar('snpEff.jar')
        
        with open(self.prefix + '.vcf','wb') as f:
            io.execute('java -jar JAR eff GENOME VCF -c CONFIG',
                JAR=jar, GENOME=reference.name, VCF=self.vcf, CONFIG=reference/'snpeff.config',
                stdout=f)

        index_vcf(self.prefix+'.vcf')



_Nway_record = collections.namedtuple('_Nway_record', 'variants genotypes counts qualities snpeff record')


@config.help("""\
Summarize a VCF file in various ways. The VCF file is presumed to have been \
filtered with "vcf-filter:" or similar such that samples only have a value for \
GT when a genotype can be called with confidence.

The reference sequence is included in the output, with name "reference". \
To exclude it use "--select -reference".

Variants are only output if there are at least two genotypes within the \
selected samples. Various other filters may be applied in addition to this, \
see list of flags.
""")
@config.String_flag('as_',
    'Output format.\n'
    'Options are:\n'
    '  vcf - filtered VCF\n'
    '  table - tabular CSV output\n'
    '  nexus - nexus file suitable for SplitsTree, etc\n'
    '  splitstree - output nexus file and then run SplitsTree to produce a phylogenetic net\n'
    'Note: nexus output will output missing sites unless you specify "--require all". '
    'Your phylogenetic software may or may not do something sane with this.')
@config.Bool_flag('qualities', 'Output qualities in table format.')
@config.Bool_flag('counts', 'Output observed variant counts in table format.')
@config.String_flag('select', 'A selection expression to select samples (see main help text).')
@config.String_flag('sort', 'A sort expression to sort samples (see main help text).')
@config.String_flag('require', 'A selection expression. '
                               'Only output variants where these samples have a called genotype. '
                               'For example "--require all" will require all selected samples to have a called genotype.')
@config.String_flag('snpeff_show', 'A selection expression. '
                                   'Show effects based on Effect, Effect_Impact or Functional_Class.')
@config.String_flag('snpeff_filter', 'A selection expression. '
                                     'Only output variants with a matching effect, using Effect, Effect_Impact or Functional_Class. '
                                     'For example "--snpeff-filter NON_SYNONYMOUS_CODING" will output only changes that modify an amino acid.')                                   
@config.Bool_flag('only_snps', 'Only output SNPs.')
@config.Positional('vcf', 'VCF file')
#@config.Section('contrast', 
#    'Two or more selection expressions defining sub-groups. '
#    'Only output variants that can be used to distinguish between some pair of sub-groups in this list.',
#    allow_flags=True)
class Vcf_nway(config.Action_with_prefix):
    as_ = 'table'
    qualities = False
    counts = False
    select = 'all'
    sort = ''
    require = ''
    only_snps = False
    snpeff_show = 'HIGH/MODERATE/LOW'
    snpeff_filter = 'all'
    #contrast = [ ]

    vcf = None
    
    def run(self):
        reader_f = io.open_possibly_compressed_file(self.vcf)
        reader = vcf.Reader(reader_f)

        tags = { }
        for item in reader.metadata.get('sampleTags',[]):
            parts = item.split(',')
            tags[parts[0]] = parts
        
        assert 'reference' not in reader.samples, 'Can\'t have a sample called reference, sorry.'

        samples = [ 'reference'] + reader.samples
        
        for sample in samples:
            if sample not in tags:
                tags[sample] = [ sample, 'all' ]

        samples = selection.select_and_sort(
            self.select, self.sort, samples, lambda sample: tags[sample])
        
        required = [ i for i, sample in enumerate(samples)
                     if selection.matches(self.require, tags[sample]) ]
        
        sample_number = dict((b,a) for a,b in enumerate(reader.samples))
        
        items = [ ]
        for record in reader:
            variants = get_variants(record)
            genotypes = [ ]
            counts = [ ]
            qualities = [ ]
            for sample in samples:
                if sample == 'reference':
                    genotypes.append([0])
                    counts.append([1])
                    qualities.append(float('inf'))
                else:
                    genotypes.append(get_genotype(record.samples[sample_number[sample]]))
                    counts.append(get_variant_counts(record.samples[sample_number[sample]]))
                    qualities.append(record.samples[sample_number[sample]].data.GQ)

            # Only output when there are at least two genotypes            
            any_interesting = False
            for i in xrange(len(genotypes)):
                for j in xrange(i):
                    if (genotypes[i] is not None and genotypes[j] is not None and
                        not genotypes_equal(genotypes[i], genotypes[j])):
                        any_interesting = True
                        break
                if any_interesting: break
            if not any_interesting:
                continue

            if any(genotypes[i] is None for i in required):
                continue
                
            if self.only_snps and any(
                genotype is not None and any(len(variants[i]) != 1 for i in genotype)
                for genotype in genotypes):
                continue
                
            snpeff = snpeff_describe(record.INFO.get('EFF',''))
            if not any( selection.matches(self.snpeff_filter, item[1]) for item in (snpeff or [('',[])]) ):
                continue

            items.append(_Nway_record(variants=variants, genotypes=genotypes, counts=counts, qualities=qualities, snpeff=snpeff, record=record))
        
        self.log.log('%d variants\n\n' % len(items))
        
        if self.as_ == 'table':
            self._write_table(samples, items)
        elif self.as_ == 'nexus':
            self._write_nexus(samples, items)
        elif self.as_ == 'splitstree':
            self._write_nexus(samples, items)
            
            io.execute(
                'SplitsTree +g -i INPUT -x COMMAND',
                no_display=True,
                INPUT=self.prefix + '.nex',
                COMMAND='UPDATE; '
                        'SAVE FILE=\'%s.nex\' REPLACE=yes; '
                        'EXPORTGRAPHICS format=svg file=\'%s.svg\' REPLACE=yes TITLE=\'NeighborNet from %d variants\'; ' 
                        'QUIT' 
                        % (self.prefix, self.prefix, len(items)),
                )
        elif self.as_ == 'vcf':
            self._write_vcf(samples, items, reader)
        
        else:
            raise grace.Error('Unknown output format: '+self.as_)
        
    def _write_table(self, samples, items):
        names = [ '%s:%d' % (item.record.CHROM, item.record.POS) for item in items ]
        sample_list = io.named_list_type(samples)
        
        groups = [ ]
        
        locations_list = io.named_list_type(['CHROM','POS'])
        locations = io.named_list_type(names, locations_list)([
            locations_list([ item.record.CHROM, item.record.POS ])
            for item in items
            ])
        groups.append(('Location',locations))
                
        genotypes = io.named_list_type(names,sample_list)([
            sample_list([ describe_genotype(item2,item.variants) for item2 in item.genotypes ])
            for item in items
            ])
        groups.append(('Genotype',genotypes))

        if self.qualities:
            qualities = io.named_list_type(names,sample_list)([
                sample_list(item.qualities)
                for item in items
                ])
            groups.append(('Quality',qualities))

        if self.counts:        
            counts = io.named_list_type(names,sample_list)([
                sample_list([ describe_counts(item2,item.variants) for item2 in item.counts ])
                for item in items
                ])
            groups.append(('Count',counts))
        
        annotation_list = io.named_list_type(['snpeff'])
        annotations = io.named_list_type(names, annotation_list)([
            annotation_list([
                ' /// '.join(item2[0] for item2 in item.snpeff if selection.matches(self.snpeff_show, item2[1]))
                ])
            for item in items
            ])
        groups.append(('Annotation',annotations))
        
        io.write_grouped_csv(self.prefix + '.csv', groups)
    
    def _write_nexus(self, samples, items):
        for item in items:
            assert len(item.variants) <= 10
        
        buckets = [ [] for sample in samples ]
        for item in items:
            if all(item2 in ('A','C','G','T') for item2 in item.variants):
                var_names = item.variants
            else:
                var_names = [ chr(ord('0')+i) for i in xrange(len(item.variants)) ]
            for i, item2 in enumerate(item.genotypes):
                assert item2 is None or len(item2) == 1, 'Only ploidy 1 is allowed for nexus output.'
                if item2 is None:
                    buckets[i].append('N')
                else:
                    buckets[i].append(var_names[item2[0]])
            
        with open(self.prefix + '.nex','wb') as f:
            print >> f, '#NEXUS'
            print >> f, 'begin taxa;'
            print >> f, 'dimensions ntax=%d;' % len(samples)
            print >> f, 'taxlabels'
            for name in samples:
                print >> f, name
            print >> f, ';'
            print >> f, 'end;'
            
            print >> f, 'begin characters;'
            print >> f, 'dimensions nchar=%d;' % len(items)
            print >> f, 'format datatype=STANDARD symbols="ACGT0123456789" missing=N;'
            print >> f, 'matrix'
            for name, bucket in zip(samples, buckets):
                print >> f, name, ''.join(bucket)
            print >> f, ';'
            print >> f, 'end;'

    def _write_vcf(self, samples, items, reader):
        # Modifies reader and items!
        
        shuffle = [
            reader.samples.index(sample)
            for sample in samples
            if sample != 'reference'
            ]
        
        reader.samples = [ reader.samples[i] for i in shuffle ]
        writer = vcf.Writer(open(self.prefix + '.vcf','wb'), reader)
        
        for item in items:
            record = item.record
            record.samples = [ record.samples[i] for i in shuffle ]
            writer.write_record(record)
        
        writer.close()
        index_vcf(self.prefix+'.vcf')
    

@config.help("""\
Patch variants in a VCF file into the reference sequence, \
producing genome sequences for each sample in the VCF file.

Only haploid variants are supported.

Note that in parts of the sequence with insufficient coverage to call variants \
or in which the variant could not be called for some other reason, \
the reference sequence will incorrectly be retained.
""")
@config.Positional('reference', 'Reference directory')
@config.Positional('vcf', 'VCF file')
class Vcf_patch(config.Action_with_output_dir):
    reference = None
    vcf = None
    
    def run(self):
        workspace = self.get_workspace()
        
        reference = reference_directory.Reference(self.reference, must_exist=True)
        
        reader_f = io.open_possibly_compressed_file(self.vcf)
        reader = vcf.Reader(reader_f)
        variants = collections.defaultdict(list)
        for record in reader:
            variants[record.CHROM].append(record)
        reader_f.close()
        
        for chrom in variants:
            variants[chrom].sort(key=lambda item: item.POS)
        
        filenames = [ workspace/(item+'.fa') for item in reader.samples ]
        for filename in filenames:
            with open(filename,'wb'): pass
        
        for name, seq in io.read_sequences(reference.reference_fasta_filename()):
            for i, sample in enumerate(reader.samples):            
                revised = [ ]
                pos = 0
                for variant in variants[name]:
                    gt = variant.samples[i].data.GT
                    if gt is None: continue
                    assert gt.isdigit(), 'Unsupported genotype (can only use haploid genotypes): '+gt
                    gt_number = int(gt)
                    if gt_number == 0:
                        var_seq = variant.REF
                    else:
                        var_seq = str(variant.ALT[gt_number-1])
                        assert re.match('[ACGTN]*$', var_seq), 'Unsupported variant type: '+var_seq
                    new_pos = variant.POS-1
                    assert new_pos >= pos, 'Variants overlap.'
                    revised.append(seq[pos:new_pos])
                    pos = new_pos
                    revised.append(var_seq)
                    assert seq[pos:pos+len(variant.REF)].upper() == variant.REF, 'REF column in VCF does not match reference sequence'
                    pos += len(variant.REF)
                revised.append(seq[pos:])
                            
                with open(filenames[i],'ab') as f:
                    io.write_fasta(f, name, ''.join(revised))

            del variants[name]        
        assert not variants, 'Chromosome names in VCF not in reference: '+' '.join(variants)
        
        


def rand_seq(n):
    return ''.join( 
        random.choice('ACGT') 
        for i in xrange(n) 
    )

@config.Positional('ref', 'Reference sequence\neg AAG')
@config.Main_section('variants', 
    'Variants, each with a number of reads, eg ACGx10 ATGx5. '
    'The first variant given is treated as the correct variant.')
@config.Configurable_section('analysis', 'Options for "nesoni analyse-sample:"', presets=[
    ('shrimp', lambda obj: nesoni.Analyse_sample(clip=None), 'Do analysis using SHRiMP'),
    ('bowtie', lambda obj: nesoni.Analyse_sample(clip=None,align=bowtie.Bowtie()), 'Do analysis using Bowtie'),
    ])
@config.Configurable_section('freebayes', 'Options for "nesoni freebayes:"', presets=[
    ('freebayes', lambda obj: Freebayes(), ''),
    ])
@config.Configurable_section('vcf_filter', 'Options for "nesoni vcf-filter:"', presets=[
    ('vcf-filter', lambda obj: Vcf_filter(), ''),
    ])
class Test_variant_call(config.Action_with_output_dir):
    ref = None
    variants = [ ]
    
    #analysis = _analysis_presets[0][1]()
    #freebayes = Freebayes()
    #vcf_filter = Vcf_filter()
    
    def run(self):
        workspace = self.get_workspace()
        
        read_length = 100
        left = rand_seq(read_length-1)
        while True:
            flank = rand_seq(1)
            if flank != self.ref[:1]: break
        left += flank
        
        right = rand_seq(read_length-1)
        while True:
            flank = rand_seq(1)
            if flank != self.ref[-1:]: break
        right = flank+right
        
        i = 0
        
        variants_used = [ ]
        
        with open(workspace/'reads.fq','wb') as f:
            for i, variant in enumerate(self.variants):
                if 'x' in variant:
                    variant, count = variant.split('x')
                    count = int(count)
                else:
                    count = 10
                variants_used.append( (variant,count) )
                seq = left+variant+right
                for j in xrange(count):
                    pos = len(variant)+random.randrange(read_length-len(variant))
                    read = seq[pos:pos+read_length]
                    if random.randrange(2):
                        read = bio.reverse_complement(read)
                    i += 1
                    io.write_fastq(f,'read_%s_%d' % (variant,i),read,chr(64+30)*len(read))

        reference = left+self.ref+right
        primary_variant = left+variants_used[0][0]+right

        with open(workspace/'reference.fa','wb') as f:
            io.write_fasta(f,'chr1',reference)
        
        legion.remake_needed()
        
        self.analysis(
            workspace/'sample',
            workspace/'reference.fa',
            reads = [ workspace/'reads.fq' ],
            ).run()
        
        self.freebayes(
            workspace/'freebayes',
            workspace/'sample',
            ).run()
        
        self.vcf_filter(
            workspace/'filtered',
            workspace/'freebayes.vcf',
            ).run()
        
        Vcf_patch(
            workspace/'patch',
            workspace/('sample','reference'),
            workspace/'filtered.vcf'
            ).run()
        
        patched = io.read_sequences(workspace/('patch','sample.fa')).next()[1]
        
        masked = io.read_sequences(workspace/('sample','consensus_masked.fa')).next()[1].upper()
        
        with open(workspace/'freebayes.vcf','rU') as f:
            reader = vcf.Reader(f)
            raw_count = len(list(reader))
        
        with open(workspace/'filtered.vcf','rU') as f:
            reader =  vcf.Reader(f)
            filtered_count = len(list(vcf.Reader(open(workspace/'filtered.vcf','rU'))))
        
        with open(workspace/('sample','report.txt'),'rb') as f:
            nesoni_count = len(f.readlines()) - 1

        self.log.log('\n')
        self.log.datum(workspace.name,'changes found by "nesoni consensus:"', nesoni_count)
        self.log.datum(workspace.name,'is correctly patched by "nesoni consensus:"', masked == primary_variant)
        self.log.log('\n')
        self.log.datum(workspace.name,'raw variants', raw_count)
        self.log.datum(workspace.name,'variants after filtering', filtered_count)
        self.log.datum(workspace.name,'is correctly patched by VCF pipeline', patched == primary_variant)
        self.log.log('\n')


@config.help("""
Assess ability to call variants under a spread of different conditions.
""")
@config.Bool_flag('legacy', 'Also report performance of older "nesoni consensus:" variant caller.')
@config.Configurable_section('template','Setting for "nesoni test-variant-call".', presets=[
    ('test-variant-call', lambda obj: Test_variant_call(), ''),
    ])
class Power_variant_call(config.Action_with_prefix):
    legacy = True
    #template = Test_variant_call()

    def tryout(self, ref, variants):
        with workspace.tempspace() as temp:
            job = self.template(temp.working_dir, ref=ref, variants=variants)            
            job.run()            
            
            #result = dict( tuple(item.values()) for item in reporting.mine_logs([job.log_filename()]) )
            [ result ] = reporting.mine_logs([job.log_filename()]).values()
            nesoni_count = int(result['changes found by "nesoni consensus:"'])
            nesoni_good = {'yes':True,'no':False}[result['is correctly patched by "nesoni consensus:"']]
            vcf_count = int(result['variants after filtering'])
            vcf_good = {'yes':True,'no':False}[result['is correctly patched by VCF pipeline']]
            return nesoni_count, nesoni_good, vcf_count, vcf_good

    def depth_test(self, ref, variant, others=[]):
        depths = range(1,30+1)
        #results = [ self.tryout(ref, ['%sx%d'%(variant,i)] + others) for i in depths ]
        result_futures = [ nesoni.future(self.tryout, ref, ['%sx%d'%(variant,i)] + others) for i in depths ]
        results = [ item() for item in result_futures ]
        
        report = '%s -> %s' % (ref or '-', variant or '-')
        if others: report += '  with contamination  ' + ', '.join(others)
        report += '\n'
        
        if self.legacy:
            report += 'nesoni consensus: [' + ''.join( '+' if item[1] else 'X' if item[0] else ' ' for item in results ) + ']\n'
        report += 'VCF pipeline      [' + ''.join( '+' if item[3] else 'X' if item[2] else ' ' for item in results ) + ']\n'

        depth_line = ''
        for i in depths:
            if i == 1 or i % 5 == 0:
                depth_line += ' '*(i-len(depth_line)) + str(i)
        report += 'depth             '+depth_line+'\n'
        
        return report
        

    def run(self):
        report = ''
        
        futures = [ ]
        for job in [
            ('A','C',[]),
            ('A','C',['Gx1']),
            ('A','C',['Gx2']),
            ('A','',[]),
            ('AC','',[]),
            ('ACGT','',[]),
            ('ACGTAGCT','',[]),
            #('ACGTAGCTAGACCTGT','',[]),
            ('','A',[]),
            ('','AC',[]),
            ('','ACGT',[]),
            ('','ACGTAGCT',[]),
            #('','ACGTAGCTAGACCTGT',[]),
        ]:  
            futures.append( nesoni.thread_future(self.depth_test, *job) )
        
        for item in futures:      
            report += item()+'\n'
        
        self.log.log(
            '\n'
            ' + = correct variant called\n'
            ' X = incorrect variant called\n'
            '\n')
        
        self.log.log(report + '\n')



