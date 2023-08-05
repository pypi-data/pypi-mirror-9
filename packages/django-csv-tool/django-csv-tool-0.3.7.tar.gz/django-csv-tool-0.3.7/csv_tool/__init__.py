import csv

from six.moves import cStringIO
import codecs
from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import force_text


class CsvSkipException(Exception):
    pass


class CsvImportTool(object):
    model = None
    fields = []
    aliases = {}

    errors = []
    count = 0

    def register_aliases(self, name, aliases):
        for alias in aliases:
            self.aliases[alias] = name

    def get_or_create(self, values):
        return self.model.objects.create()

    def save_model(self, instance, values):
        instance.save()

    def finished(self, instance, values):
        pass

    def count_lines(self, f):
        for i, l in enumerate(f):
            pass
        return i + 1

    def import_from_file(self, file_object, starting_line=1, ending_line=None):
        self.count = 0
        self.errors = []
        headers = []

        # attempt to open in universal line ending mode
        if isinstance(file_object, InMemoryUploadedFile):
            file_object = file_object.read().splitlines()
            self.total = len(file_object)
        elif isinstance(file_object, File):
            file_object.open("rU")
            self.total = self.count_lines(file_object)
            file_object.seek(0)
        else:
            self.total = self.count_lines(file_object)
            file_object.seek(0)

        for idx, row in enumerate(csv.reader(file_object)):
            if idx == 0:
                for header in row:
                    header = header.lower().strip().replace(" ", "_")
                    headers.append(self.aliases.get(header, header))
            elif ending_line and idx > ending_line:
                break
            elif idx >= starting_line:
                for idx, value in enumerate(row):
                    row[idx] = value.strip()
                values = dict(zip(headers, row))

                # empty row
                if not values:
                    continue

                try:
                    instance = self.get_or_create(values)

                    # before save
                    for header in headers:
                        if header in self.fields:
                            func = self._import_property
                        else:
                            func = getattr(self, "import_%s" % header, None)

                        if func:
                            func(instance, values, header)

                    self.save_model(instance, values)

                    for header in headers:
                        func = getattr(self, "import_%s_after" % header, None)

                        if func:
                            func(instance, values, header)

                    self.finished(instance, values)
                    self.count_row(instance, values)
                except CsvSkipException:
                    pass
                except Exception as ex:
                    self.errors.append(str(ex))

    def count_row(self, instance, values):
        self.count += 1

    # import functions
    def _import_property(self, instance, values, name):
        setattr(instance, name, values.get(name))


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([force_text(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CsvExportTool(object):
    fields = ["id", "__unicode__"]

    def labels(self, headers):
        my_labels = []
        for header in headers:
            if isinstance(header, (list, tuple)):
                header = header[0]
            else:
                header = header.replace("_", " ").title()
            my_labels.append(header)
        return my_labels

    def get_headers(self):
        headers = []
        for field in self.fields:
            if "." in field:
                headers.append(field.rsplit(".", 1)[-1])
            else:
                headers.append(field)
        return headers

    def queryset_to_dict(self, queryset):
        self.errors = []

        rows = []

        # add headers
        headers = self.get_headers()
        rows.append(self.labels(headers))

        # add records
        for instance in queryset:
            rows.append(self.instance_to_dict(instance, headers=headers))

        return rows

    def instance_to_dict(self, instance, headers=None):
        if not headers:
            headers = self.labels(self.get_headers())
        return dict(zip(headers, self.instance_to_row(instance)))

    def instance_to_row(self, instance):
        row = []
        for field in self.fields:
            if isinstance(field, (list, tuple)):
                label = field[0]
                field = field[1]
            else:
                label = field
            attr = getattr(self, "export_%s" % field, None)
            if attr:
                attr = attr(instance, label)
            else:
                attr = self._export_dotted(instance, field)

            if attr:
                attr = (u"%s" % attr).strip()
            else:
                attr = ""
            row.append(attr)
        return row

    def exported(self, instance):
        pass

    def export(self, queryset):
        self.errors = []

        rows = []

        # add headers
        headers = self.get_headers()
        rows.append(self.labels(headers))

        # add records
        self.count = 0
        self.total = len(queryset)
        for instance in queryset:
            rows.append(self.instance_to_row(instance))
            self.count += 1
            self.exported(instance)

#         # clean out unicode:
#         from django.utils.encoding import smart_str
#         for i, row in enumerate(rows):
#             for j, cell in enumerate(row):
#                 row[j] = smart_str(cell)
#             rows[i] = row
        return rows

    def _export_dotted(self, instance, fieldname):
        attr = instance
        for bit in fieldname.split("."):
            try:
                attr = getattr(attr, bit, None)
                if not attr:
                    break
            except:
                attr = None
                break

        if callable(attr):
            attr = attr()

        return attr

    def save_file(self, queryset, fileh):
        writer = UnicodeWriter(fileh)
        writer.writerows(self.export(queryset))
