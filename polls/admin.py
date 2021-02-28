from django.contrib import admin

# Register your models here.
from django.contrib import admin

from polls.models import Poll, Answer, Question, QuestionOption, PollAssignment

admin.site.register(Poll)
admin.site.register(PollAssignment)
admin.site.register(QuestionOption)
admin.site.register(Question)
admin.site.register(Answer)
