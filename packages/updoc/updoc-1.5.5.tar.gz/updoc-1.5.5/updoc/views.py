# -*- coding: utf-8 -*-
"""Here are defined Python functions of views.
Views are binded to URLs in :mod:`.urls`.
"""
import datetime
import json
import mimetypes
import zipfile

import codecs
from django.contrib.syndication.views import Feed
from django.core.files.uploadedfile import UploadedFile
import os
import re
import stat
import tarfile
import tempfile
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import F, Count, Q
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseNotModified, StreamingHttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.static import was_modified_since
from elasticsearch.exceptions import ConnectionError as ESError
import markdown

from updoc.djangoproject.settings import strip_split
from updoc.indexation import search_archive
from updoc.models import UploadDoc, Keyword, LastDocs, RssRoot, RssItem, RewrittenUrl, ProxyfiedHost
from updoc.process import process_new_file
from updoc.utils import list_directory


replace_cache = {'until': None, 're': None, 'validity': datetime.timedelta(0, 600), 'rep_dict': None, }

__author__ = "flanker"


class FileUploadForm(forms.Form):
    """Upload form"""
    file = forms.FileField(label=_('file'), max_length=255)


class DocSearchForm(forms.Form):
    """Upload form"""
    search = forms.CharField(max_length=255)
    doc_id = forms.IntegerField(widget=forms.widgets.HiddenInput(), required=False)


class UploadForm(forms.Form):
    """Upload form"""
    uid = forms.CharField(widget=forms.widgets.HiddenInput())
    id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    name = forms.CharField(label=_('Name'), max_length=240)
    keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False)


class UploadApiForm(forms.Form):
    filename = forms.CharField(label=_('Filename'), max_length=240)
    name = forms.CharField(label=_('Name'), max_length=240)
    keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False)


class UrlForm(forms.Form):
    """form for new URL to rewrite"""
    src = forms.CharField(label=_('URL to rewrite'), max_length=255)
    dst = forms.CharField(label=_('New URL'), max_length=255, required=False)


@csrf_exempt
@login_required(login_url='/login')
@permission_required('updoc.add_uploaddoc')
def upload_doc(request):
    form = FileUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        raise PermissionDenied
    uploaded_file = request.FILES['file']
    obj = process_new_file(uploaded_file, request)
    basename = os.path.basename(uploaded_file.name).rpartition('.')[0]
    if basename[-4:] == '.tar':
        basename = basename[:-4]
    # if hasattr(uploaded_file, 'temporary_file_path'):
    #     os.remove(uploaded_file.temporary_file_path())

    class FilledUploadForm(forms.Form):
        """Upload form"""
        uid = forms.CharField(widget=forms.widgets.HiddenInput(), initial=obj.uid)
        id = forms.IntegerField(widget=forms.widgets.HiddenInput(), initial=obj.id)
        name = forms.CharField(label=_('Name'), max_length=240, initial=basename,
                               widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter a name'), }))
        keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False,
                                   widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter some keywords'),
                                                                         }))

    form = FilledUploadForm()
    template_values = {'form': form, }
    return render_to_response('upload_doc.html', template_values, RequestContext(request))


@login_required(login_url='/login')
def upload(request):
    """Index view, displaying and processing a form."""
    user = request.user if request.user.is_authenticated() else None
    if request.method == 'POST':
        form = UploadForm(request.POST)
        if form.is_valid():  # pylint: disable=E1101
            messages.info(request, _('File successfully uploaded'))
            obj = get_object_or_404(UploadDoc, uid=form.cleaned_data['uid'], id=form.cleaned_data['id'], user=user)
            obj.name = form.cleaned_data['name']
            for keyword in form.cleaned_data['keywords'].lower().split():
                obj.keywords.add(Keyword.get(keyword))
            obj.save()
            return HttpResponseRedirect(reverse('updoc.views.upload'))
        else:
            obj = get_object_or_404(UploadDoc, uid=form.cleaned_data['uid'], id=form.cleaned_data['id'], user=user)
            obj.delete()
            messages.error(request, _('Unable to upload this file'))
    else:
        form = FileUploadForm()
    template_values = {'form': form, 'title': _('Upload a new file'), 'root_host': settings.HOST}
    template_values.update(csrf(request))  # prevents cross-domain requests
    return render_to_response('upload.html', template_values, RequestContext(request))


DAY = datetime.timedelta(1)


def my_docs(request):
    user = request.user if request.user.is_authenticated() else None
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            RewrittenUrl(user=user, src=form.cleaned_data['src'], dst=form.cleaned_data['dst']).save()
            return redirect('updoc.views.my_docs')
    else:
        form = UrlForm()
    uploads = UploadDoc.objects.filter(user=user).order_by('-upload_time').select_related()
    rw_urls = RewrittenUrl.objects.filter(user=user).order_by('src')
    template_values = {'uploads': uploads, 'title': _('My documents'), 'rw_urls': rw_urls,
                       'rw_form': form, 'editable': True}
    return render_to_response('my_docs.html', template_values, RequestContext(request))


def delete_url(request, url_id):
    user = request.user if request.user.is_authenticated() else None
    obj = get_object_or_404(RewrittenUrl, id=url_id)
    if not request.user.is_superuser and obj.user != user:
        raise PermissionDenied
    name = obj.src
    try:
        obj.delete()
        messages.info(request, _('%(doc)s successfully deleted') % {'doc': name})
    except IOError:
        messages.error(request, _('Unable to delete %(doc)s ') % {'doc': name})
    return HttpResponseRedirect(reverse('updoc.views.my_docs'))


def delete_doc(request, doc_id):
    user = request.user if request.user.is_authenticated() else None
    obj = get_object_or_404(UploadDoc, id=doc_id)
    if not request.user.is_superuser and obj.user != user:
        raise PermissionDenied
    name = obj.name
    try:
        obj.delete()
        messages.info(request, _('%(doc)s successfully deleted') % {'doc': name})
    except IOError:
        messages.error(request, _('Unable to delete %(doc)s ') % {'doc': name})
    return HttpResponseRedirect(reverse('updoc.views.my_docs'))


@csrf_exempt
def edit_doc(request, doc_id):
    name = request.POST.get('name')
    keywords = request.POST.get('keywords')
    user = request.user if request.user.is_authenticated() else None
    obj = get_object_or_404(UploadDoc, id=doc_id)
    if not request.user.is_superuser and obj.user != user:
        raise PermissionDenied
    if name:
        if obj.name != name.strip():
            obj.name = name.strip()
        obj.save()
    if keywords is not None:
        obj.keywords.clear()
        for keyword in keywords.lower().split():
            if keyword:
                obj.keywords.add(Keyword.get(keyword))
        obj.save()
    return HttpResponse(json.dumps({'ok': True}), content_type='application/json')


range_re = re.compile(r'bytes=(\d+)-(\d+)')


def static_serve(request, path, document_root=None):
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    if document_root is None:
        document_root = settings.STATIC_ROOT
    filename = os.path.abspath(os.path.join(document_root, path))
    if not filename.startswith(document_root):
        raise Http404
    if settings.USE_XSENDFILE:
        return xsendfile(request, filename)
    return sendfile(request, filename)


def xsendfile(request, filename):
    response = HttpResponse()
    response['X-Sendfile'] = filename.encode('utf-8')
    return response


def sendfile(request, filename, allow_replace=False):
    # Respect the If-Modified-Since header.
    if not os.path.isfile(filename):
        raise Http404
    elif settings.USE_XSENDFILE:
        return xsendfile(request, filename)
    statobj = os.stat(filename)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    content_type = mimetypes.guess_type(filename)[0]
    extension = filename.rpartition('.')[2]
    if allow_replace and extension in ('js', 'html', 'css') and os.path.getsize(filename) < 100 * 1024:
        now = datetime.datetime.now()
        if replace_cache['re'] is None or replace_cache['until'] < now:
            replace_cache['until'] = now + replace_cache['validity']
            rep_dict = dict([(x.src, x.dst) for x in RewrittenUrl.objects.all()])
            replace_cache['rep_dict'] = rep_dict
            replace_cache['re'] = re.compile("|".join([re.escape(k) for k in rep_dict.keys()]), re.M)
        if replace_cache['rep_dict']:
            try:
                with codecs.open(filename, 'r') as out_fd:
                    content = out_fd.read()
                    content = replace_cache['re'].sub(lambda x: replace_cache['rep_dict'][x.group(0)], content)
                return HttpResponse(content, content_type=content_type)
            except UnicodeDecodeError:
                pass
    range_ = request.META.get('HTTP_RANGE', '')
    t = range_re.match(range_)
    size = os.path.getsize(filename)
    start = 0
    end = size - 1
    if t:
        start, end = int(t.group(1)), int(t.group(2))
    if end - start + 1 < size:
        obj = open(filename, 'rb')
        obj.seek(start)
        response = HttpResponse(obj.read(end - start + 1), content_type=content_type, status=206)
        response['Content-Range'] = 'bytes %d-%d/%d' % (start, end, size)
    else:
        obj = open(filename, 'rb')
        return StreamingHttpResponse(obj, content_type=content_type)
    response['Content-Length'] = end - start + 1
    return response


def compress_archive(request, doc_id, fmt='zip'):
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    tmp_file = tempfile.NamedTemporaryFile()
    doc = get_object_or_404(UploadDoc, id=doc_id)
    arc_root = slugify(doc.name)
    if fmt == 'zip':
        cmp_file = zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        for (root, dirnames, filenames) in os.walk(doc.path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
                cmp_file.write(full_path, arcname)
        content_type = 'application/zip'
    elif fmt in ('gz', 'bz2', 'xz'):
        cmp_file = tarfile.open(name=arc_root + '.tar.' + fmt, mode='w:' + fmt, fileobj=tmp_file)
        for filename in os.listdir(doc.path):
            full_path = os.path.join(doc.path, filename)
            arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
            cmp_file.add(full_path, arcname)
        content_type = 'application/x-tar'
    else:
        raise ValueError
    cmp_file.close()
    tmp_file.seek(0)
    response = StreamingHttpResponse(tmp_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % arc_root
    return response


def show_doc_alt(request, doc_id, path=''):
    return show_doc(request, doc_id, path=path)


def show_doc(request, doc_id, path=''):
    if request.user.is_anonymous() and not settings.PUBLIC_DOCS:
        raise Http404
    doc = get_object_or_404(UploadDoc, id=doc_id)
    root_path = doc.path
    full_path = os.path.join(root_path, path)
    if not full_path.startswith(root_path):
        raise Http404
    user = request.user if request.user.is_authenticated() else None
    checked, created = LastDocs.objects.get_or_create(user=user, doc=doc)
    use_auth = reverse('updoc.views.show_doc', kwargs={'doc_id': doc_id, 'path': path}) == request.path
    view = 'updoc.views.show_doc' if use_auth else 'updoc.views.show_doc_alt'
    if not created:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        LastDocs.objects.filter(user=user, doc=doc).update(count=F('count') + 1, last=now)
    editable = request.user.is_superuser or request.user == doc.user
    if not os.path.isfile(full_path):
        directory = list_directory(root_path, path, view, view_arg='path',
                                   view_kwargs={'doc_id': doc.id}, dir_view_name=view,
                                   dir_view_arg='path', dir_view_kwargs={'doc_id': doc.id}, show_files=True,
                                   show_dirs=True, show_parent=True, show_hidden=False)
        template_values = {'directory': directory, 'doc': doc, 'editable': editable, 'title': str(doc),
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()]), 'doc_id': doc_id, }
        return render_to_response('list_dir.html', template_values, RequestContext(request))
    if full_path.endswith('.md'):
        view_name = 'updoc.views.show_doc'
        if request.user.is_anonymous():
            view_name = 'updoc.views.show_doc_alt'
        path_components = [(reverse(view_name, kwargs={'doc_id': doc_id, 'path': ''}), _('root'))]
        components = path.split('/')
        for index_, comp in enumerate(components):
            p = '/'.join(components[0:index_ + 1])
            path_components.append((reverse(view_name, kwargs={'doc_id': doc_id, 'path': p}), comp))
        template_values = {'doc': doc, 'editable': editable, 'title': str(doc), 'path': path, 'paths': path_components,
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()]), 'doc_id': doc_id, }
        try:
            with open(full_path) as fd:
                content = fd.read()
            template_values['content'] = mark_safe(markdown.markdown(content))
            return render_to_response('markdown.html', template_values, RequestContext(request))
        except UnicodeDecodeError:
            pass
    return sendfile(request, full_path, allow_replace=True)


def show_favorite(request, root_id=None):
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
        roots = []
        favorites = []
        messages.info(request, _('You must be logged to see this page.'))
        current_root_name = _('Bookmarks')
        root_id = 0
    else:
        roots = list(RssRoot.objects.all().order_by('name'))
        if root_id is None and roots:
            root_id = roots[0].id
        elif not root_id:
            root_id = 0
        if root_id:
            current_root_name = get_object_or_404(RssRoot, id=root_id).name
        else:
            current_root_name = _('Bookmarks')
        favorites = RssItem.objects.filter(root__id=root_id).order_by('name')
    template_values = {'roots': roots, 'values': favorites, 'current_root_name': current_root_name,
                       'current_id': int(root_id)}
    return render_to_response('list_favorites.html', template_values, RequestContext(request))


def show_proxies(request):
    proxies = ProxyfiedHost.objects.exclude(host='').order_by('priority')
    defaults = '; '.join([x.proxy_str() for x in ProxyfiedHost.objects.filter(host='').order_by('priority')])
    if request.user.is_anonymous() and not settings.PUBLIC_PROXIES:
        proxies = []
        defaults = ''
    if not defaults:
        defaults = 'DIRECT'
    template_values = {'proxies': proxies, 'model': ProxyfiedHost, 'defaults': defaults}
    return render_to_response('proxy.pac', template_values, content_type='application/x-ns-proxy-autoconfig')


@csrf_exempt
def upload_api(request):
    user = request.user if request.user.is_authenticated() else None
    if user is None:
        # username = request.GET.get('username', '')
        # password = request.GET.get('password', '')
        # username = unquote(username)
        # password = unquote(password)
        # if username and password:
        #     users = get_user_model().objects.filter(username=username)[0:1]
        #     if not users:
        #         return HttpResponse(_('Invalid user %(u)s') % {'u': username}, status=401)
        #     user = users[0]
        #     if not user.check_password(password):
        #         return HttpResponse(_('Invalid password for user %(u)s') % {'u': username}, status=401)
        #     request.user = user
        # else:
        return HttpResponse(_('You must be logged to upload files.'), status=401)
    elif request.method != 'POST':
        return HttpResponse(_('Only POST requests are allowed.'), status=400)
    form = UploadApiForm(request.GET)
    if not form.is_valid():
        raise Http404
    # read the request and push it into a tmp file
    tmp_file = tempfile.TemporaryFile(mode='w+b')
    c = False
    chunk = request.read(32768)
    while chunk:
        tmp_file.write(chunk)
        c = True
        chunk = request.read(32768)
    tmp_file.flush()
    tmp_file.seek(0)
    if not c:
        return HttpResponse(_('Empty file. You must POST a valid file.'), status=400)
    # ok, we have the tmp file
    uploaded_file = UploadedFile(name=form.cleaned_data['filename'], file=tmp_file)

    existing_obj = None
    existing_objs = list(UploadDoc.objects.filter(user=user, name=form.cleaned_data['name'])[0:1])
    if existing_objs:
        existing_obj = existing_objs[0]
        existing_obj.clean_archive()
    try:
        obj = process_new_file(uploaded_file, request, obj=existing_obj)
        obj.name = form.cleaned_data['name']
        obj.save()
        for keyword in strip_split(form.cleaned_data['keywords'].lower()):
            obj.keywords.add(Keyword.get(keyword))
    except Exception as e:
        return HttpResponse(str(e), status=400)
    finally:
        tmp_file.close()
    return HttpResponse(_('File successfully uploaded and indexed.'), status=200)


def full_list(request):
    user = request.user if request.user.is_authenticated() else None
    search = DocSearchForm(request.GET)
    if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
        messages.info(request, _('You must be logged to see documentations.'))
        keywords_with_counts, recent_uploads, recent_checked = [], [], []
    else:
        recent_uploads = UploadDoc.objects.order_by('name')
        recent_checked = LastDocs.objects.filter(user=user).select_related().order_by('-last')[0:40]
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
        rss_roots = []
    else:
        rss_roots = RssRoot.objects.all().order_by('name')
    template_values = {'recent_checked': recent_checked, 'title': _('Updoc'), 'rss_roots': rss_roots,
                       'recent_uploads': recent_uploads, 'search': search, 'keywords': [],
                       'list_title': _('All documents'), }
    return render_to_response('index.html', template_values, RequestContext(request))


def index(request):
    """Index view, displaying and processing a form."""
    user = request.user if request.user.is_authenticated() else None
    search = DocSearchForm(request.GET)
    if search.is_valid():
        pattern = search.cleaned_data['search']
        doc_id = search.cleaned_data['doc_id'] or ''
        # ElasticSearch
        es_search = []
        es_total = 0
        if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
            messages.info(request, _('You must be logged to search across docs.'))
        else:
            try:
                es_search, es_total = search_archive(pattern, archive_id=doc_id)
            except ESError:
                messages.error(request, _('Unable to use indexed search.'))
        extra_obj = {}
        for obj in UploadDoc.objects.filter(id__in=set([x[0] for x in es_search])).only('id', 'name'):
            extra_obj[obj.id] = obj.name
        es_result = []
        for es in es_search:
            if es[0] not in extra_obj:
                continue
            es_result.append((extra_obj[es[0]], es[0], es[1]))
        es_result.sort(key=lambda x: x[1])
        es_data = {'results': es_result, 'total': es_total, }

        # classical search
        if not doc_id:
            docs = UploadDoc.objects.all()
            # list of UploadDoc.name, UploadDoc.id, path, UploadDoc.upload_time
            if len(pattern) > 3:
                docs = docs.filter(Q(name__icontains=pattern) | Q(keywords__value__icontains=pattern))
            else:
                docs = docs.filter(Q(name__iexact=pattern) | Q(keywords__value__iexact=pattern))
            docs = docs.distinct().select_related()
        else:
            docs = None
        template_values = {'uploads': docs, 'title': _('Search results'), 'rw_form': None,
                           'editable': False, 'es_data': es_data, 'doc_id': doc_id}
        return render_to_response('my_docs.html', template_values, RequestContext(request))
    if request.user.is_anonymous() and not settings.PUBLIC_INDEX:
        messages.info(request, _('You must be logged to see documentations.'))
        keywords_with_counts, recent_uploads, recent_checked = [], [], []
    else:
        keywords_with_counts = Keyword.objects.all().annotate(count=Count('uploaddoc')).filter(count__gt=0)\
            .order_by('-count')[0:15]
        recent_uploads = UploadDoc.objects.order_by('-upload_time')[0:10]
        recent_checked = LastDocs.objects.filter(user=user).select_related().order_by('-last')[0:20]
    if request.user.is_anonymous() and not settings.PUBLIC_BOOKMARKS:
        rss_roots = []
    else:
        rss_roots = RssRoot.objects.all().order_by('name')
    template_values = {'recent_checked': recent_checked, 'title': _('Updoc'), 'rss_roots': rss_roots,
                       'recent_uploads': recent_uploads, 'search': search, 'keywords': keywords_with_counts,
                       'list_title': _('Recent uploads'), }
    return render_to_response('index.html', template_values, RequestContext(request))


class KeywordFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request, kw):
        return get_object_or_404(Keyword, value=kw)

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        return obj.value

    # noinspection PyMethodMayBeStatic
    def link(self, obj):
        return reverse('updoc.views.index') + '?search=' + obj.value

    # noinspection PyMethodMayBeStatic
    def description(self, obj):
        return _("Documentations with keyword %(kw)s") % {'kw': obj.value}

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        pattern = obj.value
        if len(pattern) > 3:
            docs = UploadDoc.objects.filter(Q(name__icontains=pattern) | Q(keywords__value__icontains=pattern))
        else:
            docs = UploadDoc.objects.filter(Q(name__iexact=pattern) | Q(keywords__value__iexact=pattern))
        return docs.order_by('name')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return ''

    def item_link(self, item):
        return item.get_absolute_url(item.index)


class MostViewedFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request):
        user = request.user
        """:type user: django.contrib.auth.models.User"""
        if user.is_authenticated():
            return request.user
        return None

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is None:
            return _('Favorite documentations')
        return _('Documentations of %(n)s') % {'n': obj.username}

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def link(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return reverse('updoc.views.my_docs')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def description(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _("Most viewed documentations")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is not None:
            return LastDocs.objects.filter(user=obj).select_related().order_by('-count')[0:30]
        elif not settings.PUBLIC_INDEX or not settings.PUBLIC_DOCS:
            return []
        return LastDocs.objects.filter(user=None).select_related().order_by('-count')[0:30]

    def item_title(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.doc.name

    def item_description(self, item):
        """:type item: updoc.models.LastDocs"""
        return ''

    def item_link(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.doc.get_absolute_url(item.doc.index)


class LastDocsFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request):
        user = request.user
        """:type user: django.contrib.auth.models.User"""
        if user.is_authenticated():
            return request.user
        return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def title(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _('Last documentations')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def link(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is not None:
            return reverse('updoc.views.my_docs')
        return reverse('updoc.views.index')

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def description(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        return _("Most recent documentations")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        """:type obj: django.contrib.auth.models.User"""
        if obj is None and (not settings.PUBLIC_INDEX or not settings.PUBLIC_DOCS):
            return []
        return UploadDoc.objects.order_by('-upload_time')[0:30]

    def item_title(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.name

    def item_description(self, item):
        """:type item: updoc.models.LastDocs"""
        return ''

    def item_link(self, item):
        """:type item: updoc.models.LastDocs"""
        return item.get_absolute_url(item.index)


class RssFeed(Feed):

    # noinspection PyMethodOverriding
    def get_object(self, request, root_id):
        return get_object_or_404(RssRoot, pk=root_id)

    # noinspection PyMethodMayBeStatic
    def title(self, obj):
        return obj.name

    # noinspection PyMethodMayBeStatic
    def link(self, obj):
        return obj.get_absolute_url()

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def description(self, obj):
        return _("List of bookmarks URLs.")

    # noinspection PyMethodMayBeStatic
    def items(self, obj):
        return RssItem.objects.filter(root=obj).order_by('name')

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return ''

    def item_link(self, item):
        return item.url