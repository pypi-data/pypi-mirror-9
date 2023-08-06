from AccessControl.unauthorized import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.fullview import msgFact as _
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


class IFullViewPortlet(IPortletDataProvider):

    content = schema.Choice(
        title=_(u"Content Item"),
        source=SearchableTextSourceBinder(
            {},
            default_query='path:'
        ),
        required=True
    )

    show_title = schema.Bool(
        title=_(u"label_show_title", default=u"Show Content Title"),
        description=_(
            u"help_show_title",
            default=u"Show the content title."),
        default=True,
        required=False
    )

    link_title = schema.Bool(
        title=_(u"label_link_title", default=u"Link Content Title"),
        description=_(
            u"help_link_title",
            default=u"Link the content title with the content."),
        default=True,
        required=False
    )

    show_content = schema.Bool(
        title=_(u"label_show_content", default=u"Show content"),
        description=_(
            u"help_show_content",
            default=u"Show the content. You might want to not show it, if you "
                    "only want to show title and description and link to the "
                    "content."),
        default=True,
        required=False
    )


class Assignment(base.Assignment):
    implements(IFullViewPortlet)
    content = None
    show_title = True
    link_title = True
    show_content = True

    def __init__(self, content, show_title, link_title, show_content):
        self.content = content
        self.show_title = show_title
        self.link_title = link_title
        self.show_content = show_content

    @property
    def title(self):
        """Title of add view in portlet management screen."""
        return _(u"Full View Portlet")


class Renderer(base.Renderer):

    @property
    @memoize
    def content_obj(self):
        item = self.data.content
        if item:
            portal_url = getToolByName(self.context, 'portal_url')
            portal_path = portal_url.getPortalPath()
            try:
                item = self.context.restrictedTraverse(
                    '{0}{1}'.format(portal_path, item), None
                )
            except Unauthorized:
                item = None
        return item

    @property
    def title(self):
        return self.content_obj.title

    @property
    def url(self):
        url = None
        item = self.content_obj
        if item:
            url = item.absolute_url()
        return url

    render = ViewPageTemplateFile('fullview.pt')


class AddForm(base.AddForm):
    form_fields = form.Fields(IFullViewPortlet)
    label = _(u"Add Full View Portlet")
    description = _(u"Show a content item as full view.")

    def create(self, data):
        return Assignment(
            content=data.get('content', None),
            show_title=data.get('show_title', True),
            link_title=data.get('link_title', True),
            show_content=data.get('show_content', True)
        )


class EditForm(base.EditForm):
    form_fields = form.Fields(IFullViewPortlet)
    label = _(u"Edit Full View Portlet")
    description = _(u"Show a content item as full view.")


class FullViewItem(BrowserView):

    def __init__(self, context, request):
        super(FullViewItem, self).__init__(context, request)
        self.item_type = self.context.portal_type

    @property
    def default_view(self):
        context = self.context
        item_layout = context.getLayout()
        default_view = context.restrictedTraverse(item_layout)
        return default_view

    @property
    def item_macros(self):
        default_view = self.default_view
        if IBrowserView.providedBy(default_view):
            # IBrowserView
            return default_view.index.macros
        else:
            # FSPageTemplate
            return default_view.macros

    @property
    def item_url(self):
        context = self.context
        url = context.absolute_url()
        props = getToolByName(context, 'portal_properties')
        use_view_action = props.site_properties.typesUseViewActionInListings
        return self.item_type in use_view_action and '%s/view' % url or url
