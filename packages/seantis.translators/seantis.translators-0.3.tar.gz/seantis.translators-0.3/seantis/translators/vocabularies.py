from five import grok
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from seantis.translators import _


class GenderVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value='M', title=_(u'Male')),
            SimpleTerm(value='F', title=_(u'Female'))
        ])

grok.global_utility(
    GenderVocabulary, name='seantis.translators.vocabularies.Gender'
)


class PermitVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value='B', title=_(u'B')),
            SimpleTerm(value='C', title=_(u'C')),
            SimpleTerm(value='Ci', title=_(u'Ci')),
            SimpleTerm(value='G', title=_(u'G')),
            SimpleTerm(value='L', title=_(u'L')),
            SimpleTerm(value='F', title=_(u'F')),
            SimpleTerm(value='N', title=_(u'N')),
            SimpleTerm(value='S', title=_(u'S')),
        ])

grok.global_utility(
    PermitVocabulary, name='seantis.translators.vocabularies.Permit'
)


class YesNoUnknownVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value=True, title=_(u'Yes')),
            SimpleTerm(value=False, title=_(u'No')),
            SimpleTerm(value=None, title=_(u'Unknown')),
        ])

grok.global_utility(
    YesNoUnknownVocabulary,
    name='seantis.translators.vocabularies.YesNoUnknown'
)


class CertificatesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([
            SimpleTerm(value='ZHAW', title=_(u'ZHAW Certificate')),
            SimpleTerm(value='OGZH', title=_(u'OGZH Certificate')),
        ])

grok.global_utility(
    CertificatesVocabulary,
    name='seantis.translators.vocabularies.Certificates'
)
