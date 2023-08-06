import csv
import codecs

from six import StringIO, text_type, PY2
from pyramid.renderers import JSON
from skosprovider_sqlalchemy.models import Collection, Concept, Label, Note, Language
from pyramid_skosprovider.utils import concept_adapter as skos_concept_adapter
from pyramid_skosprovider.utils import collection_adapter as skos_collection_adapter
from pyramid_skosprovider.utils import label_adapter as skos_label_adapter
from pyramid_skosprovider.utils import note_adapter as skos_note_adapter
from skosprovider.skos import Concept as SkosConcept
from skosprovider.skos import Collection as SkosCollection
from skosprovider.skos import Label as SkosLabel
from skosprovider.skos import Note as SkosNote


class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.stream = f
        self.writer = csv.writer(self.stream, dialect=dialect, **kwds)
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):  # pragma: no cover
        #some ugly code to support python2
        if PY2:
            encoded_row = []
            for s in row:
                if isinstance(s, text_type):
                    encoded_row.append(self.encoder.encode(s))
                else:
                    encoded_row.append(s)
            self.writer.writerow(encoded_row)
        else:
            self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CSVRenderer(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        f_out = StringIO()
        writer = UnicodeWriter(f_out, delimiter=',', quoting=csv.QUOTE_ALL)

        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        resp.content_type = 'text/csv'
        resp.content_disposition = 'attachment;filename="' + value['filename'] + '.csv"'
        return f_out.getvalue()


json_renderer_verbose = JSON()


def concept_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Concept` to json with verbose relations.

    :param skosprovider_sqlalchemy.models.Concept obj: The concept to be rendered.
    :rtype: :class:`dict`
    '''
    matches = {}
    for m in obj.matches:
        key = m.matchtype.name[:m.matchtype.name.find('Match')]
        if not key in matches:
            matches[key] = []
        matches[key].append(m.uri)
    return {
        'id': obj.concept_id,
        'type': obj.type,
        'uri': obj.uri,
        'label': obj.label().label if obj.label() else None,
        'labels': obj.labels,
        'notes': obj.notes,
        'broader': [map_relation(c) for c in obj.broader_concepts],
        'narrower': [map_relation(c) for c in obj.narrower_concepts],
        'related': [map_relation(c) for c in obj.related_concepts],
        'member_of': [map_relation(c) for c in obj.member_of],
        'subordinate_arrays': [map_relation(c) for c in obj.narrower_collections],
        'matches': matches
    }


def collection_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Collection` to json with verbose relations.

    :param skosprovider_sqlalchemy.models.Collection obj: The collection to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'id': obj.concept_id,
        'type': obj.type,
        'uri': obj.uri,
        'label': obj.label().label if obj.label() else None,
        'labels': obj.labels,
        'members': [map_relation(c) for c in obj.members],
        'member_of': [map_relation(c) for c in obj.member_of],
        'superordinates': [map_relation(c) for c in obj.broader_concepts]
    }


def map_relation(thing):
    #Map thing in a relation, leaving out the relations (to avoid circular dependencies)
    return {
        'id': thing.concept_id,
        'type': thing.type,
        'uri': thing.uri,
        'label': thing.label().label if thing.label() else None,
        'labels': thing.labels
    }


def label_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Label` to json.

    :param skosprovider_sqlalchemy.models.Label obj: The label to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'label': obj.label,
        'type': obj.labeltype_id,
        'language': obj.language_id
    }


def note_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Note` to json.

    :param skosprovider_sqlalchemy.models.Note obj: The note to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'note': obj.note,
        'type': obj.notetype_id,
        'language': obj.language_id
    }


def language_adaptor(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider_sqlalchemy.models.Language` to json.

    :param skosprovider_sqlalchemy.models.Language obj: The language to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'id': obj.id,
        'name': obj.name
    }

json_renderer_verbose.add_adapter(Concept, concept_adapter)
json_renderer_verbose.add_adapter(Collection, collection_adapter)
json_renderer_verbose.add_adapter(Label, label_adapter)
json_renderer_verbose.add_adapter(Note, note_adapter)
json_renderer_verbose.add_adapter(Language, language_adaptor)
json_renderer_verbose.add_adapter(SkosConcept, skos_concept_adapter)
json_renderer_verbose.add_adapter(SkosCollection, skos_collection_adapter)
json_renderer_verbose.add_adapter(SkosLabel, skos_label_adapter)
json_renderer_verbose.add_adapter(SkosNote, skos_note_adapter)
