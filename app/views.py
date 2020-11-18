from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import os
import json
from pathlib import Path
from accounts.models import Account
from .models import uploadFile, shareFile, urlMapping, passwordResetRequest
from django.contrib import messages
import shutil
import uuid
import pdfkit
import time
import requests
import datetime
import random
from twilio.rest import Client
import smtplib
import bcrypt
# import pyrebase

account_sid = 'AC294b2942d799027e5545212fd91fe65f'
auth_token = 'e6bc29bb76d764e35c0c46701810ef63'

# firebaseConfig = {
#   'apiKey': "AIzaSyCkMd4dg9xq9JfelWe1ZG67tQFKbE2ud-4",
#   'authDomain': "anvi-48aa3.firebaseapp.com",
#   'databaseURL': "https://anvi-48aa3.firebaseio.com",
#   'projectId': "anvi-48aa3",
#   'storageBucket': "anvi-48aa3.appspot.com",
#   'messagingSenderId': "1028522121582",
#   'appId': "1:1028522121582:web:4fdf5c2c10a02f310ac97f",
#   'measurementId': "G-7N6H9LDGWV"
# }

# firebase = pyrebase.initialize_app(firebaseConfig)

# firebaseDB = firebase.database()

BASE_DIR = Path(__file__).resolve().parent.parent

def generate_random_string(len):
    random_string = ''
    for _ in range(len):
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        random_string += (chr(random_integer))
    return random_string

def go_to_show_files(request):
    return redirect('show_files')

def check_user(request):
    try:
        check_user = request.session['user']
        return check_user['email']
    except:
        return redirect('logout_user')

def shares(request):
    context = {
        'title': 'Shares',
    }
    return render(request, 'app/shares.html', context)
def url_mapping(request, token):
    try:
        url_check = urlMapping.objects.get(short_token=token)
        try:
            url_check.opened = True
        except:
            pass
        return redirect(url_check.original_url)
    except:
        return HttpResponse("URL Doesn't Exists")

def directorySize(directory):
    total = 0;
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += directorySize(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total

def show_files(request):
    try:
        user_check = request.session['user']
    except:
        return redirect('login_user')
    email = request.session['user']['email']
    user_account = Account.objects.get(email = email)
    media_files = os.path.join(BASE_DIR, 'media')
    user_token = user_account.token
    if request.method == "GET":
        if request.GET.get('action') == "add_folder":
            path = request.GET['path'][4:]
            path.replace('home', '')
            user_folder = media_files + "/files/" + user_token + "_files" + path + "/" + request.GET['folder_name']
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)
                response = {}
                response['text'] = 'true'
                return JsonResponse(response)
            else:
                response = {}
                response['text'] = 'false'
                return JsonResponse(response)
    if request.method == "POST":
        if request.POST.get('action') == "delete_file":
            file_name = request.POST.get('file_name')
            path = request.POST.get('path')[4:]
            response = {}
            user_folder = media_files + "/files/" + user_token + "_files" + path + "/" + file_name
            if os.path.exists(user_folder):
                os.remove(user_folder)
                try:
                    check_shares = shareFile.objects.filter(file_name = file_name)
                    for i in check_shares:
                        i.delete()
                except:
                    pass
                response['text'] = 'file deleted'
            else: 
                response['text'] = "error occured while deleting file"
            return JsonResponse(response)
        elif request.POST.get('action') == "unshare_report":
            file_name = request.POST.get('file_name')
            share_user_id = request.POST.get('share_user_id')
            response = {}
            try:
                share_check = shareFile.objects.get(file_name=file_name, receiver_id=share_user_id)
                share_check.delete()
                response['text'] = 'true'
            except:
                response['text'] = 'false'
            return JsonResponse(response)
        elif request.POST.get('action') == "share_file":
            file_path = request.POST.get('path', 'home')[4:]
            file_name = request.POST.get('file_name')
            sender_folder = media_files + "/files/" + user_account.token + "_files" + file_path + f"/{file_name}"
            file_path_db = '/media/files/' + user_account.token + "_files" + file_path + f"/{file_name}"
            response = {}
            response['text'] = 'true'
            response['file_name'] = file_name + ".pdf"
            response['file_path'] = f"{file_path_db}"
            newshare = shareFile(sender_id=int(user_account.id), receiver_id=request.POST.get('email'), file_path=file_path_db ,file_name=file_name, token=str(uuid.uuid4()), doctor_name=request.POST.get('doctor_name'))
            newshare.save()
            response['token'] = str(uuid.uuid4())
            return JsonResponse(response)
        file_name = request.FILES['files'].name
        file_path = request.POST['folder_path'][4:]
        uploaded_file = request.FILES['files']
        file_token = str(uuid.uuid4())
        newupload = uploadFile(uploaded_by=user_account, file_name=file_name, file_path=file_path, file_uploaded=uploaded_file, token=file_token)
        newupload.save()
        get_file = uploadFile.objects.get(token=file_token)
        media_files = os.path.join(BASE_DIR, 'media')
        new_path = media_files + "/files/" + user_account.token + "_files" + get_file.file_path + "/" + get_file.file_name
        path = get_file.file_uploaded.url
        path = [i for i in path.split("/")][2:]
        final_path = ""
        final_path = final_path + media_files
        for i in path:
            final_path = final_path + "/" + i
        shutil.move(final_path, new_path)
        new_path_rename = media_files + "/files/" + user_account.token + "_files" + get_file.file_path + "/" + get_file.file_name.replace(" ", "_")
        os.rename(new_path, new_path_rename)
        response = {}
        response['text'] = "true"
        return JsonResponse(response)
    path = request.GET.get("path", 'home')[4:]
    path_directory = [i for i in path.split("/")]
    paths = []
    for i in range(0, len(path_directory)):
        path_dict = {}
        try:
            if path_directory[i] != "":
                path_dict['name'] = path_directory[i]
                link = "home/"
                for j in range(0, i+1):
                    if len(path_directory[j]) > 1:
                        link += f'{path_directory[j]}/'
                path_dict['path'] = link
                paths.append(path_dict)
        except:
            pass
    email = request.session['user']['email']
    user_account = Account.objects.get(email = email)
    media_files = os.path.join(BASE_DIR, 'media')
    user_token = user_account.token
    user_folder = media_files + "/files/" + user_token + "_files" + path
    folders = []
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    else:
        folders = os.listdir(user_folder)
    files_list = []
    folders_list = []
    for i in folders:
        if "." in i:
            file_object = {}
            file_path = "media/files/" + user_token + "_files" + path + "/" + i
            file_object['file_size'] = round(os.path.getsize(user_folder + f"/{i}")/1024 ,2)
            date = os.path.getmtime(user_folder + f"/{i}")
            file_object['file_date_in_milliseconds'] = date
            file_object['file_date'] = datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d')
            file_object['path'] = file_path
            file_object['file_name'] = i
            files_list.append(file_object)
        else:
            if i == "temp":
                continue
            folders_list.append(i)
    totalSize = directorySize(f'{media_files}/files/{user_token}_files')
    folderSize = directorySize(f'{media_files}/files/{user_token}_files{path}')
    totalSize = totalSize/1024/1024
    folderSize = folderSize/1024/1024
    files_list = sorted(files_list, key=lambda i:i['file_date_in_milliseconds'], reverse=True)
    context = {
        'title': 'Files',
        'files': files_list,
        'folders': folders_list,
        'paths': paths,
        'contacts': Account.objects.all(),
        'totalSize': totalSize,
        'folderSize': folderSize,
    }
    shares = shareFile.objects.filter(sender_id=int(user_account.id))
    context['shares'] = shares
    return render(request, 'app/show_files.html', context)

def passwordResetRequestGet(request):
    if request.method == "POST":
        if request.POST.get('action') == 'passwordResetRequest':
            response = {}
            try:
                token=generate_random_string(50)
                email = request.POST.get('email')
                newRequest = passwordResetRequest(email=email, token=token)
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login('udayptl9@gmail.com', 'ahwoahunadxwpbvl')
                    subject = 'Password Reset Request'
                    body = f'Password Reset can be done by clicking here: {request.POST.get("hostName")}/passwordResetRequestProcess/{token}/ \n Team BIDS'
                    message = f'Subject: {subject} \n\n{body}'
                    smtp.sendmail('udayptl9@gmail.com', email, message)
                newRequest.save()
                response['text'] = 'true'
            except Exception as e:
                print(f'Error: {e}')
                response['text'] = 'false'
            return JsonResponse(response)

def passwordResetRequestProcess(request, token):
    if request.method == "POST":
        if request.POST.get('action') == 'passwordResetRequestProcess':
            response = {}
            response['text'] = 'false'
            email = request.POST.get('email')
            password = request.POST.get('password').encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            try:
                fetchRequestFilter = passwordResetRequest.objects.get(email=email, token=token)
                if fetchRequestFilter.requestUsed == False:
                    fetchRequestFilter.requestUsed = True
                    fetchRequestFilter.save()
                    userAccount = Account.objects.get(email=email)
                    userAccount.password = hashed_password.decode('utf-8')
                    userAccount.save()
                    response['text'] = 'true'
                    return JsonResponse(response)
                else:
                    response['text'] = 'false'
                    return JsonResponse(response)
            except Exception as e:
                print(f'Error: {e}')
                return JsonResponse(response)
    try:
        fetchRequest = passwordResetRequest.objects.get(token=token)
        if fetchRequest.requestUsed == True:
            messages.error(request, 'Link is already expired or does not exists')
            return redirect('logout_user')
    except:
        messages.error(request, "Link is already expired or doest not exists")
        return redirect('logout_user')
    return render(request, 'app/passwordResetRequestProcess.html', {'title': 'Password Reset', 'token': token})

def show_contacts(request):
    if request.method == "POST":
        if request.POST.get('action') == "send_user_data":
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = "+91" + request.POST.get('phone_number')
            client = Client(account_sid, auth_token)
            client.messages.create(
                body = f"ANVI Diagnostic Centre:\nYour account as been created successfully:\nLogin Details:\nEmail: {email}\nPassword: {password}",
                from_= '+14242303489',
                to = phone
            )
            response = {}
            response['text'] = 'true'
            return JsonResponse(response)
    context = {
        'title': 'Contacts',
    }
    return render(request, 'app/contacts.html', context)

def default_pdf(request):
    email = check_user(request)
    user_account = Account.objects.get(email = email)
    media_files = os.path.join(BASE_DIR, 'media')
    user_token = user_account.token
    tempFolder = media_files + "/files/" + user_token + "_files" + f'/temp/'
    if not os.path.exists(tempFolder):
        os.makedirs(tempFolder)
    if request.GET.get('action') == 'getPDF':
        paper_code = request.GET.get('paper_code')
        tempFileName = request.GET.get('tempFileName')
        path = request.GET.get('path')[4:]
        response = {}
        response['text'] = 'false'
        if os.path.exists(f'{tempFolder}/{tempFileName}'):
            destFolder = media_files + "/files/" + user_token + "_files/" + path
            shutil.move(f'{tempFolder}/{tempFileName}', f'{destFolder}/{tempFileName}')
            os.rename(f'{destFolder}/{tempFileName}', f'{destFolder}/{request.GET.get("file_name")}.pdf')
            response['text'] = 'true'
            response['file_name'] = request.GET.get("file_name")
        return JsonResponse(response)
    elif request.GET.get('action') == 'getPreview':
        response = {}
        response['text'] = 'false'
        paper_code = request.GET.get('paper_code')
        paper_code_linebreaks = [i for i in paper_code.split('\n')]
        email = request.GET.get('email')
        admin_email = request.session['user']['email']
        admin_user_account = Account.objects.get(email = admin_email)
        media_files = os.path.join(BASE_DIR, 'media')
        admin_token = admin_user_account.token
        fileNamePrefix = generate_random_string(50)
        html_file = media_files + "/files/" + admin_token + "_files" + f"/temp/{fileNamePrefix}.html"
        pdf_file = media_files + "/files/" + admin_token + "_files" + f"/temp/{fileNamePrefix}.pdf"
        if not os.path.exists(html_file):
            with open(f'{html_file}',"w") as f:
                for i in paper_code_linebreaks:
                    f.writelines(i + "\n")
                f.close()
        if not os.path.exists(pdf_file):
            doctor_code = request.GET.get('doctor_code')
            htmls_footer = media_files + f"/htmls/footer_{doctor_code}.html"
            htmls_header = media_files + "/htmls/header.html"
            pdfkit.from_file(html_file, pdf_file, {'--footer-html': f'{htmls_footer}', '--header-html': f'{htmls_header}'})
            baseDir = media_files + "/files/" + admin_token + "_files" + f"/temp/"
            test = os.listdir(baseDir)
            for item in test:
                if item.endswith(".html"):
                    os.remove(os.path.join(baseDir, item))
            webLink = "/media/files/" + admin_token + "_files" + f"/temp/{fileNamePrefix}.pdf"
            response['text'] = 'true'
            response['tempPdfPath'] = webLink
            response['pdfSize'] = os.path.getsize(pdf_file) // 1024
            response['tempFileName'] = f'{fileNamePrefix}.pdf'
        else:
            response['text'] = 'false'
        return JsonResponse(response)
    elif request.GET.get('action') == "share_file":
        response = {}
        response['text'] = 'false'
        email = request.GET.get('email')
        path = request.GET.get('path')
        doctor_name = request.GET.get('doctor_name')
        file_name = request.GET.get('file_name')
        file_path = request.GET.get('path', 'home')[4:]
        admin_email = request.session['user']['email']
        admin_user_account = Account.objects.get(email = admin_email)
        media_files = os.path.join(BASE_DIR, 'media')
        admin_token = admin_user_account.token
        sender_folder = "/media/files/" + admin_token + "_files" + file_path + f"/{file_name}.pdf"
        newshare = shareFile(sender_id=int(admin_user_account.id), receiver_id=email, file_path=sender_folder, file_name=file_name+".pdf", token=str(uuid.uuid4()), doctor_name=doctor_name)
        newshare.save()
        response['text'] = 'true'
        response['file_name'] = file_name + ".pdf"
        response['file_path'] = f"{sender_folder}"
        response['token'] = str(uuid.uuid4())
        return JsonResponse(response)
    elif request.GET.get('action') == "send_sms":
        response = {'text': 'false'}
        patient_number = request.GET.get('patient_number', 0)
        print(patient_number)
        if patient_number:
            file_name = request.GET.get('file_name')
            file_path = request.GET.get('path')[4:]
            sms_content = request.GET.get('sms_content')
            admin_email = request.session['user']['email']
            admin_user_account = Account.objects.get(email = admin_email)
            media_files = os.path.join(BASE_DIR, 'media')
            admin_token = admin_user_account.token
            original_url = request.GET.get('host_name') + "/media/files/" + admin_token + "_files" + file_path + f"/{file_name}.pdf"
            short_url = request.GET.get('host_name') + f"/{original_url}"
            client = Client(account_sid, auth_token)
            client.messages.create(
                body = f"{sms_content}\nLink: http://{short_url}",
                from_= '+14242303489',
                to = f"+91{patient_number}"
            )
            response['text'] = 'true'
        else:
            response['text'] = 'false'
        return JsonResponse(response)
    elif request.GET.get('action') == 'delete_user':
        uid = request.GET.get('uid')
        print(uid)
        newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post('https://us-central1-anvi-48aa3.cloudfunctions.net/deleteUser', json={"uid": uid}, headers=newHeaders)
        return JsonResponse(response)
    context = {
        'title': 'Create PDF',
    }
    return render(request, 'app/default_pdf.html', context)

def page_not_found(request):
    return render(request, 'app/404.html')
