
from nesoni import config, legion, workspace, working_directory, reference_directory, io, grace, selection, sam


@config.help("""\

Align reads using Bowtie 2.

Paired end reads should either be given as two files in the "pairs"
section, or as a single interleaved file in the "interleaved" section.

""")
@config.Main_section('references', 
    'Reference sequence filenames, '
    'or a directory created using "nesoni make-reference: --bowtie yes" (recommended).')
@config.Int_flag('cores', 'Maximum cores to use.', affects_output=False)
@config.Section('reads', 'FASTQ files containing unpaired reads.')
@config.Section('interleaved', 'FASTQ files containing interleaved read pairs.')
@config.Grouped_section('pairs', 'Pair of FASTQ files containing read pairs.')
@config.Section('bowtie_options', 'Options to pass to bowtie.', allow_flags=True, append=False)
class Bowtie(config.Action_with_output_dir):
    cores = 8
    references = []
    reads = []
    interleaved = []
    pairs = []
    bowtie_options = [ '--no-discordant', '--no-mixed', '-k', '10' ]
    
    _workspace_class = working_directory.Working
    
    #def cores_required(self):
    #    # All of them, please.
    #    return legion.coordinator().get_cores()

    def run(self):
        assert self.reads or self.pairs or self.interleaved, 'No reads given'
    
        io.check_name_uniqueness(self.reads, self.pairs, self.interleaved)
        
        working = self.get_workspace()
        working.setup_reference(self.references, bowtie=True)
        working.update_param(snp_cost=2.0)        
        reference = working.get_reference()
        
        log_file = open(self.log_filename(),'wb')
              
        with workspace.tempspace(dir=working.working_dir) as temp:
            n = [ 0 ]
            def tempname():
                n[0] += 1
                return temp/('%d.fq'%n[0])
            def convert(filename):
                info = io.get_file_info(filename)
                ok = selection.matches('type-fastq:[compression-none/compression-gzip/compression-bzip2]', info)
                if ok:
                    return filename            
                result_name = tempname()
                with open(result_name,'wb') as f:
                    for name, seq, qual in io.read_sequences(filename, qualities='required'):
                        io.write_fastq(f, name, seq, qual)
                return result_name
            
            ones = [ ]
            twos = [ ]
            singles = [ ]
            
            for pair in self.pairs:
                assert len(pair) == 2, 'Need two files in each "pair:" section.'
                ones.append(convert(pair[0]))
                twos.append(convert(pair[1]))
            
            for item in self.interleaved:
                left_name = tempname()
                right_name = tempname()
                ones.append(left_name)
                twos.append(right_name)
                with open(left_name,'wb') as left, \
                     open(right_name,'wb') as right:
                    reader = io.read_sequences(item, qualities='required')
                    while True:
                        try:
                            name, seq, qual = reader.next()
                        except StopIteration:
                            break
                        io.write_fastq(left, name,seq,qual)
                        
                        try:
                            name, seq, qual = reader.next()
                        except StopIteration:
                            raise grace.Error('Interleaved file contains odd number of sequences')
                        io.write_fastq(right, name,seq,qual)
            
            for item in self.reads:
                singles.append(convert(item))

            cores = min(self.cores, legion.coordinator().get_cores())

            command = (
                [ 'bowtie2', 
                    '--threads', str(cores),
                    '--rg-id', '1',
                    '--rg', 'SM:'+working.name,                    
                    ] + 
                self.bowtie_options + 
                [ '-x', reference.get_bowtie_index_prefix() ]
                )
            commands = [ ]
            if ones:
                commands.append(command + [ '-1', ','.join(ones), '-2', ','.join(twos) ])
            if singles:
                commands.append(command + [ '-U', ','.join(singles) ])
            
            temp_bam_name = temp/'temp.bam'

            with io.pipe_to(
                     ['samtools', 'view', '-S', '-b', '-'],
                     stdout=open(temp_bam_name,'wb'),
                     stderr=log_file
                     ) as f:
                header_sent = False
                for command in commands:
                    self.log.log('Running:\n' + ' '.join(command) + '\n')            
                    with io.pipe_from(
                        command,
                        stderr=log_file,
                        cores=cores
                        ) as f_out:
                        for line in f_out:
                            if not header_sent or not line.startswith('@'):
                                f.write(line)
                    header_sent = True

            #io.execute([
            #    'samtools', 'sort', '-n', temp_bam_name, working/'alignments'
            #    ])
            
            sam.sort_bam(temp_bam_name, working/'alignments', by_name=True, cores=self.cores)
            
        log_file.close()




