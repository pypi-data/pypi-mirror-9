from five import grok
from zope.schema.interfaces import IVocabularyFactory
from plone.principalsource.source import PrincipalSourceBinder, PrincipalSource


# By default, we list groups and we can search for users in ajax
class PrincipalSource(PrincipalSource):
    def search_principals(self, groups_first=False, **kw):
        if kw:
            results = self.acl_users.searchPrincipals(groups_first=True, **kw)
        else:
            # if no kw, we have been called from source __iter__ because
            # of Chosen widget populate_select attribute is set to True
            results = self.acl_users.searchGroups()
        return [r for r in results if r.get('groupid', None) != 'AuthenticatedUsers']

    @property
    def _search(self):
        if self.users and self.groups:
#            return self.acl_users.searchPrincipals
            return self.search_principals
        elif self.users:
            return self.acl_users.searchUsers
        elif self.groups:
            return self.acl_users.searchGroups


class PrincipalSourceBinder(PrincipalSourceBinder):

    def __call__(self, context):
        return PrincipalSource(context, self.users, self.groups)


class PrincipalsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary for principals"""
    grok.name('dms.principals')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        principals = PrincipalSourceBinder(users=True, groups=True)
        return principals(context)


class TreatingGroupsVocabulary(grok.GlobalUtility):
    """Vocabulary for treating groups"""
    grok.name('collective.dms.basecontent.treating_groups')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        principals = PrincipalSourceBinder(users=True, groups=True)
#        principals = queryUtility(IVocabularyFactory, name=u'plone.principalsource.Principals')
        return principals(context)


class RecipientGroupsVocabulary(grok.GlobalUtility):
    """Vocabulary for recipient groups"""
    grok.name('collective.dms.basecontent.recipient_groups')
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
#        principals = queryUtility(IVocabularyFactory, name=u'plone.principalsource.Principals')
        principals = PrincipalSourceBinder(users=True, groups=True)
        return principals(context)
