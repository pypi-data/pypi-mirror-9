from bingads.manifest import BULK_FORMAT_VERSION
from bingads.bulk import DownloadFileType

from bingads.internal.bulk.bulk_object_factory import _BulkObjectFactory
from bingads.internal.bulk.csv_writer import _CsvWriter
from bingads.internal.bulk.csv_headers import _CsvHeaders
from bingads.internal.bulk.row_values import _RowValues
from bingads.internal.bulk.string_table import _StringTable


class _BulkObjectWriter():
    def __init__(self, file_path, file_format):
        self._file_path = file_path

        if file_format == DownloadFileType.csv:
            self._delimiter = ','
        elif file_format == DownloadFileType.tsv:
            self._delimiter = '\t'
        else:
            raise ValueError('Invalid file_format provided: {0}'.format(file_format))

        self._csv_writer = _CsvWriter(self.file_path, delimiter=self._delimiter)
        self._csv_writer.__enter__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._csv_writer.__exit__(exc_type, exc_val, exc_tb)

    def close(self):
        self.__exit__(None, None, None)

    def write_file_metadata(self):
        self.write_headers()
        self.write_format_version()

    def write_headers(self):
        self._csv_writer.writerow(_CsvHeaders.HEADERS)

    def write_format_version(self):
        version_row = _RowValues()
        version_row[_StringTable.Type] = _StringTable.SemanticVersion
        version_row[_StringTable.Name] = BULK_FORMAT_VERSION
        self._csv_writer.writerow(version_row.columns)

    def write_object_row(self, bulk_object, exclude_readonly_data=False):
        values = _RowValues()
        bulk_object.write_to_row_values(values, exclude_readonly_data)
        values[_StringTable.Type] = _BulkObjectFactory.get_bulk_row_type(bulk_object)
        self._csv_writer.writerow(values.columns)

    @property
    def file_path(self):
        return self._file_path

    @property
    def delimiter(self):
        return self._delimiter
