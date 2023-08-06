
import random

from django.contrib.auth.models import AnonymousUser, User
from django.db import models
from django.template import Node, Library, TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _

from tendenci.addons.corporate_memberships.models import CorpMembership
from tendenci.core.base.template_tags import ListNode, parse_tag_kwargs
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.base.utils import tcurrency


register = Library()


@register.inclusion_tag(
        "corporate_memberships/applications/render_corpmembership_field.html")
def render_corpmembership_field(request, field_obj,
                                corpprofile_form,
                            corpmembership_form):
    if field_obj.field_type == "section_break":
        field = None
    else:
        field_name = field_obj.field_name
        if field_name in corpprofile_form.field_names \
                and not field_obj.display_only:
            field = corpprofile_form[field_name]
        elif field_name in corpmembership_form.field_names \
                and not field_obj.display_only:
            field = corpmembership_form[field_name]
        else:
            field = None

    return {'request': request, 'field_obj': field_obj,
            'field': field}


@register.simple_tag
def individual_pricing_desp(corp_membership):
    """
    Return the description of pricing for the individual memberships
    joining under this corp_membership.
    """
    description = ''
    if corp_membership:
        corporate_type = corp_membership.corporate_membership_type
        membership_type = corporate_type.membership_type
        admin_fee = membership_type.admin_fee
        if not admin_fee:
            admin_fee = 0

        if not (membership_type.price + admin_fee):
            membership_price = 'free'
        else:
            membership_price = tcurrency(membership_type.price)
            if membership_type.admin_fee:
                membership_price = '%s + %s' % (
                                    membership_price,
                                    tcurrency(membership_type.admin_fee))

        threshold = corporate_type.apply_threshold
        threshold_limit = corporate_type.individual_threshold
        threshold_price = corporate_type.individual_threshold_price
        if not threshold_price:
            threshold_price = 'free'
        else:
            threshold_price = tcurrency(threshold_price)

        if threshold and threshold_limit > 0:
            description += 'first %d %s, ' % (
                                    threshold_limit,
                                    threshold_price
                                    )
            description += 'then %s ' % membership_price
        else:
            description += '%s ' % membership_price
    return description



@register.inclusion_tag("corporate_memberships/nav.html", takes_context=True)
def corpmemb_nav(context, user, corp_memb=None):
    context.update({
        'nav_object': corp_memb,
        "user": user
    })
    return context


@register.inclusion_tag("corporate_memberships/options.html", takes_context=True)
def corpmemb_options(context, user, corp_memb):
    context.update({
        "opt_object": corp_memb,
        "user": user
    })
    return context


@register.inclusion_tag("corporate_memberships/applications/search_form.html", takes_context=True)
def corpmembership_search(context):
    return context


class AllowViewCorpNode(Node):
    def __init__(self, corp_memb, user, context_var):
        self.corp_memb = corp_memb
        self.user = user
        self.var_name = context_var

    def resolve(self, var, context):
        return Variable(var).resolve(context)

    def render(self, context):
        corp_memb = self.resolve(self.corp_memb, context)
        user = self.resolve(self.user, context)

        boo = corp_memb.allow_view_by(user)

        if self.var_name:
            context[self.var_name] = boo
            return ""
        else:
            return boo

@register.tag
def allow_view_corp(parser, token):
    """
        {% allow_view_corp corp_memb user as allow_view %}
    """
    bits  = token.split_contents()

    try: corp_memb = bits[1]
    except: corp_memb = None

    try: user = bits[2]
    except: user = None

    if len(bits) >= 5:
        context_var = bits[4]
    else:
        context_var = None
    return AllowViewCorpNode(corp_memb, user, context_var=context_var)


class AllowEditCorpNode(Node):
    def __init__(self, corp_memb, user, context_var):
        self.corp_memb = corp_memb
        self.user = user
        self.var_name = context_var

    def resolve(self, var, context):
        return Variable(var).resolve(context)

    def render(self, context):
        corp_memb = self.resolve(self.corp_memb, context)
        user = self.resolve(self.user, context)

        boo = corp_memb.allow_edit_by(user)

        if self.var_name:
            context[self.var_name] = boo
            return ""
        else:
            return boo

@register.tag
def allow_edit_corp(parser, token):
    """
        {% allow_edit_corp corp_memb user as allow_edit %}
    """
    bits  = token.split_contents()

    try: corp_memb = bits[1]
    except: corp_memb = None

    try: user = bits[2]
    except: user = None

    if len(bits) >= 5:
        context_var = bits[4]
    else:
        context_var = None
    return AllowEditCorpNode(corp_memb, user, context_var=context_var)


class ListCorpMembershipNode(ListNode):
    model = CorpMembership

    def __init__(self, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

        if not self.model:
            raise AttributeError(_('Model attribute must be set'))
        if not issubclass(self.model, models.Model):
            raise AttributeError(_('Model attribute must derive from Model'))
        if not hasattr(self.model.objects, 'search'):
            raise AttributeError(_('Model.objects does not have a search method'))

    def render(self, context):
        tags = u''
        query = u''
        user = AnonymousUser()
        limit = 3
        order = '-join_dt'

        randomize = False

        allow_anonymous_search = get_setting('module',
                                         'corporate_memberships',
                                         'anonymoussearchcorporatemembers')
        allow_member_search = get_setting('module',
                                         'corporate_memberships',
                                         'membersearchcorporatemembers')
        allow_member_search = allow_member_search or allow_anonymous_search

        if 'random' in self.kwargs:
            randomize = bool(self.kwargs['random'])

        if 'user' in self.kwargs:
            try:
                user = Variable(self.kwargs['user'])
                user = user.resolve(context)
            except:
                user = self.kwargs['user']
                if user == "anon" or user == "anonymous":
                    user = AnonymousUser()
        else:
            # check the context for an already existing user
            # and see if it is really a user object
            if 'user' in context:
                if isinstance(context['user'], User):
                    user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']

        limit = int(limit)

        if 'query' in self.kwargs:
            try:
                query = Variable(self.kwargs['query'])
                query = query.resolve(context)
            except:
                query = self.kwargs['query']  # context string

        if 'order' in self.kwargs:
            try:
                order = Variable(self.kwargs['order'])
                order = order.resolve(context)
            except:
                order = self.kwargs['order']

        items = CorpMembership.objects.all()
        if user.is_authenticated():
            if not user.profile.is_superuser:
                if user.profile.is_member and allow_member_search:
                    items = items.distinct()
                else:
                    items = items.none()
        else:
            if not allow_anonymous_search:
                items = items.none()

        objects = []

        # if order is not specified it sorts by relevance
        if order:
            items = items.order_by(order)

        if randomize:
            objects = [item for item in random.sample(items, items.count())][:limit]
        else:
            objects = [item for item in items[:limit]]

        context[self.context_var] = objects
        return ""


@register.tag
def list_corporate_memberships(parser, token):
    """
    Used to pull a list of :model:`corporate_memberships.CorpMembership` items.

    Usage::

        {% list_corporate_memberships as [varname] [options] %}

    Be sure the [varname] has a specific name like ``corpmembership_sidebar`` or
    ``corpmembership_list``. Options can be used as [option]=[value]. Wrap text values
    in quotes like ``query="cool"``. Options include:

        ``limit``
           The number of items that are shown. **Default: 3**
        ``order``
           The order of the items. **Default: Newest Approved**
        ``user``
           Specify a user to only show public items to all. **Default: Viewing user**
        ``query``
           The text to search for items. Will not affect order.
        ``random``
           Use this with a value of true to randomize the items included.

    Example::

        {% list_corporate_memberships as corpmembership_list limit=5 %}
        {% for corpmembership in corpmembership_list %}
            {{ corpmembership.corp_profile.name }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[2]

    if len(bits) < 3:
        message = "'%s' tag requires at least 2 parameters" % bits[0]
        raise TemplateSyntaxError(_(message))

    if bits[1] != "as":
        message = "'%s' second argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(_(message))

    kwargs = parse_tag_kwargs(bits)

    if 'order' not in kwargs:
        kwargs['order'] = '-join_dt'

    return ListCorpMembershipNode(context_var, *args, **kwargs)
