from z3c.saconfig import Session
from z3c.form import form, field, button
from plone.app.z3cform.layout import FormWrapper
#from collective.z3cform.wizard.wizard import WIZARD_SESSION_KEY

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cirb.organizations import organizationsMessageFactory as _
from cirb.organizations.content.organization import Organization, Category
from cirb.organizations.browser.interfaces import ISearch

import json
from sqlalchemy import func 
from plone.namedfile import file
from plone.namedfile.interfaces import IImageScaleTraversable
#import logging

from zope.interface import implements
SESSION_JSON = "search_json"
SESSION_SEARCH = "search_term"
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


class LetterButton(button.Button):
    pass
   

class CategoryButton(button.ImageButton):
    pass


class Search(form.Form):
    implements(IImageScaleTraversable)

    label = _(u'Organization search')
    ignoreContext = True
    fields = field.Fields(ISearch)

    template = ViewPageTemplateFile('templates/search.pt')
    results = []

    def search(self, search):
        session = Session()
        self.results = session.query(Organization).filter(func.lower(Organization.name).like('{0}'.format(search))).filter(Organization.language == self.context.Language()).all()
        if len(self.results) == 0:
            self.status = _(u"No organization found.")

    def get_categories(self):
        categories = [cat for cat in dir(Category) if not cat.startswith("_") and not cat[-3:] == "_id"]
        categories.remove('metadata')
        categories.remove('other')
        if 'organization' in categories:
            categories.remove('organization')
        return categories

    def update(self):
        for letter in ALPHABET:
            letterbutton = LetterButton(letter, unicode(letter))
            self.buttons = button.Buttons(self.buttons, letterbutton)
        self.handlers.addHandler(LetterButton, button.Handler(LetterButton, self.handleLettersButton))
        for cat in self.get_categories():
            categorybutton = CategoryButton(name=cat, title=unicode(cat),
                                            image=u"{0}.png".format(cat))
            self.buttons = button.Buttons(self.buttons, categorybutton)
        self.handlers.addHandler(CategoryButton, button.Handler(CategoryButton, self.handleCategoriesButton))
        super(Search, self).update()
    
    def handleLettersButton(self, form, action):
        self.search("{0}%".format(action.value.lower()))

    def handleCategoriesButton(self, form, action):
        print action.value
        session = Session()
        self.results = session.query(Organization).filter(Organization.category.has(getattr(Category, action.value) == True)).filter(Organization.language == self.context.Language()).all()
        if len(self.results) == 0:
            self.status = _(u"No organization found.")


    @button.buttonAndHandler(_(u'Search'))
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if not errors:
            input_content = data.get('search')
            if not input_content:
                search_text = "%"
            else:
                search_text = "%{0}%".format(input_content.lower())

            self.search(search_text)
    
    def get_results(self):
        if not 'SESSION' in self.request.keys():
            return None
        
        if SESSION_JSON in self.request.SESSION.keys():
            self.request.SESSION.delete(SESSION_JSON)
         
        if len(self.results) == 0:
            return None

        self.request.SESSION.set(SESSION_JSON, [{'orga': {'id':orga.organization_id, 'name':orga.name, 'x': orga.x, 'y':orga.y}} for orga in self.results])
        return self.results

    def folder_url(self):
        return self.context.absolute_url()

    def img(self, name, orga_id):
        session = Session()
        orga = session.query(Organization).get(orga_id)
        blob = getattr(orga, name)
        src = ""
        if blob:
            namedimage = file.NamedImage(data=blob) 
            extension = namedimage.contentType.split('/')[-1].lower()
            src = "{0}/org/{1}/@@images/{2}.{3}".format(self.context.absolute_url(), orga.organization_id, name, extension)
        return src
    

class SearchView(FormWrapper):
    form = Search
    
    def __call__(self):
        
        return super(SearchView, self).__call__()

    def json(self):
        ids = self.request.SESSION.get(SESSION_JSON)
        self.request.response.setHeader('Content-Type', "application/json")
        return list_to_json(ids)


def list_to_json(ids):
    return json.dumps(ids)
