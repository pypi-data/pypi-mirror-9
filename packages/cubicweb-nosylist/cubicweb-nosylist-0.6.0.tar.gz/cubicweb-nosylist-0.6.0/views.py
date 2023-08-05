"""nosy list views

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.registry import objectify_predicate
from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import tags, utils
from cubicweb.predicates import (relation_possible, authenticated_user,
                                 is_instance, one_line_rset,
                                 match_user_groups, logged_user_in_rset,
                                 match_kwargs)
from cubicweb.view import EntityView, StartupView
from cubicweb.web import component, action, stdmsgs
from cubicweb.web import formfields as ff, formwidgets  as fw
from cubicweb.web.views import basecontrollers, forms, uicfg
from cubicweb.web.views.ajaxcontroller import ajaxfunc


_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('*', 'interested_in', '*'), 'hidden')
_pvs.tag_object_of(('*', 'interested_in', '*'), 'hidden')
_pvs.tag_object_of(('*', 'nosy_list', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'nosy_list', '*'), 'hidden')

_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'nosy_list', '*'), 'main', 'hidden')
_afs.tag_object_of(('*', 'nosy_list', '*'), 'main', 'hidden')
_afs.tag_subject_of(('*', 'interested_in', '*'), 'main', 'hidden')
_afs.tag_object_of(('*', 'interested_in', '*'), 'main', 'hidden')


class NotificationComponent(component.EntityCtxComponent):
    """component to control explicit registration for notification on an entity
    (eg interested_in relation)"""
    __regid__ = 'notification'
    __select__ = (component.EntityCtxComponent.__select__ &
                  relation_possible('interested_in', 'object', 'CWUser',
                                    action='add'))
    context = 'ctxtoolbar'

    def render(self, w):
        req = self._cw
        user = req.user
        entity = self.entity
        req.add_css('cubicweb.pictograms.css')
        req.add_js('cubes.nosylist.js')
        if not user.cw_adapt_to('IEmailable').get_email():
            title = req._('You can not register to be notified about changes '
                          'for this %s until you configure your email address.'
                          ) % entity.dc_type()
            icon = 'icon-attention'
            url = user.absolute_url(vid='edition')
            text = ''
            btn_style = ''
        else:
            icon = 'icon-mail'
            if (has_user_interest(req, user, entity)
                or user_in_nosy_list(req, user, entity)):
                title = req._('Click here if you don\'t want to be notified anymore'
                              ' for this %s') % entity.dc_type()
                text = req._('Unwatch')
                btn_style = 'active notificationComponent'
            else:
                # user isn't registered
                title = req._('Click here to be notified about changes for this %s'
                              ) % entity.dc_type()
                text = req._('Watch')
                btn_style = 'notificationComponent'
            url = '#'
        w(u'<a href="%s" class="toolbarButton %s btn btn-default %s" '
           'title="%s" data-eid="%s">%s</a>' % (
            xml_escape(url), xml_escape(icon), xml_escape(btn_style),
            xml_escape(title), entity.eid, xml_escape(text),
            ))

def has_user_interest(cnx, user, entity):
    """return true if the user is currently interested in the entity"""
    return bool(cnx.execute(
        'Any X WHERE U interested_in X, U eid %(u)s, X eid %(x)s',
        {'u': user.eid, 'x': entity.eid}))

def user_in_nosy_list(cnx, user, entity):
    """return true if the user is in the nosy list for the entity"""
    return bool(cnx.execute(
        'Any X WHERE X nosy_list U, U eid %(u)s, X eid %(x)s',
        {'u': user.eid, 'x': entity.eid}))


class ManageNotificationsAction(action.Action):
    """link to the notification management page (in the user drop down menu)"""
    __regid__ = 'usermenu_notifications_mgmt'
    __select__ = authenticated_user()

    title = _('notifications')
    category = 'useractions'
    order = 11
    icon = 'icon-mail'

    def url(self):
        return self._cw.user.absolute_url(vid='notifications')


class CWUserManageNotificationsAction(action.Action):
    """link to the notification management page (in the action box of user
    primary view)
    """
    __regid__ = 'actionsbox_notifications_mgmt'
    __select__ = (is_instance('CWUser') & one_line_rset()
                  & match_user_groups('owners', 'managers'))

    title = _('notifications')
    category = 'moreactions'

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='notifications')


class DeleteNotificationView(EntityView):
    """view used internally by the user notifications management table"""

    __regid__ = 'delete_notif'

    @objectify_predicate
    def check_rset_shape(cls, req, rset=None, row=None, **kwargs):
        if not rset:
            return 0
        rowdesc = rset.description[row or 0]
        # suppose target entity in column 2, and permission has been checked by
        # parent view
        if rowdesc[0] == 'CWUser' and len(rowdesc) == 3:
            return 1
        return 0

    __select__ = check_rset_shape()

    def cell_call(self, row, col, ueid=None):
        req = self._cw
        req.add_js('cubes.nosylist.js')
        user = self.cw_rset.get_entity(row, 0)
        entity = self.cw_rset.get_entity(row, 2)
        if user.eid == req.user.eid:
            msg = req._(u"Click here if you don't want to receive anymore "
                        "notification for this %(etype)s") % {
            'etype': entity.dc_type()}
        else:
            msg = req._(u"Click here if you don't want %(login)s to receive "
                        "anymore notification for this %(etype)s") % {
            'login': user.login,
            'etype': entity.dc_type()}
        self.w(u'[<a title="%s" href="javascript:removeRelation(\'interested_in\', %s, %s)">-</a>]' \
               % (msg, user.eid, entity.eid))


class CWUserManageNotificationsView(StartupView):
    __regid__ = 'notifications'
    __select__ = (one_line_rset() &
                  (match_user_groups('users') & logged_user_in_rset())
                  |
                  (match_user_groups('managers') & is_instance('CWUser'))
                  )

    @property
    def title(self):
        if len(self.cw_rset) == 1:
            user = self.cw_rset.get_entity(0, 0)
            return self._cw._('notifications management of %s') % user.name()
        return self._cw._('notifications management')

    def cell_call(self, row, col):
        req = self._cw
        user = self.cw_rset.get_entity(row, col)
        rset = req.execute('Any U,T,X ORDERBY T WHERE X is T,U interested_in X,'
                           'U eid %(x)s', {'x': user.eid})
        self.w(u'<h1>%s</h1>' % xml_escape(self.title))
        if rset:
            if user.eid == req.user.eid:
                msg = req._(u"You're registered to receive email notification "
                            "for the following entities:")
            else:
                msg = req._(u'%s is registered to receive email notification '
                            'for the following entities:') % user.login
            self.w(u'<div>%s</div>' % msg)
            self.wview('table', rset, mainindex=2, cellvids={0: 'delete_notif'},
                       headers=[None, req._('type'), req._('entity')])
        else:
            if user.eid == req.user.eid:
                msg = req._(u'You are currently not registered to receive '
                            'email notification for any type of entities.')
            else:
                msg = req._(u'%s is currently not registered to receive '
                            'email notification for any type of entities.') \
                            % user.login
            self.w(u'<div>%s</div>' % msg)


class INosyListManageNotificationsAction(CWUserManageNotificationsAction):
    __select__ = (match_user_groups('managers') & one_line_rset() &
                  relation_possible('nosy_list', 'subject', 'CWUser', action='add'))


class OneLineUserInterestedInView(EntityView):
    __select__ = is_instance('CWUser') & match_kwargs('related_entity')
    __regid__ = 'oneline_user_interested_in'

    def cell_call(self, row, col, related_entity=None):
        self._cw.add_js('cubes.nosylist.js')
        user = self.cw_rset.get_entity(row, col)
        msg = self._cw._(u"Click here if you don't want %(login)s to receive "
                         "anymore notification for this %(etype)s") % {
            'login': user.login,
            'etype': related_entity.dc_type()}
        self.w(u'[<a title="%s" href="javascript:%s">-</a>] '
               % (msg, self.deletejs(user.eid, related_entity.eid)))
        user.view('outofcontext', w=self.w)

    def deletejs(self, ueid, eeid):
        return u"removeRelation('interested_in', %s, %s)" % (ueid, eeid)


class OneLineUserNosyListView(OneLineUserInterestedInView):
    __regid__ = 'oneline_user_nosy_list'

    def deletejs(self, ueid, eeid):
        return u"removeRelation('nosy_list', %s, %s)" % (eeid, ueid)



class INosyListManageNotificationsView(EntityView):
    __regid__ = 'notifications'
    __select__ = (match_user_groups('managers') & one_line_rset() &
                  relation_possible('nosy_list', 'subject', 'CWUser', action='add'))


    @property
    def title(self):
        if len(self.cw_rset) == 1:
            entity = self.cw_rset.get_entity(0, 0)
            return self._cw._('notifications management for %s') % entity.dc_title()
        return self._cw._('notifications management')

    def cell_call(self, row, col, **kwargs):
        req = self._cw
        req.add_js(('cubes.nosylist.js', 'cubicweb.widgets.js',))
        req.add_css('cubes.nosylist.css')
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div id="%s%s">' % (self.__regid__, entity.eid))
        self.w(u'<h1>%s</h1>' % xml_escape(self.title))
        if 'interested_in' in entity.e_schema.objrels:
            iirset = entity.related('interested_in', 'object')
            nlrql = 'Any U WHERE X nosy_list U, X eid %(x)s, NOT U interested_in X'
        else:
            iirset = None
            nlrql = 'Any U WHERE X nosy_list U, X eid %(x)s'
        nlrset = req.execute(nlrql, {'x': entity.eid})
        if not iirset and not nlrset:
            self.w(u'<div>%s</div>' %
                   self._cw._(u'No users registered to receive notifications.'))
        else:
            if iirset is not None:
                self.w(u'<h4>%s:</h4>' %
                    self._cw._(u'interested_in_object').capitalize())
                if iirset:
                    self.wview('oneline_user_interested_in', iirset,
                               related_entity=entity)
                    self.w(u'<br/>')
                form = self._cw.vreg['forms'].select(
                    'interested_in_form', self._cw, entity=entity,
                    __redirectpath=entity.rest_path(),
                    __redirectparams='vid=notifications')
                form.render(w=self.w, main_form_title='', table_class='add_user')
                self.w(u'<br/>')
            if nlrset:
                self.w(u'<h4>%s:</h4>' % self._cw._(u'nosy_list').capitalize())
                self.wview('oneline_user_nosy_list', nlrset,
                           related_entity=entity)
        self.w(u'</div>')


class INosyListAutoCompletionWidget(fw.AutoCompletionWidget):
    def _get_url(self, entity, field):
        fname = self.autocomplete_initfunc
        return entity._cw.build_url('json', fname=fname, mode='remote',
                                    pageid=entity._cw.pageid, arg=entity.eid)

    def _render(self, form, field, renderer):
        entity = form.edited_entity
        domid = field.dom_id(form).replace(':', r'\\:')
        data = self.autocomplete_initfunc(form, field)
        form._cw.add_onload(u'$("#%s").cwautocomplete(%s, %s);'
                            % (domid, utils.json_dumps(data),
                               utils.json_dumps(self.autocomplete_settings)))
        values = self.values(form, field)
        inputs = [tags.input(name=field.input_name(form, self.suffix),
                             type='hidden', value=value)
                  for value in values if value]
        attrs = self.attributes(form, field)
        inputs.append(tags.input(name=field.input_name(form, self.suffix),
                                 type=self.type, value='', **attrs))
        return u'\n'.join(inputs)


def not_interested_in_users(form, field):
    """return users not interested in an entity"""
    req = form._cw
    eid = form.edited_entity.eid
    rql = ('Any U,F,S,L ORDERBY F,S,L WHERE U is CWUser, U firstname F, U surname S, U login L, '
           'NOT U interested_in X, X eid %(x)s')
    return [(user.eid, user.name())
            for user in req.execute(rql, {'x' : eid}).entities()]


class InterestedInForm(forms.EntityFieldsForm):
    __regid__ = 'interested_in_form'
    __select__ = (match_user_groups('managers') &
                  relation_possible('interested_in', 'object', 'CWUser',
                                    action='add'))

    cwtarget = 'eformframe'
    form_buttons = [fw.SubmitButton(stdmsgs.BUTTON_OK)]

    interested_in = ff.RelationField(label=_('Add a user'), role='object',
                                     widget=INosyListAutoCompletionWidget(
                                         autocomplete_initfunc=not_interested_in_users,
                                         # XXX doesn't work with cw 3.10.7
                                         autocomplete_settings={'limit': 20}),
                                     eidparam=True)
    @property
    def action(self):
        return self._cw.build_url('validateform')

@ajaxfunc(output_type='json')
def toggle_nosylist(self, eid):
    req = self._cw
    user = req.user
    entity = req.entity_from_eid(eid)
    msg = req._('You are no longer registered for this %s') % entity.dc_type()
    if has_user_interest(req, user, entity):
        # user is explicitly registered
        rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
    elif user_in_nosy_list(req, user, entity):
        # user is implicitly registered
        rql = 'DELETE X nosy_list U WHERE U eid %(u)s, X eid %(x)s'
    else:
        # user isn't registered
        rql = 'SET U interested_in X WHERE U eid %(u)s, X eid %(x)s'
        msg = req._('You are now registered for this %s') % entity.dc_type()
    req.execute(rql, {'u': user.eid, 'x': eid})
    return msg


@monkeypatch(basecontrollers.JSonController)
def js_remove_relation(self, rtype, seid, oeid):
    self._cw.execute('DELETE S %s O WHERE S eid %%(s)s, O eid %%(o)s' % rtype,
                     {'s': seid, 'o': oeid})
