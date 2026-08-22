from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Test, TestAttempt, Question, Option, UserAnswer
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'quiz/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def test_list(request):
    tests = Test.objects.all()
    return render(request, 'quiz/test_list.html', {'tests': tests})

@login_required
def start_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    # Create a new attempt when they click "Start"
    attempt = TestAttempt.objects.create(user=request.user, test=test)
    return redirect('take_test', attempt_id=attempt.id)

@login_required
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    if attempt.completed:
        return redirect('test_result', attempt_id=attempt.id) # We will write this view later
    
    questions = attempt.test.questions.all()
    return render(request, 'quiz/take_test.html', {'attempt': attempt, 'questions': questions})

@login_required
def save_answer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        attempt = get_object_or_404(TestAttempt, id=data.get('attempt_id'), user=request.user)
        question = get_object_or_404(Question, id=data.get('question_id'))
        
        # Get or create the answer to prevent duplicates if they click multiple times
        user_answer, created = UserAnswer.objects.get_or_create(attempt=attempt, question=question)

        option_id = data.get('option_id')
        if option_id:
            option = get_object_or_404(Option, id=option_id)
            user_answer.selected_option = option
            user_answer.is_correct = option.is_correct
        else:
            # Time ran out, marked as unanswered/incorrect
            user_answer.selected_option = None
            user_answer.is_correct = False
        
        user_answer.save()
        return JsonResponse({"status": "success"})
        
    return JsonResponse({"status": "error"}, status=400)

@login_required
def finish_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    # Calculate score based on saved UserAnswers
    correct_count = attempt.answers.filter(is_correct=True).count()
    attempt.score = correct_count
    attempt.completed = True
    attempt.save()

    return redirect('test_result', attempt_id=attempt.id)

@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    
    # Security check: if they somehow get here before finishing, send them back
    if not attempt.completed:
        return redirect('take_test', attempt_id=attempt.id)
        
    # select_related makes the database query much faster by grabbing the linked data at the same time
    answers = attempt.answers.select_related('question', 'selected_option').all()
    
    return render(request, 'quiz/test_result.html', {
        'attempt': attempt,
        'answers': answers
    })

@login_required
def dashboard(request):
    # Get all completed attempts for the logged-in user, oldest to newest
    attempts = TestAttempt.objects.filter(user=request.user, completed=True).order_by('start_time')
    
    # Prepare data for Chart.js
    test_names = [attempt.test.title for attempt in attempts]
    scores = [attempt.score for attempt in attempts]
    
    return render(request, 'quiz/dashboard.html', {
        'test_names': json.dumps(test_names),  # Convert to JSON so JavaScript can read it
        'scores': json.dumps(scores),
        'attempts': attempts.order_by('-start_time') # Send recent ones first for a list view
    })