import logging
from Acquisition import aq_inner
from Products.Five import BrowserView
#from Products.LinguaPlone.interfaces import ITranslatable
from Products.statusmessages.interfaces import IStatusMessage

from cirb.organizations.content.organization import Organization, Association, Category
from cirb.organizations.browser.organizationssearch import renderCategoryButton
from cirb.organizations import organizationsMessageFactory as _
#from cirb.organizations.browser.interfaces import IOrganizationsLayer
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.saconfig import Session
from zope.interface import implements


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

    def new_language(self):
        if self.context.Language() == "fr":
            return 'nl'
        else:
            return 'fr'

    def has_completed(self, orga):
        html = ""
        if not orga.x or not orga.y:
            if not orga.address.street:
                html += "<span class='state-private'>No address</span>&nbsp;"
            else:
                html += "<span class='state-private'>Bad xy</span>"
        else:
            for decimal in orga.x.split('.'):
                if not decimal.isdecimal():
                    html += "<span class='state-private'>x</span>,&nbsp;"

            for decimal in orga.y.split('.'):
                if not decimal.isdecimal():
                    html += "<span class='state-private'>y</span>,&nbsp;"

        if not orga.person_incharge.second_name:
            html += "<span class='state-private'>Person in charge</span>,&nbsp;"

        if not orga.person_contact.second_name:
            html += "<span class='state-private'>Contact</span>,&nbsp;"

        if orga.person_contact.fax == ' ':
            html += "<span class='state-private'>Fax</span>,&nbsp;"

        if orga.website == ' ':
            html += "<span class='state-private'>Website</span>,&nbsp;"

        if not html:
            html = "<span class='state-published'>Ok</span>"
        return html


class DeleteView(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = Session()
        self.logger = logging.getLogger('cirb.organizations.browser.organizationsmanage')

    def delete(self):
        id_del_orga = self.request.form.get('del')
        if not delete_orga(self.session, id_del_orga):
            msg = _(u'no id fund for delete a organization')
            self.logger.info(msg)
            IStatusMessage(self.request).add(msg, type="error")
            return self.request.response.redirect("{0}/organizations_manage".format(self.context.absolute_url()))
        msg = _(u"The organization is deleted")
        IStatusMessage(self.request).add(msg, type="info")
        return self.request.response.redirect("{0}/organizations_manage".format(self.context.absolute_url()))


def delete_orga(session, id):
    assoc = []
    del_orga = session.query(Organization).get(id)
    if not del_orga:
        return False
    translated_orga = del_orga.get_translation()
    if translated_orga:
        assoc.append(translated_orga.organization_id)

    assoc.append(del_orga.organization_id)
    if len(assoc) > 1:
        delete_association(assoc)

    session.delete(del_orga)

    if translated_orga:
        session.delete(translated_orga)

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


class OView(BrowserView):
    implements(IImageScaleTraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('cirb.organizations.browser.organizationmanage')

    def get_categories(self):
        translations = []
        for cat in self.context.get_categories():
            translations.append(self.context.translate(cat))
        return ", ".join(translations)

    def input_categories(self):
        categories = []
        already_enseignement_formation = False
        for cat in self.context.get_categories_without_other():
            attr = getattr(Category, cat, False)
            if attr:
                if cat == "education" or cat == "training" or cat == "tutoring":
                    if not already_enseignement_formation:
                        categories.append(renderCategoryButton(self.context, _(u'enseignement_formation')))
                        already_enseignement_formation = True
                else:
                    categories.append(renderCategoryButton(self.context, cat))

        return categories

    def organizations_search_url(self):
        url = self.context.aq_parent.aq_parent.absolute_url()
        return "{0}/organizations_search".format(url)

    def translate_url(self):
        lang = self.context.Language()
        trans = [u'fr', u'nl']
        trans.remove(lang)
        if not self.context.hasTranslation(trans[0]):
            return "{0}/@@translate?newlanguage={1}".format(self.context.absolute_url(), trans[0])
        else:
            return False

    def has_image(self, image_name):
        named_image = getattr(self.context, image_name)
        if named_image.contentType:
            return True
        else:
            return False

