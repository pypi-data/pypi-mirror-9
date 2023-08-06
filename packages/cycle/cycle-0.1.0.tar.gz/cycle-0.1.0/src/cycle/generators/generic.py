# import std libs
import os
from os import path
from pkg_resources import resource_filename, resource_listdir, resource_isdir, resource_exists
import re
# import third party libs
# import local libs
from cycle.meta import __title__ as pkgname
from cycle.utils import format_json, get_template_renderer


class GenericGeneratorException(Exception):
    pass


class GenericGenerator(object):
    '''
    To be written...
    '''
    
    @staticmethod
    def template_base(template):
        return resource_filename(pkgname, os.path.join('data/prototypes',template))
    
    @staticmethod
    def template_exists(template):
        # verify template is available as pkgdata
        return os.path.isdir(GenericGenerator.template_base(template))
    
    @staticmethod
    def generate(target_dir, metadata, template):
        if not GenericGenerator.template_exists(template):
            raise IOError('Template %s not found' % template)
        
        template_base = GenericGenerator.template_base(template)
        tmp_metadata = {}
        tmp_metadata.update(metadata)
        for key in metadata.keys():
            tmp_metadata['++%s++' % key] = metadata[key]
        
        regex_meta = re.compile("(%s)" % "|".join(map(re.escape, tmp_metadata.keys())))
        tree = []
        for root, dirs, files in os.walk(template_base):
            for name in dirs:
                tree.append(os.path.join(root, name))
            for name in files:
                tree.append(os.path.join(root, name))
        
        if path.exists(target_dir):
            raise IOError('Path % already exists' % target_dir)
        os.mkdir(target_dir)
        for resource in tree:
            rel_resource = resource.replace(template_base + os.path.sep, '')
            if rel_resource in ('wizard.json'):
                continue
            rendered_filename = regex_meta.sub(lambda mo: tmp_metadata[mo.string[mo.start():mo.end()]], rel_resource)
            print rendered_filename
            if os.path.isdir(resource):
                os.mkdir(os.path.join(target_dir, rendered_filename))
            else:
                data = open(resource, 'r').read()
                f_name, f_ext = path.splitext(rendered_filename)
                if f_ext in ('.tmpl'):
                    rendered_filename = f_name
                    template = get_template_renderer(data)
                    content = template.render(metadata)
                else:
                    content = data
                with open(os.path.join(target_dir, rendered_filename), 'w') as fh:
                    fh.write(content)
        # FIXME: general object to string fix required
        metadata['datetime_created'] = str(metadata['datetime_created'])
        metadata_file = os.path.join(target_dir, 'metadata.json')
        with open(metadata_file, 'w') as fh:
            fh.write(format_json(metadata))
