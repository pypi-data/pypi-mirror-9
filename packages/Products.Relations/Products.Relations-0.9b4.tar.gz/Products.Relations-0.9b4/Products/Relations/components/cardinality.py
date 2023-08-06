# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.exceptions import ReferenceException

from Products.Relations import exception, interfaces, ruleset
from Products.Relations.config import *
from Products.Relations.schema import BaseSchemaWithInvisibleId

# Maybe some day we will get consistency on how implements works
# so that we don't have to do this - cwarner
from zope.interface import implements
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.interfaces import IExtensibleMetadata


class CardinalityConstraint(BaseContent, ruleset.RuleBase):
    """An IValidator and IReferenceLayerProvider that enforces cardinality."""
    implements(IBaseContent, IReferenceable, IExtensibleMetadata, interfaces.IValidator,
               interfaces.IReferenceLayerProvider)

    content_icon = 'cardinalityconstraint_icon.gif'

    def validateConnected(self, reference, chain):
        self._validate(reference, chain)

    def validateDisconnected(self, reference, chain):
        self._validate(reference, chain)

    def _validate(self, reference, chain):
        rc = getToolByName(self, REFERENCE_CATALOG)
        search_sources = rc(targetUID=reference.targetUID,
                    relationship=reference.relationship)
        search_targets = rc(sourceUID=reference.sourceUID,
                    relationship=reference.relationship)
        sources = len(search_sources)
        targets = len(search_targets)

        self.doValidate(sources, targets, reference, chain)

    def doValidate(self, sources, targets, reference, chain=None):
        rs = self.getRuleset()
        minsc = self.getMinSourceCardinality()
        maxsc = self.getMaxSourceCardinality()
        mintc = self.getMinTargetCardinality()
        maxtc = self.getMaxTargetCardinality()

        if minsc:
            if sources < minsc:
                raise exception.ValidationException(
                    "Too few sources (%s) for '%s'." % (sources, rs.Title()),
                    reference, chain)

        if maxsc:
            if sources > maxsc:
                raise exception.ValidationException(
                    "Too many sources (%s) for '%s'." % (sources, rs.Title()),
                    reference, chain)

        # XXX: i18n
        if mintc:
            if targets < mintc:
                raise exception.ValidationException(
                    "Too few targets (%s) for '%s'." % (targets, rs.Title()),
                    reference, chain)

        if maxtc:
            if targets > maxtc:
                raise exception.ValidationException(
                    "Too many targets (%s) for '%s'." % (targets, rs.Title()),
                    reference, chain)

    def provideReferenceLayer(self, reference): # IReferenceLayerProvider
        return CardinalityReferenceLayer(self.getRuleset(), self)
    
    # AT implementation    
    schema = BaseSchemaWithInvisibleId + Schema((
        IntegerField('minSourceCardinality',
                     widget=IntegerWidget(label='Minimum Source Cardinality',
                                         label_msgid='label_relation_minsrccardinality',
                                         description="Information about minimum source cardinality",
                                         description_msgid='help_relation_minsrccardinality',
                                         i18n_domain='Relations',),),
        IntegerField('maxSourceCardinality',
                     widget=IntegerWidget(label='Maximum Source Cardinality',
                                         label_msgid='label_relation_maxsrccardinality',
                                         description="Information about maximum source cardinality",
                                         description_msgid='help_relation_maxsrccardinality',
                                         i18n_domain='Relations',),),
        IntegerField('minTargetCardinality',
                     widget=IntegerWidget(label='Minimum Target Cardinality',
                                         label_msgid='label_relation_mintargcardinality',
                                         description="Information about minimum target cardinality",
                                         description_msgid='help_relation_mintargcardinality',
                                         i18n_domain='Relations',),),
        IntegerField('maxTargetCardinality',
                     widget=IntegerWidget(label='Maximum Target Cardinality',
                                         label_msgid='label_relation_mintargcardinality',
                                         description="Information about maximum target cardinality",
                                         description_msgid='help_relation_mintargcardinality',
                                         i18n_domain='Relations',),),
        ))
    portal_type = 'Cardinality Constraint'

registerType(CardinalityConstraint, PROJECTNAME)


class CardinalityReferenceLayer:
    implements(interfaces.IReferenceLayerProvider,)

    def __init__(self, ruleset, cc):
        self.ruleset = ruleset
        self.component = cc # cardinality constraint

    def beforeSourceDeleteInformTarget(self, reference):
        rc = getToolByName(self.ruleset, REFERENCE_CATALOG)
        search_sources = rc(targetUID=reference.targetUID,
                    relationship=self.ruleset.getId())
        search_targets = rc(sourceUID=reference.sourceUID,
                    relationship=self.ruleset.getId())
        sources = len(search_sources) - 1
        targets = len(search_targets)

        try:
            self.component.doValidate(sources, targets, reference)
        except exception.ValidationException, e:
            raise ReferenceException, e

    def beforeTargetDeleteInformSource(self, reference):
        rc = getToolByName(self.ruleset, REFERENCE_CATALOG)
        search_sources = rc(targetUID=reference.targetUID,
                    relationship=self.ruleset.getId())
        search_targets = rc(sourceUID=reference.sourceUID,
                    relationship=self.ruleset.getId())
        sources = len(search_sources)
        targets = len(search_targets) - 1

        try:
            self.component.doValidate(sources, targets, reference)
        except exception.ValidationException, e:
            raise ReferenceException, e
