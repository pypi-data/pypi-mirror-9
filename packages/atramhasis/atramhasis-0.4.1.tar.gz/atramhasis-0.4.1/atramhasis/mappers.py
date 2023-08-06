# -*- coding: utf-8 -*-
'''
Module containing mapping functions used by Atramhasis.
'''

from skosprovider_sqlalchemy.models import Label, Note, Concept, Thing, Collection, Match, MatchType
from sqlalchemy.orm.exc import NoResultFound


def map_concept(concept, concept_json, skos_manager):
    '''
    Map a concept from json to the database.

    :param skosprovider_sqlalchemy.models.Thing concept: A concept or 
        collection as known to the database.
    :param dict concept_json: A dict representing the json sent to our REST 
        service.
    :param skos_manager: A skos_manager to acces db operations
    :returns: The :class:`skosprovider_sqlalchemy.models.Thing` enhanced 
        with the information from the json object.
    '''
    concept.type = concept_json.get('type', None)
    if concept.type in ('concept', 'collection'):
        concept.labels[:] = []
        labels = concept_json.get('labels', [])
        for l in labels:
            label = Label(label=l.get('label', ''), labeltype_id=l.get('type', ''), language_id=l.get('language', ''))
            concept.labels.append(label)
        concept.notes[:] = []
        notes = concept_json.get('notes', [])
        for n in notes:
            note = Note(note=n.get('note', ''), notetype_id=n.get('type', ''), language_id=n.get('language', ''))
            concept.notes.append(note)

        concept.member_of.clear()
        member_of = concept_json.get('member_of', [])
        for memberof in member_of:
            try:
                memberof_collection = skos_manager.get_thing(
                    concept_id=memberof['id'],
                    conceptscheme_id=concept.conceptscheme_id)
            except NoResultFound:
                memberof_collection = Collection(concept_id=memberof['id'], conceptscheme_id=concept.conceptscheme_id)
            concept.member_of.add(memberof_collection)

        if concept.type == 'concept':
            concept.related_concepts.clear()
            related = concept_json.get('related', [])
            for related in related:
                try:
                    related_concept = skos_manager.get_thing(
                        concept_id=related['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    related_concept = Concept(concept_id=related['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.related_concepts.add(related_concept)
            concept.narrower_concepts.clear()

            concept.broader_concepts.clear()
            broader = concept_json.get('broader', [])
            for broader in broader:
                try:
                    broader_concept = skos_manager.get_thing(
                        concept_id=broader['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    broader_concept = Concept(concept_id=broader['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.broader_concepts.add(broader_concept)
            narrower = concept_json.get('narrower', [])
            for narrower in narrower:
                try:
                    narrower_concept = skos_manager.get_thing(
                        concept_id=narrower['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    narrower_concept = Concept(concept_id=narrower['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.narrower_concepts.add(narrower_concept)

            matches = []
            matchdict = concept_json.get('matches', {})
            for type in matchdict:
                db_type = type + "Match"
                matchtype = skos_manager.get_match_type(db_type)
                for uri in matchdict[type]:
                    concept_id = concept_json.get('id', -1)
                    try:
                        match = skos_manager.get_match(uri=uri, matchtype_id=matchtype.name,
                                                       concept_id=concept_id)
                    except NoResultFound:
                        match = Match()
                        match.matchtype = matchtype
                        match.uri = uri
                    matches.append(match)
            concept.matches = matches

            concept.narrower_collections.clear()
            narrower_collections = concept_json.get('subordinate_arrays', [])
            for narrower in narrower_collections:
                try:
                    narrower_collection = skos_manager.get_thing(
                        concept_id=narrower['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    narrower_collection = Collection(concept_id=narrower['id'],
                                                     conceptscheme_id=concept.conceptscheme_id)
                concept.narrower_collections.add(narrower_collection)

        if concept.type == 'collection':
            concept.members.clear()
            members = concept_json.get('members', [])
            for member in members:
                try:
                    member_concept = skos_manager.get_thing(
                        concept_id=member['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    member_concept = Concept(concept_id=member['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.members.add(member_concept)

            concept.broader_concepts.clear()
            broader_concepts = concept_json.get('superordinates', [])
            for broader in broader_concepts:
                try:
                    broader_concept = skos_manager.get_thing(
                        concept_id=broader['id'],
                        conceptscheme_id=concept.conceptscheme_id)
                except NoResultFound:
                    broader_concept = Concept(concept_id=broader['id'], conceptscheme_id=concept.conceptscheme_id)
                concept.broader_concepts.add(broader_concept)

    return concept
