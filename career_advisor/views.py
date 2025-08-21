import re
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import SkillForm
from .forms import SubmissionForm
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .forms import ResumeSubmissionForm  
from django.http import JsonResponse
from .models import ContactMessage
from django.core.mail import send_mail
from django.conf import settings

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# simple mapping skills -> careers
CAREER_MAP = {
    'python': ['Python Developer', 'Backend Developer', 'Data Engineer'],
    'django': ['Backend Developer (Django)'],
    'flask': ['Backend Developer (Flask)'],
    'sql': ['Database Developer / Analyst'],
    'postgresql': ['Database Developer'],
    'mysql': ['Database Developer'],
    'pandas': ['Data Analyst', 'Data Scientist'],
    'numpy': ['Data Scientist'],
    'scikit-learn': ['ML Engineer', 'Data Scientist'],
    'tensorflow': ['ML Engineer (Deep Learning)'],
    'pytorch': ['ML Engineer (Deep Learning)'],
    'nlp': ['NLP Engineer'],
    'computer vision': ['Computer Vision Engineer'],
    'javascript': ['Frontend / Full-Stack Developer'],
    'react': ['Frontend / Full-Stack Developer'],
    'html': ['Frontend Developer'],
    'css': ['Frontend Developer'],
    'aws': ['Cloud / DevOps Engineer'],
    'docker': ['MLOps / DevOps Engineer'],
    'kubernetes': ['DevOps / SRE'],
    'tableau': ['BI Analyst'],
    'power bi': ['BI Analyst'],
    'spark': ['Big Data Engineer'],
    'hadoop': ['Big Data Engineer'],
    'java': ['Java Developer'],
    'c++': ['Systems / Game Developer'],
    'git': ['Software Engineer'],
    'linux': ['Systems / DevOps'],
    'wordpress': ['Web Developer'],
}

def extract_text_from_file(f):
    """Try to extract text from uploaded file (.txt/.pdf/.docx)."""
    name = f.name.lower()
    content = ""
    try:
        if name.endswith('.txt'):
            content = f.read().decode('utf-8', errors='ignore')
        elif name.endswith('.pdf'):
            # try PyPDF2
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(f)
                texts = [p.extract_text() or "" for p in reader.pages]
                content = "\n".join(texts)
            except Exception:
                content = ""
        elif name.endswith('.docx'):
            try:
                import docx
                # need to save to temp or read bytes
                from io import BytesIO
                doc = docx.Document(BytesIO(f.read()))
                content = "\n".join([p.text for p in doc.paragraphs])
            except Exception:
                content = ""
        else:
            # attempt decode
            try:
                content = f.read().decode('utf-8', errors='ignore')
            except Exception:
                content = ""
    except Exception:
        content = ""
    return content.lower()

def get_skills_from_text(text):
    text = (text or "").lower()
    # simple split on commas + words
    maybe = re.findall(r"[a-z0-9\+\-\.]+(?: [a-z0-9\+\-\.]+)?", text)
    found = set()
    for token in maybe:
        token = token.strip()
        # check for multi-word keys first
        for key in CAREER_MAP.keys():
            if key in token or (" " in key and key in text):
                found.add(key)
    # if spaCy is available, add lemma matching
    if nlp:
        doc = nlp(text)
        for tok in doc:
            w = tok.lemma_.lower()
            if w in CAREER_MAP:
                found.add(w)
    return sorted(found)

def score_and_recommend(skills_found):
    score = {}
    for sk in skills_found:
        careers = CAREER_MAP.get(sk, [])
        for c in careers:
            score[c] = score.get(c, 0) + 1
    # fallback if score empty: suggest general roles
    if not score:
        return ["Software Developer", "Data Analyst", "Explore AI & Data"]
    # sort by score desc
    recs = sorted(score.items(), key=lambda x: -x[1])
    return [r[0] for r in recs][:6]

def home(request):
    form = SkillForm()
    return render(request, 'career_advisor/home.html', {'form': form})

def recommend(request):
    recommendations = []
    matched_skills = []
    if request.method == 'POST':
        form = SkillForm(request.POST, request.FILES)
        if form.is_valid():
            skills_text = form.cleaned_data.get('skills') or ""
            resume_file = form.cleaned_data.get('resume')
            text = skills_text or ""
            if resume_file:
                text_from_resume = extract_text_from_file(resume_file)
                text = text + "\n" + text_from_resume

            skills_found = get_skills_from_text(text)
            matched_skills = skills_found
            recommendations = score_and_recommend(skills_found)
        else:
            recommendations = ["Please submit a valid form."]
    return render(request, 'career_advisor/home.html', {
        'recommendations': recommendations,
        'matched_skills': matched_skills,
        'form': SkillForm()
    })

def upload_resume(request):
    return render(request, 'career_advisor/upload_resume.html')

def enter_skills(request):
    return render(request, 'career_advisor/enter_skills.html')

def about(request):
    return render(request, 'career_advisor/about.html')

def contact(request):
    return render(request, 'career_advisor/contact.html')

def upload_or_enter(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # ✅ Saves to DB
            return render(request, 'success.html', {'message': 'Your submission was saved!'})
    else:
        form = SubmissionForm()
    
    return render(request, 'upload_or_enter.html', {'form': form})

def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        ResumeSubmission.objects.create(resume=resume_file)
        return render(request, 'upload_resume.html', {'message': 'Resume uploaded successfully!'})
    return render(request, 'upload_resume.html')

from django.shortcuts import render, redirect
from .models import ResumeSubmission
from django.contrib import messages

def submit_resume(request):
    if request.method == 'POST':
        form = ResumeSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your resume has been submitted successfully!")
            return redirect('submit_resume')
    else:
        form = ResumeSubmissionForm()

    recent_resumes = ResumeSubmission.objects.all().order_by('-submitted_at')[:5]  # show latest 5
    context = {
        'form': form,
        'recent_resumes': recent_resumes,
    }
    return render(request, 'career_advisor/resume_submit.html', context)

def contact(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Save to model
        ContactMessage.objects.create(name=name, email=email, message=message)

        # Optionally, send email here

        return JsonResponse({"success": True})

    return render(request, "career_advisor/contact.html")
