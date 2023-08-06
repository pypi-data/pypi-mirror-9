# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
import sys
import cgi
import json
import uuid
import shutil
import datetime
import importlib
import traceback
import logging

import pytz
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader, RequestContext
from django.template.defaultfilters import date
from django.shortcuts import render_to_response, get_object_or_404
from django.core import management
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError


from rest_framework import generics, views
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.authentication import (SessionAuthentication,
                                           BasicAuthentication)

from steelscript.common.timeutils import round_time
from steelscript.commands.steel import shell, ShellFailed
from steelscript.appfwk.apps.datasource.models import Job, Table
from steelscript.appfwk.apps.datasource.serializers import TableSerializer
from steelscript.appfwk.apps.datasource.forms import TableFieldForm
from steelscript.appfwk.apps.devices.models import Device
from steelscript.appfwk.apps.geolocation.models import Location, LocationIP
from steelscript.appfwk.apps.preferences.models import (SystemSettings,
                                                        PortalUser)
from steelscript.appfwk.apps.report.models import (Report, Section, Widget,
                                                   WidgetJob, WidgetAuthToken)
from steelscript.appfwk.apps.report.serializers import ReportSerializer, \
    WidgetSerializer
from steelscript.appfwk.apps.report.utils import create_debug_zipfile
from steelscript.appfwk.apps.report.forms import (ReportEditorForm,
                                                  CopyReportForm)
from steelscript.appfwk.project.middleware import URLTokenAuthentication


logger = logging.getLogger(__name__)


@api_view(['GET'])
def reload_config(request, namespace=None, report_slug=None):
    """ Reload all reports or one specific report
    """
    if namespace and report_slug:
        logger.debug("Reloading %s report" % report_slug)
        management.call_command('reload',
                                namespace=namespace,
                                report_name=report_slug)
    elif namespace:
        logger.debug("Reloading reports under namespace %s" % namespace)
        management.call_command('reload', namespace=namespace)
    else:
        logger.debug("Reloading all reports")
        management.call_command('reload')

    # prioritize next param over HTTP_REFERERs
    if hasattr(request, 'QUERY_PARAMS') and 'next' in request.QUERY_PARAMS:
        return HttpResponseRedirect(request.QUERY_PARAMS['next'])
    elif ('HTTP_REFERER' in request.META and
          'reload' not in request.META['HTTP_REFERER']):
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect(reverse('report-view-root'))


def download_debug(request):
    """ Create zipfile and send it back to client
    """
    # XXX when we implement RBAC this method needs to be ADMIN-level only

    zipfile = create_debug_zipfile()
    wrapper = FileWrapper(file(zipfile))
    response = HttpResponse(wrapper, content_type='application/zip')
    zipname = os.path.basename(zipfile)
    response['Content-Disposition'] = 'attachment; filename=%s' % zipname
    response['Content-Length'] = os.stat(zipfile).st_size
    return response


def rm_file(filepath):
    """ Remove a file, ignoring errors that may occur

    :param filepath: file name with path
    """
    try:
        os.remove(filepath)
    except:
        pass


class GenericReportView(views.APIView):
    def get_media_params(self, request):
        """ Implement this method in subclasses to compute the values of
            the template, criteria and expand_tables template params.
        """

        raise NotImplementedError('get_media_params() must be implemented in '
                                  ' subclass.')

    def render_html(self, report, request, namespace, report_slug, isprint):
        """ Render HTML response
        """

        logging.debug('Received request for report page: %s' % report_slug)

        if not request.user.profile_seen:
            # only redirect if first login
            return HttpResponseRedirect(reverse('preferences')+'?next=/report')

        devices = Device.objects.all()
        if len(devices) == 0:
            # redirect if no devices defined
            return HttpResponseRedirect(reverse('device-list'))

        # search across all enabled devices
        for device in devices:
            if (device.enabled and ('host.or.ip' in device.host or
                                    device.username == '<username>' or
                                    device.password == '<password>' or
                                    device.password == '')):
                return HttpResponseRedirect('%s?invalid=true' %
                                            reverse('device-list'))

        if not request.user.profile_seen:
            # only redirect if first login
            return HttpResponseRedirect(reverse('preferences')+'?next=/report')

        # Setup default criteria for the report based on underlying tables
        system_settings = SystemSettings.get_system_settings()
        form_init = {'ignore_cache': system_settings.ignore_cache}
        for table in report.tables():
            if table.criteria:
                form_init.update(table.criteria)

        # Collect all fields organized by section, with section id 0
        # representing common report level fields
        fields_by_section = report.collect_fields_by_section()

        # Merge fields into a single dict for use by the Django Form # logic
        all_fields = SortedDict()
        [all_fields.update(c) for c in fields_by_section.values()]
        form = TableFieldForm(all_fields,
                              hidden_fields=report.hidden_fields,
                              initial=form_init)

        # Build a section map that indicates which section each field
        # belongs in when displayed
        section_map = []
        if fields_by_section[0]:
            section_map.append({'title': 'Common',
                                'parameters': fields_by_section[0]})

        for s in Section.objects.filter(report=report).order_by('position',
                                                                'title'):
            show = False
            for v in fields_by_section[s.id].values():
                if v.keyword not in (report.hidden_fields or []):
                    show = True
                    break

            if show:
                section_map.append({'title': s.title,
                                    'parameters': fields_by_section[s.id]})

        template, criteria, expand_tables = self.get_media_params(request)

        return render_to_response(template,
                                  {'report': report,
                                   'developer': system_settings.developer,
                                   'maps_version': system_settings.maps_version,
                                   'maps_api_key': system_settings.maps_api_key,
                                   'endtime': 'endtime' in form.fields,
                                   'form': form,
                                   'section_map': section_map,
                                   'show_sections': (len(section_map) > 1),
                                   'criteria': criteria,
                                   'expand_tables': expand_tables},
                                  context_instance=RequestContext(request))


class ReportView(GenericReportView):
    """ Main handler for /report/{id}
    """
    model = Report
    serializer_class = ReportSerializer
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get_media_params(self, request):
        template = 'report.html'
        criteria = 'null'
        expand_tables = False

        return template, criteria, expand_tables

    # ReportView.get()
    def get(self, request, namespace=None, report_slug=None):
        if request.accepted_renderer.format == 'html':  # handle HTML calls
            queryset = Report.objects.filter(enabled=True)

            try:
                if namespace is None:
                    namespace = queryset[0].namespace

                if report_slug is None:
                    qs = (queryset.filter(namespace=namespace)
                          ).order_by('position', 'title')
                    kwargs = {'report_slug': qs[0].slug,
                              'namespace': namespace}
                    return HttpResponseRedirect(reverse('report-view',
                                                        kwargs=kwargs))
                else:
                    report = queryset.get(namespace=namespace,
                                          slug=report_slug)
            except:
                raise Http404

            return self.render_html(report, request, namespace, report_slug,
                                    False)
        else:  # handle REST calls
            queryset = Report.objects.filter(enabled=True)
            if namespace and report_slug:
                queryset = queryset.get(namespace=namespace,
                                        slug=report_slug)
            elif report_slug:
                queryset = queryset.get(namespace='default',
                                        slug=report_slug)
            elif namespace:
                queryset = queryset.filter(namespace='default')

            serializer = ReportSerializer(instance=queryset)
            return Response(serializer.data)

    # ReportView.post()
    def post(self, request, namespace=None, report_slug=None):
        if namespace is None or report_slug is None:
            return self.http_method_not_allowed(request)

        logger.debug("Received POST for report %s, with params: %s" %
                     (report_slug, request.POST))

        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)

        fields_by_section = report.collect_fields_by_section()
        all_fields = SortedDict()
        [all_fields.update(c) for c in fields_by_section.values()]
        form = TableFieldForm(all_fields, hidden_fields=report.hidden_fields,
                              data=request.POST, files=request.FILES)

        if form.is_valid():
            logger.debug('Form passed validation: %s' % form)
            formdata = form.cleaned_data
            logger.debug('Form cleaned data: %s' % formdata)

            # parse time and localize to user profile timezone
            timezone = pytz.timezone(request.user.timezone)
            form.apply_timezone(timezone)

            if formdata['debug']:
                logger.debug("Debugging report and rotating logs now ...")
                management.call_command('rotate_logs')

            logger.debug("Report %s validated form: %s" %
                         (report_slug, formdata))

            # setup definitions for each Widget
            definition = []

            # store datetime info about when report is being run
            # XXX move datetime format to preferences or somesuch
            now = datetime.datetime.now(timezone)
            definition.append({'datetime': str(date(now, 'jS F Y H:i:s')),
                               'timezone': str(timezone),
                               'debug': formdata['debug']})

            # create matrix of Widgets
            lastrow = -1
            rows = []
            for w in report.widgets().order_by('row', 'col'):
                if w.row != lastrow:
                    lastrow = w.row
                    rows.append([])
                rows[-1].append(Widget.objects.get_subclass(id=w.id))

            # populate definitions
            for row in rows:
                for w in row:
                    widget_def = {"widgettype": w.widgettype().split("."),
                                  "posturl": reverse('widget-job-list',
                                                     args=(report.namespace,
                                                           report.slug,
                                                           w.slug)),
                                  "options": w.uioptions,
                                  "widgetid": w.id,
                                  "widgetslug": w.slug,
                                  "row": w.row,
                                  "width": w.width,
                                  "height": w.height,
                                  "criteria": form.as_text()
                                  }
                    definition.append(widget_def)

            logger.debug("Sending widget definitions for report %s: %s" %
                         (report_slug, definition))

            return HttpResponse(json.dumps(definition))
        else:
            # return form with errors attached in a HTTP 400 Error response
            return HttpResponse(str(form.errors), status=400)


class ReportPrintView(GenericReportView):
    """ Handles printer-friendly report pages
    """
    model = Report
    serializer_class = ReportSerializer
    renderer_classes = (TemplateHTMLRenderer, )

    def get_media_params(self, request):
        template = 'report_print.html'
        criteria = json.dumps(dict(zip(request.POST.keys(),
                                       request.POST.values())))
        expand_tables = ('expand_tables' in request.POST and
                         request.POST['expand_tables'] != '')
        return template, criteria, expand_tables

    def post(self, request, namespace, report_slug):
        queryset = Report.objects.filter(enabled=True)
        try:
            report = queryset.get(namespace=namespace, slug=report_slug)
        except:
            raise Http404

        return self.render_html(report, request, namespace, report_slug, True)


class ReportEditor(views.APIView):
    """ Edit Report files directly.  Requires superuser permissions. """
    renderer_classes = (TemplateHTMLRenderer, )
    permission_classes = (IsAdminUser, )

    def _git_repo(self):
        # check if git enabled for this project
        try:
            shell(cmd='git status', cwd=settings.PROJECT_ROOT, allow_fail=True)
            return True
        except ShellFailed:
            return False

    def get(self, request, namespace, report_slug):
        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)
        form = ReportEditorForm(report.filepath)
        copyform = CopyReportForm(report)
        return render_to_response('edit.html',
                                  {'report': report,
                                   'form': form,
                                   'ajaxform': copyform,
                                   'gitavail': self._git_repo()},
                                  context_instance=RequestContext(request))

    def post(self, request, namespace, report_slug):
        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)
        form = ReportEditorForm(report.filepath, request.POST)
        if form.is_valid():
            form.save()
            msg = 'Report %s saved.' % report.filepath
        else:
            msg = 'Problem saving report ... review content.'

        messages.add_message(request, messages.INFO, msg)
        copyform = CopyReportForm(report)
        return render_to_response('edit.html',
                                  {'report': report,
                                   'form': form,
                                   'ajaxform': copyform,
                                   'gitavail': self._git_repo()},
                                  context_instance=RequestContext(request))


class ReportEditorDiff(views.APIView):
    """ Show git diff of report file.  Requires superuser permissions. """
    renderer_classes = (TemplateHTMLRenderer, )
    permission_classes = (IsAdminUser, )

    def get(self, request, namespace, report_slug):
        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)
        from ansi2html import Ansi2HTMLConverter
        conv = Ansi2HTMLConverter(inline=True, dark_bg=False)
        ansi = shell('git diff --color %s' % report.filepath, save_output=True)
        html = conv.convert(ansi, full=False)
        if (not html and shell('git ls-files %s' % report.filepath,
                               save_output=True)):
            html = 'No changes.'
        else:
            html = 'File not committed to git repository.'

        return render_to_response('editdiff.html',
                                  {'report': report,
                                   'diffhtml': html},
                                  context_instance=RequestContext(request))


class ReportCopy(views.APIView):
    """ Edit Report files directly.  Requires superuser permissions. """
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    permission_classes = (IsAdminUser, )

    def get(self, request, namespace, report_slug):
        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)
        form = CopyReportForm(report)
        return render_to_response('ajax_form.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))

    def update_title(self, report, form):
        """ Writes new title into file"""
        with open(form.filepath(), "r+") as f:
            lines = f.read().split("\n")
            new_line = None
            for ind, ln in enumerate(lines):
                if "Report.create" in ln and not ln.startswith('#'):
                    new_line = ln.replace(report.title, form.reportname)
                    break
            if new_line is None:
                raise ValidationError("Current report does not have title")
            lines[ind] = new_line
            f.seek(0)
            f.write("\n".join(lines))
            f.truncate()

    def post(self, request, namespace, report_slug):
        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)
        form = CopyReportForm(report, request.POST)
        response = {}
        if form.is_valid():
            try:
                shutil.copyfile(report.filepath, form.filepath())
                # update the title of the new report
                self.update_title(report, form)

                response['redirect'] = reverse('report-editor',
                                               args=(form.namespace,
                                                     form.slug))

                return Response(json.dumps(response))
            except IOError:
                rm_file(form.filepath())
                msg = ('Error copying file from %s to %s' % (report.filepath,
                                                             form.filepath()))
                template = """<li id="message_ajax"><a href="#" onclick="$('#message_ajax').fadeOut(); return false;"><small>clear</small></a> %s</li>'"""
                response['messages'] = template % msg
                return Response(json.dumps(response))
            except Exception, e:
                rm_file(form.filepath())
                msg = ('Error copying report file %s: %s' % (report.filepath,
                                                             str(e)))
                template = """<li id="message_ajax"><a href="#" onclick="$('#message_ajax').fadeOut(); return false;"><small>clear</small></a> %s</li>'"""
                response['messages'] = template % msg
                return Response(json.dumps(response))

        t = loader.get_template('ajax_form.html')
        c = RequestContext(request, {'ajaxform': form})
        response['form'] = t.render(c)
        return Response(json.dumps(response))


class ReportCriteria(views.APIView):
    """ Handle requests for criteria fields.

        `get`  returns a json object of all criteria for the specified
               Report, or optionally for a specific widget within the Report

        `post` takes a criteria form and returns a json object of just
               the changed, or dynamic values
    """
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def get(self, request, namespace=None, report_slug=None, widget_slug=None):
        all_fields = SortedDict()

        report = get_object_or_404(Report,
                                   namespace=namespace,
                                   slug=report_slug)

        if widget_slug:
            w = get_object_or_404(
                Widget,
                slug=widget_slug,
                section__in=Section.objects.filter(report=report)
            )
            all_fields = w.collect_fields()
        else:
            fields_by_section = report.collect_fields_by_section()
            for c in fields_by_section.values():
                all_fields.update(c)

        form = TableFieldForm(all_fields, use_widgets=False)

        # create object from the tablefield keywords
        # then populate it with the initial data that got generated by default
        keys = form._tablefields.keys()
        criteria = dict(zip(keys, [None]*len(keys)))
        criteria.update(form.data)

        return HttpResponse(json.dumps(criteria))

    def post(self, request, namespace=None, report_slug=None):
        # handle REST calls
        if report_slug is None:
            return self.http_method_not_allowed(request)

        logger.debug("Received POST for report %s, with params: %s" %
                     (report_slug, request.POST))

        report = get_object_or_404(Report,
                                   namespace=namespace,
                                   slug=report_slug)

        fields_by_section = report.collect_fields_by_section()
        all_fields = SortedDict()
        [all_fields.update(c) for c in fields_by_section.values()]

        form = TableFieldForm(all_fields, hidden_fields=report.hidden_fields,
                              data=request.POST, files=request.FILES)

        response = []

        for field in form.dynamic_fields():
            response.append({'id': field.auto_id,
                             'html': str(field)})
        return HttpResponse(json.dumps(response))


class ReportWidgets(views.APIView):
    """ Return default criteria values for all widgets, with latest time,
        if applicable.

        Used in auto-run reports when specifying detailed criteria isn't
        necessary.
    """

    authentication_classes = (SessionAuthentication,
                              BasicAuthentication,
                              URLTokenAuthentication)

    def get(self, request, namespace=None, report_slug=None):
        try:
            report = Report.objects.get(namespace=namespace,
                                        slug=report_slug)
        except:
            raise Http404

        # parse time and localize to user profile timezone
        timezone = pytz.timezone(request.user.timezone)
        now = datetime.datetime.now(timezone)

        # pin the endtime to a round interval if we are set to
        # reload periodically
        minutes = report.reload_minutes
        if minutes:
            # avoid case of long duration reloads to have large reload gap
            # e.g. 24-hour report will consider 12:15 am or later a valid time
            # to roll-over the time time values, rather than waiting
            # until 12:00 pm
            trimmed = round_time(dt=now, round_to=60*minutes, trim=True)
            if now - trimmed > datetime.timedelta(minutes=15):
                now = trimmed
            else:
                now = round_time(dt=now, round_to=60*minutes)

        widget_defs = []

        widget_defs.append({'datetime': str(date(now, 'jS F Y H:i:s')),
                            'timezone': str(timezone),
                            })
        for w in report.widgets().order_by('row', 'col'):
            # get default criteria values for widget
            # and set endtime to now, if applicable
            criteria = ReportCriteria.as_view()(request,
                                                w.section.report.namespace,
                                                w.section.report.slug,
                                                w.slug)
            widget_criteria = json.loads(criteria.content)
            if 'endtime' in widget_criteria:
                widget_criteria['endtime'] = now.isoformat()

            # setup json definition object
            widget_def = {
                "widgettype": w.widgettype().split("."),
                "posturl": reverse('widget-job-list',
                                   args=(w.section.report.namespace,
                                         w.section.report.slug,
                                         w.slug)),
                "options": w.uioptions,
                "widgetid": w.id,
                "widgetslug": w.slug,
                "row": w.row,
                "width": w.width,
                "height": w.height,
                "criteria": widget_criteria
            }

            widget_defs.append(widget_def)

        return HttpResponse(json.dumps(widget_defs))


class ReportTableList(generics.ListAPIView):
    """Return list of tables associated with a given Report."""
    serializer_class = TableSerializer

    def get_queryset(self):
        report = Report.objects.get(namespace=self.kwargs['namespace'],
                                    slug=self.kwargs['report_slug'])
        return report.tables()


class WidgetDetailView(generics.RetrieveAPIView):
    """ Return Widget details looked up by slug field. """
    model = Widget
    lookup_field = 'slug'
    lookup_url_kwarg = 'widget_slug'
    serializer_class = WidgetSerializer
    renderer_classes = (JSONRenderer, )


class WidgetView(views.APIView):
    """ Handler for displaying one widget which uses default criteria
    """
    serializer_class = ReportSerializer
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    authentication_classes = (URLTokenAuthentication,)

    def get(self, request, namespace=None, report_slug=None, widget_slug=None):
        token = request.GET.dict()['auth']

        token_obj = WidgetAuthToken.objects.get(token=token)
        criteria = json.dumps(token_obj.criteria)

        token_obj.save()

        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)

        # widget slugs aren't unique globally, but should be unique within
        # any given report
        w = get_object_or_404(
            Widget,
            slug=widget_slug,
            section__in=Section.objects.filter(report=report)
        )

        system_settings = SystemSettings.get_system_settings()
        widget_type = [str(x) for x in w.widgettype().split(".")]
        widget_def = {
            "namespace": namespace,
            "report_slug": report_slug,
            "widgettype": [widget_type[0], widget_type[1]],
            "widgetid": w.id,
            "widgetslug": w.slug,
            "criteria": mark_safe(criteria),
            "authtoken": token
        }

        return render_to_response(
            'widget.html',
            {"widget": widget_def,
             'maps_version': system_settings.maps_version,
             'maps_api_key': system_settings.maps_api_key},
            context_instance=RequestContext(request)
        )


class WidgetTokenView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request, namespace=None,
             report_slug=None, widget_slug=None):
        logger.debug("Received POST for widget token, widget %s: %s" %
                     (widget_slug, request.POST))

        user = PortalUser.objects.get(username=request.user)

        # First remove last '/' at the end
        # then remove authtoken at the end
        pre_url = request.path.rstrip('/').rsplit('/', 1)[0]

        criteria = json.loads(request.POST.dict()['criteria'])

        tokens = WidgetAuthToken.objects.filter(user=user, pre_url=pre_url,
                                                criteria=criteria)
        if tokens:
            token = tokens[0].token
        else:
            token = uuid.uuid4().hex
            widget_auth = WidgetAuthToken(token=token,
                                          user=user,
                                          pre_url=pre_url,
                                          criteria=criteria)
            widget_auth.save()
        return Response({'auth': token})


class WidgetJobsList(views.APIView):
    parser_classes = (JSONParser,)

    authentication_classes = (SessionAuthentication,
                              BasicAuthentication,
                              URLTokenAuthentication)

    def post(self, request, namespace, report_slug, widget_slug, format=None):
        logger.debug("Received POST for report %s, widget %s: %s" %
                     (report_slug, widget_slug, request.POST))

        report = get_object_or_404(Report, namespace=namespace,
                                   slug=report_slug)

        widget = get_object_or_404(
            Widget,
            slug=widget_slug,
            section__in=Section.objects.filter(report=report)
        )

        req_json = json.loads(request.POST['criteria'])

        fields = widget.collect_fields()

        form = TableFieldForm(fields, use_widgets=False,
                              hidden_fields=report.hidden_fields,
                              include_hidden=True,
                              data=req_json, files=request.FILES)

        if not form.is_valid():
            raise ValueError("Widget internal criteria form is invalid:\n%s" %
                             (form.errors.as_text()))

        if form.is_valid():
            logger.debug('Form passed validation: %s' % form)
            formdata = form.cleaned_data
            logger.debug('Form cleaned data: %s' % formdata)

            # parse time and localize to user profile timezone
            timezone = pytz.timezone(request.user.timezone)
            form.apply_timezone(timezone)

            try:
                form_criteria = form.criteria()
                logger.debug('Form_criteria: %s' % form_criteria)
                job = Job.create(table=widget.table(),
                                 criteria=form_criteria)
                job.start()

                wjob = WidgetJob(widget=widget, job=job)
                wjob.save()

                logger.debug("Created WidgetJob %s for report %s (handle %s)" %
                             (str(wjob), report_slug, job.handle))

                return Response({"joburl": reverse('report-job-detail',
                                                   args=[namespace,
                                                         report_slug,
                                                         widget_slug,
                                                         wjob.id])})
            except Exception as e:
                logger.exception("Failed to start job, an exception occurred")
                return HttpResponse(str(e), status=400)

        else:
            logger.error("form is invalid, entering debugger")
            from IPython import embed; embed()


class WidgetJobDetail(views.APIView):

    authentication_classes = (SessionAuthentication,
                              BasicAuthentication,
                              URLTokenAuthentication)

    def get(self, request, namespace, report_slug, widget_slug, job_id,
            format=None, status=None):
        wjob = WidgetJob.objects.get(id=job_id)

        job = wjob.job
        widget = wjob.widget

        if not job.done():
            # job not yet done, return an empty data structure
            #logger.debug("%s: Not done yet, %d%% complete" % (str(wjob),
            #                                                  job.progress))
            resp = job.json()
        elif job.status == Job.ERROR:
            resp = job.json()
            logger.debug("%s: Job in Error state, deleting Job" % str(wjob))
            wjob.delete()
        else:
            try:
                i = importlib.import_module(widget.module)
                widget_func = i.__dict__[widget.uiwidget].process
                if widget.rows > 0:
                    tabledata = job.values()[:widget.rows]
                else:
                    tabledata = job.values()

                if tabledata is None or len(tabledata) == 0:
                    resp = job.json()
                    resp['status'] = Job.ERROR
                    resp['message'] = "No data returned"
                    logger.debug("%s marked Error: No data returned" %
                                 str(wjob))
                elif hasattr(i, 'authorized') and not i.authorized()[0]:
                    _, msg = i.authorized()
                    resp = job.json()
                    resp['data'] = None
                    resp['status'] = Job.ERROR
                    resp['message'] = msg
                    logger.debug("%s Error: module unauthorized for user %s"
                                 % (str(wjob), request.user))
                elif (hasattr(i, 'authorized') and
                      not Location.objects.all() and
                      not LocationIP.objects.all()):
                    # we are using a maps widget, but have no locations
                    resp = job.json()
                    resp['data'] = None
                    resp['status'] = Job.ERROR
                    msg = '''\
Geolocation data has not been loaded.
See <a href="https://support.riverbed.com/apis/steelscript/appfwk/configuration.html#locations">\
geolocation documentation</a> for more information.'''
                    resp['message'] = msg
                    logger.debug("%s Error: geo location data not loaded.")
                elif status is not None:  # Only status metadata requested
                    resp = job.json()
                else:
                    data = widget_func(widget, job, tabledata)
                    resp = job.json(data)
                    logger.debug("%s complete" % str(wjob))

            except:
                logger.exception("Widget %s (%s) Job %s processing failed" %
                                 (widget.slug, widget.id, job.id))
                resp = job.json()
                resp['status'] = Job.ERROR
                ei = sys.exc_info()
                resp['message'] = str(traceback.format_exception_only(ei[0],
                                                                      ei[1]))

            wjob.delete()

        resp['message'] = cgi.escape(resp['message'])

        return HttpResponse(json.dumps(resp))
