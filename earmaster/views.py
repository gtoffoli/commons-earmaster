from datetime import datetime
import pyexcel
import pytz

from tincan import (
    Statement,
    Agent,
    Verb,
    Activity,
    Context,
    Result,
    Score,
    LanguageMap,
    ActivityDefinition,
)

from xapi_client.utils import xapi_activities, xapi_verbs
from xapi_client.track.xapi_statements import send_statement, get_language, get_object_id

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

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

            timezone = pytz.timezone("Europe/Rome")

            actor = Agent(
                name=user.get_display_name(),
                mbox='mailto:%s' % user.email,
            )

            project_id = get_object_id(request, project)

            activity_type = xapi_activities['assessment']['type']
            object_language = 'it'
            verb = Verb(
                id=xapi_verbs['completed']['id'],
                display=LanguageMap(**xapi_verbs['completed']['display']),
            )

            file = request.FILES['file']
            filename = file.name
            extension = filename.split(".")[-1]
            content = file.read()
            records = pyexcel.get_records(file_type=extension, file_content=content)
            name_dict = records[0]
            keys = name_dict.keys()
            rows = []
            for record in records:
                date_time = record['Ora']
                lesson = record['Lezione']
                course = record['Corso']
                activity = record['Attività']
                duration_seconds = record['Durata (Secondi)']
                response_seconds = record['Tempo medio di risposta (Secondi)']
                score_percent = record['Punteggio (%)']
                questions = record['Domande con risposta']
                correct_answers = record['Risposte corrette']

                timestamp = datetime.strptime(date_time, "%d/%m/%Y %H.%M")
                timestamp = timezone.localize(timestamp)
                
                object_name = 'EarMaster: {}'.format(activity)
                object_description = 'Esercizio di {} in lezione EarMaster "{}"'.format(activity, lesson)
                activity_definition = ActivityDefinition(
                     name=LanguageMap(**{object_language: object_name}),
                     description=object_description and LanguageMap(**{object_language: object_description}) or None,
                     type=activity_type,                                        
                )
                course_id = '{}{}'.format(project_id, slugify(course))
                lesson_id = '{}/{}'.format(course_id, slugify(lesson))
                object = Activity(
                    objectType='Activity',
                    id=lesson_id,
                    definition=activity_definition,
                )
                parent = {
                   'objectType': 'Activity',
                   'id': course_id,
                   'definition': {'type': xapi_activities['course']['type'], 'name': {'it': course}}
                }
                grouping = {
                   'objectType': 'Activity',
                   'id': project_id,
                   'definition': {'type': xapi_activities['project']['type'], 'name': LanguageMap(**{get_language(project): project.name})}
                }
                context = {
                    'platform': 'EarMaster',
                    'context_activities': {
                        'parent': parent,
                        'grouping': grouping
                    }
                }
                context = Context(**context)

                score_scaled = float(score_percent.replace('%', ''))/100
                score_max = questions
                score_raw = correct_answers
                score =  {
                    'min': 0,
                    'max': score_max,
                    'raw': score_raw,
                    'scaled': score_scaled
                }
                score = Score(**score)
                result = {
                    'duration': duration_seconds,
                    'score': score
                }
                result = Result(**result)

                statement = Statement(
                    actor=actor,
                    verb=verb,
                    object=object,
                    context=context,
                    result=result,
                    timestamp=timestamp
                )
                result = send_statement(statement)
            return HttpResponseRedirect('/project/%s/' % project.slug)
        return render(request, self.template_name, {'earmaster_import_results_form': form})
