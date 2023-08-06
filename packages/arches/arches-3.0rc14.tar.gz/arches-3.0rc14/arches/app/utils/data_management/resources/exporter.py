import os
import csv
import zipfile
import datetime
import json
import glob
from django.conf import settings
from formats.csvfile import CsvWriter 
from django.http import HttpResponse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class ResourceExporter(object):

    def __init__(self, file_format):
        self.filetypes = {'csv': CsvWriter}
        self.format = file_format
        self.writer = self.filetypes[file_format]()
        self.export_temp_directory = os.path.join(settings.PACKAGE_ROOT, 'source_data', 'business_data', 'tmp_export_files')

    def export(self, resources, zip=False):
        configs = self.read_export_configs()
        result = self.writer.write_resources(resources, configs, self.export_temp_directory)
        return result

    def read_export_configs(self):
        '''
        Reads the export configuration file and adds an array for records to store property data
        '''
        configs = settings.EXPORT_CONFIG
        if configs != '':
            resource_export_configs = json.load(open(settings.EXPORT_CONFIG, 'r'))
            configs = resource_export_configs[self.format]
            for key, val in configs['RESOURCE_TYPES'].iteritems():
                configs['RESOURCE_TYPES'][key]['records'] = []
        
        return configs

    def zip_response(self, files_for_export, zip_file_name=None, file_type=None):
        '''
        Given a list of export file names, zips up all the files with those names and returns and http response.
        '''
        buffer = StringIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip:
            for f in files_for_export:
                f['outputfile'].seek(0)
                zip.writestr(f['name'], f['outputfile'].read())

        zip.close()
        buffer.flush()
        zip_stream = buffer.getvalue()
        buffer.close()

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename=' + zip_file_name
        response['Content-length'] = str(len(zip_stream))
        response['Content-Type'] = 'application/zip'
        response.write(zip_stream)
        return response




