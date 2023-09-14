from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .forms import SignupForm
from .forms import SessionForm
from .models import Session
from .forms import PrivateSessionForm
from .forms import PhotoForm
from .models import Photo


def index(request):
    return render(request, 'main/base.html', {})

def home(request):
    return render(request, 'main/home.html', {})

def portfolio(request):
    return render(request, 'main/portfolio.html', {})

def pricing(request):
    return render(request, 'main/pricing.html', {})


def weddingSession(request):
    return render(request, 'main/session/wedding.html', {})
def newbornSession(request):
    return render(request, 'main/session/newborn.html', {})
def familySession(request):
    return render(request, 'main/session/family.html', {})

def profile(request):
    return render(request, 'main/profile.html', {})


def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = SignupForm()

    return render(request, 'registration/sign_up.html', {'form':form})


def log_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/home')
    
    return render(request, 'registration/logout.html', {})



@user_passes_test(lambda user: user.is_superuser)
def control_panel(request):
    return render(request, 'main/control_panel/control_panel.html', {})

@user_passes_test(lambda user: user.is_superuser)
def create_session(request):
    if request.method == 'POST':
        name = request.POST['name']
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save()
            return redirect('view_session', name=name)

    else:
        form = SessionForm()
    return render(request, 'main/control_panel/create_session.html', {'form': form})




@user_passes_test(lambda user: user.is_superuser)
def delete_sessions(request):
    sessions = Session.objects.all()
    return render(request, 'main/control_panel/delete_sessions.html', {'sessions': sessions})

@user_passes_test(lambda user: user.is_superuser)
def delete_session(request,name):
    session = Session.objects.filter(name=name).delete()
    return render(request, 'main/session/session_template.html', {'session': session})


@user_passes_test(lambda user: user.is_superuser)
def view_sessions(request):
    sessions = Session.objects.all()

    for session in sessions:
        photos = session.photo_set.all()
        photos_size = []
        for photo in photos:
            photos_size.append(photo.image.size / 1024)
        photos_size_in_session = round(sum(photos_size))
        session.photos_size_in_session = photos_size_in_session

    return render(request, 'main/control_panel/view_sessions.html', {'sessions': sessions})




def view_session(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()

    if request.user.is_superuser:
        return render(request, 'main/session/private_session.html', {'session': session, 'photos':photos})


"""
def view_session(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()

    photos_size = []
    for photo in photos:
        photos_size.append(photo.image.size/(1024))
    photos_size_in_session = round(sum(photos_size))

    if request.user.is_superuser:
        return render(request, 'main/session/private_session.html', {'session': session, 'photos':photos, 'photos_size_in_session':photos_size_in_session})

    if request.method == 'POST':
        form = PrivateSessionForm(request.POST)
        if form.is_valid():
            entered_password = form.cleaned_data['password']
            if entered_password == session.password:
                return render(request, 'main/session/private_session.html', {'session': session, 'photos':photos})
    
    else:
        form = PrivateSessionForm()
    
    return render(request, 'main/session/private_session_form.html', {'form': form})

"""






@user_passes_test(lambda user: user.is_superuser)
def photos_sessions(request):
    sessions = Session.objects.all()

    if request.method == 'POST':

        if 'clear_session' in request.POST:
            session =  request.POST['session']
            dropped_photo = Photo.objects.filter(session=session)
            import os
            from django.conf import settings
            for photo in dropped_photo:
                file_path = os.path.join(settings.MEDIA_ROOT, str(photo.image))
                if os.path.exists(file_path):
                    os.remove(file_path)
                photo.delete()

        if 'delete_session' in request.POST:
            name =  request.POST['session']
            session = Session.objects.filter(name=name).delete()

        

        if 'add_images_session' in request.POST:
            from PIL import Image
            from io import BytesIO
            from django.core.files import File

            form = PhotoForm(request.POST, request.FILES)
            if form.is_valid():
                images = request.FILES.getlist('image')
                image_type = request.POST.get('image_type')

                for image in images:
                    if image_type == 'original':
                        photo = Photo(title=image.name, image=image, session=form.cleaned_data['session'])
                        photo.save()
                    elif image_type == 'resized':
                        img = Image.open(image)
                        img.thumbnail((img.width // 4, img.height // 4))  # Pomniejszenie do 1/4 rozmiaru
                        output_io = BytesIO()
                        img.save(output_io, format='JPEG') 
                        output_io.seek(0)

                        photo = Photo(title=form.cleaned_data['title'], image=File(output_io, name=image.name), session=form.cleaned_data['session'])
                        photo.save()

                img_obj = form.instance
                return render(request, 'main/control_panel/photos_sessions.html', {'form': form, 'img_obj': img_obj, 'sessions':sessions})
        
    else:
        form = PhotoForm()


    photos = Photo.objects.all()
    return render(request, 'main/control_panel/photos_sessions.html', {'sessions': sessions, 'photos': photos})



from django.http import JsonResponse
def update_photo_select(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        photo.selected_to_edit = not photo.selected_to_edit
        photo.save()
        return JsonResponse({'status': 'ok'})
    

import json
def update_photo_select_multiple(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            photo_ids = data.get('photoIds', [])

            for photo_id in photo_ids:
                photo = get_object_or_404(Photo, id=photo_id)
                photo.selected_to_edit = False
                photo.save()
            return JsonResponse({'message': 'Photos updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'message': 'Method not allowed'}, status=405)