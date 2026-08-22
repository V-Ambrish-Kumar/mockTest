from django.contrib import admin
from .models import Subject, Topic, Question, Option, Test, TestTopicRule, TestAttempt
import random

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4  # Shows 4 blank option fields automatically

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [OptionInline]
    list_display = ('text', 'topic', 'time_to_answer')
    list_filter = ('topic__subject', 'topic')

admin.site.register(Subject)
admin.site.register(Topic)

# Add these classes to the bottom of the file:
class TestTopicRuleInline(admin.TabularInline):
    model = TestTopicRule
    extra = 1

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [TestTopicRuleInline]
    exclude = ('questions',) # Hides the manual question checklist

    def save_related(self, request, form, formsets, change):
        # 1. Save the Test and the Topic Rules first
        super().save_related(request, form, formsets, change)
        
        test = form.instance
        selected_questions = []
        
        # 2. Loop through the rules and pick random questions for each topic
        for rule in test.rules.all():
            # Get all available questions for this topic
            topic_qs = list(Question.objects.filter(topic=rule.topic))
            
            # Make sure we don't try to pick more questions than actually exist
            pick_count = min(rule.count, len(topic_qs))
            
            # Pick them randomly and add to our master list
            selected_questions.extend(random.sample(topic_qs, pick_count))
        
        # 3. Attach the randomly selected questions to the test automatically
        test.questions.set(selected_questions)