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
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files import File
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import json



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
            photos_size.append(photo.image.size / (1024*1024))
        photos_size_in_session = round(sum(photos_size))
        session.photos_size_in_session = photos_size_in_session

    return render(request, 'main/control_panel/view_sessions.html', {'sessions': sessions})


def view_session(request, name):
    session = get_object_or_404(Session, name=name)
    photos = session.photo_set.all()
    photos_size = []
    for photo in photos:
        photos_size.append(photo.image.size/(1024*1024))
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


@user_passes_test(lambda user: user.is_superuser)
def photos_sessions(request):
    sessions = Session.objects.all()

    if request.method == 'POST':
        if 'clear_session' in request.POST:
            session_id =  request.POST['session']
            dropped_photo = Photo.objects.filter(session_id=session_id)
            for photo in dropped_photo:
                photo.delete()


        if 'delete_session' in request.POST:
            session_id =  request.POST['session']
            dropped_photo = Photo.objects.filter(session_id=session_id)
            for photo in dropped_photo:
                photo.delete()
                
            Session.objects.filter(id=session_id).delete()


        if 'add_images_session' in request.POST:
            form = PhotoForm(request.POST, request.FILES)
            if form.is_valid():
                images = request.FILES.getlist('image')
                image_type = request.POST.get('image_type')

                for image in images:
                    try:
                        img = Image.open(image)
                        if img.format !='JPEG':
                            raise ValidationError("not jpeg")
                        
                        if image_type == 'original':
                            photo = Photo(title=image.name, image=image, session=form.cleaned_data['session'])
                            photo.save()

                        elif image_type == 'resized':
                            create_watermarked_photo(image, form.cleaned_data['session'])


                    except Exception as e:
                        form.add_error('image',str(e))

                img_obj = form.instance
                return render(request, 'main/control_panel/photos_sessions.html', {'form': form, 'img_obj': img_obj, 'sessions':sessions})
        
    else:
        form = PhotoForm()

    photos = Photo.objects.all()
    return render(request, 'main/control_panel/photos_sessions.html', {'sessions': sessions, 'photos': photos})


def update_photo_select(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        photo.selected_to_edit = not photo.selected_to_edit
        photo.save()
        return JsonResponse({'status': 'ok'})
    

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


def create_watermarked_photo(image, session):
    img = Image.open(image)
    img.thumbnail((img.width, img.height))
    text = "moccastudio"
    opacity = 60
    grid = 5

    img_width, img_height = img.size
    text_size = img_width // 32
    font = ImageFont.truetype("arial.ttf", text_size)
    text_color = (255, 255, 255, opacity)

    cell_width = img_width // grid
    cell_height = img_height // grid
    for i in range(grid**2):
        row = i // grid
        col = i % grid
        x = col * cell_width + cell_width // 2 - cell_width // 3
        y = row * cell_height + cell_height // 2 

        text_image = Image.new('RGBA', (cell_width, cell_height), (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((cell_width // 2, cell_height // 2), text, fill=text_color, font=font, anchor="mm")
        rotated_text = text_image.rotate(45, expand=True)
        img.paste(rotated_text, (x - cell_width // 2, y - cell_height // 2), rotated_text)

    output_io = BytesIO()
    img.save(output_io, format='JPEG') 
    output_io.seek(0)

    photo = Photo(title=image.name, image=File(output_io, name=image.name), session=session)
    photo.save()