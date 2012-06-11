from Acquisition import aq_inner
from Products.Five import BrowserView
#from Products.LinguaPlone.interfaces import ITranslatable
from Products.statusmessages.interfaces import IStatusMessage

from z3c.saconfig import Session
from cirb.organizations.content.organization import Organization, Association
from cirb.organizations import organizationsMessageFactory as _
#from cirb.organizations.browser.interfaces import IOrganizationsLayer
import transaction
import logging
#from zope.interface import implements


class ManageView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = Session()

    def manage(self):
        results = self.session.query(Organization).filter(Organization.language == self.context.Language()).all()
        return results

    def translate_url(self):
        context = aq_inner(self.context)
        if context.getLanguage() == 'fr':
            view = context.getTranslation('nl')
            absolute_url = "{0}/organizations_form?set_language=nl".format(view.absolute_url())
        else:
            view = context.getTranslation('fr')
            absolute_url = "{0}/organizations_form?set_language=fr".format(view.absolute_url())
            return absolute_url


class DeleteView(BrowserView):
    def __init__(self, context, request, session=''):
        self.context = context
        self.request = request
        self.session = Session()
        self.logger = logging.getLogger('cirb.organizations.browser.organizationsmanage')

    def delete(self):
        id_del_orga = self.request.form.get('del')
        if not delete_orga(self.session, id_del_orga):
            msg = u'no id fund for delete a organization'
            self.logger.info(msg)
            IStatusMessage(self.request).add(msg, type="error")
            return self.request.response.redirect(self.context.absolute_url())
        msg = _(u"The organization {0} is deleted".format(self.session.query(Organization).get(id_del_orga)))
        IStatusMessage(self.request).add(msg, type="info")
        return self.request.response.redirect(self.context.absolute_url())


def delete_orga(session, id):
    assoc = []
    del_orga = session.query(Organization).get(id)
    if not del_orga:
        return False
    translated_orga = del_orga.get_translation()
    if translated_orga:
        assoc.append(translated_orga.organization_id)
        session.delete(translated_orga)

    assoc.append(del_orga.organization_id)
    session.delete(del_orga)
    transaction.commit()
    if len(assoc) > 1:
        delete_association(assoc)

    return True


def delete_association(ids):
    if not len(ids) == 2:
        logger = logging.getLogger('cirb.organizations.browser.organizationsmanage')
        logger.error("Try to delete an association, but there are not 2 ids.")
        return
    session = Session()
    query1 = session.query(Association).filter(Association.canonical_id == ids[0]).filter(Association.translated_id == ids[1]).filter(Association.association_type == 'lang')
    query2 = session.query(Association).filter(Association.canonical_id == ids[1]).filter(Association.translated_id == ids[0]).filter(Association.association_type == 'lang')
    query = query1.union(query2)
    assoc = query.all()
    if len(assoc) > 1:
        logger.error("There are {0} association with ids {1} and {2}").format(len(assoc), ids[0], ids[1])
        session.delete(query.first())

from zope.interface import implements
from plone.namedfile.interfaces import IImageScaleTraversable

class OView(BrowserView):
    implements(IImageScaleTraversable)

    def __call__(self, *args, **kwargs):
        lang = self.request.get("set_language")
        if lang:
            redirect = self.context.getTranslation(lang)
            import pdb; pdb.set_trace()
            return self.request.RESPONSE.redirect(redirect)

        return super(OView,self).__call__(args, kwargs)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('cirb.organizations.browser.organizationmanage')
