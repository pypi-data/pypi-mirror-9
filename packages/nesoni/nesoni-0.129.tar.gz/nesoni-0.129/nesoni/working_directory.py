
import os, re

from nesoni import grace, io, config, reference_directory, selection

class Working(io.Workspace):
    def set_reference(self, path):
        self.update_param(reference=self.path_as_relative_path(path))

    def setup_reference(self, filenames, bowtie=False):
        if len(filenames) == 1 and os.path.isdir(filenames[0]):
            self.set_reference(filenames[0])
            return
        
        path = self / 'reference'
        reference_directory.Make_reference(path, filenames=filenames, bowtie=bowtie).run()
        self.set_reference(path)

    def get_reference(self):
        if 'reference' in self.param:
            path = self.relative_path_as_path(self.param['reference'])
        else:
            path = self.working_dir
        
        return reference_directory.Reference(path, must_exist=True)

    def get_filtered_bam(self):
        filename = self / 'alignments_filtered.bam'
        assert os.path.exists(filename), 'Alignments in %s haven\'t been filtered, need to run "nesoni filter:" or "nesoni consensus:".' % self.name
        return filename

    def get_filtered_sorted_bam(self):
        filename = self / 'alignments_filtered_sorted.bam'
        assert os.path.exists(filename), 'Alignments in %s haven\'t been filtered, need to run "nesoni filter:" or "nesoni consensus:".' % self.name
        return filename

    def get_tags(self):
        return [self.name]+self.param.get('tags',[])

    def matches(self, expression):
        return selection.matches(expression, self.get_tags())
    
    def get_depths(self):
        #if os.path.exists(self/'depths.store'):
        #    from . import storage
        #    return storage.Storage(self/'depths.store').data
        #else:
        return self.get_object('depths.pickle.gz')



@config.help("""\
Label a working directory with a list of tags.

(The list is stored in the file <workding_dir>/parameters.)
""")
@config.Main_section('tags', 'Tags to give working directory.\n(Any existing tags are discarded.)')
class Tag(config.Action_with_working_dir):
    tags = [ ]
    
    _workspace_class = Working
    
    def run(self):
        for tag in self.tags:
            assert not tag.startswith('-'), 'Tags shouldn\'t start with "-".'
            for char in '+:, \t\'\"':
                assert char not in tag, 'Tags shouldn\'t contain "'+char+'".'
        
        workspace = self.get_workspace()
        workspace.update_param(tags=self.tags)




