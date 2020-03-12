from datetime import datetime
import pyexcel
import json

from tincan import (
    Statement,
    Agent,
    Verb,
    Activity,
    Context,
    LanguageMap,
    ActivityDefinition,
)

from xapi_client.track.xapi_statements import send_statement

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.conf import settings
from django.contrib.auth.models import User

from commons.models import Project
from .forms import ImportResultsForm

def project_update_context(var_dict, project):
    memberships = project.get_memberships(state=1)
    user_ids = [membership.user_id for membership in memberships]
    users = User.objects.filter(id__in=user_ids).order_by('last_name','first_name')
    form = ImportResultsForm(initial={'project': project.id })
    form.fields['user'].queryset = users
    var_dict['earmaster_import_results_form'] = form

class ImportResults(View):
    form_class = ImportResultsForm
    template_name = 'project_detail.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            project = get_object_or_404(Project, id=data['project'])
            user = data['user']
            print(project, user)
            file = request.FILES['file']
            filename = file.name
            print('filename:', filename)
            extension = filename.split(".")[-1]
            content = file.read()
            records = pyexcel.get_records(file_type=extension, file_content=content)
            name_dict = records[0]
            keys = name_dict.keys()
            rows = []
            for record in records:
                row = [record[key] for key in keys]
                print(row)
                rows.append(row)
            return HttpResponseRedirect('/project/%s/' % project.slug)
        print('errors:', form.errors)
        return render(request, self.template_name, {'earmaster_import_results_form': form})
