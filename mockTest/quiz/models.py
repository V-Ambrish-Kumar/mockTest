# Save this inside: quiz/models.py

from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.subject.name})"

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    time_to_answer = models.IntegerField(help_text="Time to answer in seconds")
    explanation = models.TextField(blank=True, null=True, help_text="Why is this answer correct?") 

    def __str__(self):
        return self.text[:50]

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Test(models.Model):
    title = models.CharField(max_length=200)
    # The 'syllabus' field is removed. We keep 'questions' but will hide it in Admin.
    questions = models.ManyToManyField(Question, blank=True)

    def __str__(self):
        return self.title

# Add this new model below Test:
class TestTopicRule(models.Model):
    test = models.ForeignKey(Test, related_name='rules', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    count = models.IntegerField(default=5, help_text="Number of questions to randomly pick")

    def __str__(self):
        return f"{self.topic.name} ({self.count} Qs)"

# --- New Models for Users ---

class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.user.username} - Q: {self.question.id}"