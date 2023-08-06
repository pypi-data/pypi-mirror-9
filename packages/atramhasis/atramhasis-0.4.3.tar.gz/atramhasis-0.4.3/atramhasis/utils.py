# -*- coding: utf-8 -*-
'''
Module containing utility functions used by Atramhasis.
'''
from pyramid.httpexceptions import HTTPMethodNotAllowed

from skosprovider.skos import Concept, Collection, Label, Note, ConceptScheme
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider


def from_thing(thing):
    '''
        Map a :class:`skosprovider_sqlalchemy.models.Thing` to a 
        :class:`skosprovider.skos.Concept` or
        a :class:`skosprovider.skos.Collection`, depending on the type.

        :param skosprovider_sqlalchemy.models.Thing thing: Thing to map.
        :rtype: :class:`~skosprovider.skos.Concept` or 
            :class:`~skosprovider.skos.Collection`.
        '''
    if thing.type and thing.type == 'collection':
        return Collection(
            id=thing.concept_id,
            uri=thing.uri,
            concept_scheme=ConceptScheme(thing.conceptscheme.uri),
            labels=[
                Label(l.label, l.labeltype_id, l.language_id)
                for l in thing.labels
            ],
            members=[member.concept_id for member in thing.members] if hasattr(thing, 'members') else [],
            member_of=[c.concept_id for c in thing.member_of],
            superordinates=[broader_concept.concept_id for broader_concept in thing.broader_concepts]
        )
    else:
        matches = {}
        for m in thing.matches:
            key = m.matchtype.name[:m.matchtype.name.find('Match')]
            if not key in matches:
                matches[key] = []
            matches[key].append(m.uri)
        return Concept(
            id=thing.concept_id,
            uri=thing.uri,
            concept_scheme=ConceptScheme(thing.conceptscheme.uri),
            labels=[
                Label(l.label, l.labeltype_id, l.language_id)
                for l in thing.labels
            ],
            notes=[
                Note(n.note, n.notetype_id, n.language_id)
                for n in thing.notes
            ],
            broader=[c.concept_id for c in thing.broader_concepts],
            narrower=[c.concept_id for c in thing.narrower_concepts],
            related=[c.concept_id for c in thing.related_concepts],
            member_of=[c.concept_id for c in thing.member_of],
            subordinate_arrays=[narrower_collection.concept_id for narrower_collection in thing.narrower_collections],
            matches=matches,
        )


def internal_providers_only(fn):
    '''
    aspect oriented way to check if provider is internal when calling the decorated function

    :param fn: the decorated function
    :return: around advice
    :raises pyramid.httpexceptions.HTTPMethodNotAllowed: when provider is not internal
    '''
    def advice(parent_object, *args, **kw):

        if isinstance(parent_object.provider, SQLAlchemyProvider) and \
                not 'external' in parent_object.provider.get_metadata()['subject']:
            return fn(parent_object, *args, **kw)
        else:
            raise HTTPMethodNotAllowed()

    return advice
