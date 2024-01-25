from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from base.forms import AnnouncementForm, AnnouncementcommentForm
from base.models import Announcement, AnnouncementComment
from employee.models import EmployeeWorkInformation
from horilla.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from notifications.signals import notify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



@login_required
def announcement_view(request):

    """
    This method is used to render all announcemnts.
    """

    announcement_list = Announcement.objects.all().order_by('-created_on')

    # Set the number of items per page
    items_per_page = 10
    
    paginator = Paginator(announcement_list, items_per_page)
    
    page = request.GET.get('page')
    try:
        announcements = paginator.page(page)
    except PageNotAnInteger:
        # If the page is not an integer, deliver the first page.
        announcements = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page of results.
        announcements = paginator.page(paginator.num_pages)
    
    return render(request, "announcement/announcement.html", {'announcements': announcements})



@login_required
def create_announcement(request):
        
    """
    This method renders form and template to update Announcement
    """

    form = AnnouncementForm()
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            anou,attachment_ids = form.save(commit=False)
            anou.save()
            anou.attachments.set(attachment_ids)
            departments = form.cleaned_data["department"]
            job_positions = form.cleaned_data["job_position"]
            anou.department.set(departments)
            anou.job_position.set(job_positions)
            messages.success(request, _("Announcement created successfully."))

            depar = []
            jobs = []
            emp_dep = []
            emp_jobs = []
            for i in departments:
                depar.append(i.id)
            for i in job_positions:
                jobs.append(i.id)

            for i in depar:
                emp = EmployeeWorkInformation.objects.filter(department_id = i)
                for i in emp:
                    name = i.employee_id
                    emp_dep.append(name.employee_user_id)

            for i in jobs:
                emp = EmployeeWorkInformation.objects.filter(job_position_id = i)
                for i in emp:
                    name = i.employee_id
                    emp_jobs.append(name.employee_user_id)

            notify.send(
                request.user.employee_get,
                recipient=emp_dep,
                verb="Your department was mentioned in a post.",
                verb_ar="تم ذكر قسمك في منشور.",
                verb_de="Ihr Abteilung wurde in einem Beitrag erwähnt.",
                verb_es="Tu departamento fue mencionado en una publicación.",
                verb_fr="Votre département a été mentionné dans un post.",
                redirect="/announcement",
                icon="chatbox-ellipses",
            )

            notify.send(
                request.user.employee_get,
                recipient=emp_jobs,
                verb="Your job position was mentioned in a post.",
                verb_ar="تم ذكر وظيفتك في منشور.",
                verb_de="Ihre Arbeitsposition wurde in einem Beitrag erwähnt.",
                verb_es="Tu puesto de trabajo fue mencionado en una publicación.",
                verb_fr="Votre poste de travail a été mentionné dans un post.",
                redirect="/announcement",
                icon="chatbox-ellipses",
            )

            response = render(
                request, "announcement/announcement_form.html", {"form": form}
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(request, "announcement/announcement_form.html", {"form": form})


@login_required
def delete_announcement(request, anoun_id):

    """
    This method is used to delete announcemnts.
    """
    
    announcement = Announcement.objects.filter(id=anoun_id)
    announcement.delete()
    messages.success(request, _("Announcement deleted successfully."))
    return redirect(announcement_view)


@login_required
def update_announcement(request, anoun_id):

    """
    This method renders form and template to update Announcement
    """

    announcement = Announcement.objects.get(id=anoun_id)
    form = AnnouncementForm(instance = announcement)

    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            anou,attachment_ids = form.save(commit=False)
            announcement = anou.save()
            anou.attachments.set(attachment_ids)
            departments = form.cleaned_data["department"]
            job_positions = form.cleaned_data["job_position"]
            anou.department.set(departments)
            anou.job_position.set(job_positions)
            messages.success(request, _("Announcement updated successfully."))

            depar = []
            jobs = []
            emp_dep = []
            emp_jobs = []
            for i in departments:
                depar.append(i.id)
            for i in job_positions:
                jobs.append(i.id)

            for i in depar:
                emp = EmployeeWorkInformation.objects.filter(department_id = i)
                for i in emp:
                    name = i.employee_id
                    emp_dep.append(name.employee_user_id)

            for i in jobs:
                emp = EmployeeWorkInformation.objects.filter(job_position_id = i)
                for i in emp:
                    name = i.employee_id
                    emp_jobs.append(name.employee_user_id)

            notify.send(
                request.user.employee_get,
                recipient=emp_dep,
                verb="Your department was mentioned in a post.",
                verb_ar="تم ذكر قسمك في منشور.",
                verb_de="Ihr Abteilung wurde in einem Beitrag erwähnt.",
                verb_es="Tu departamento fue mencionado en una publicación.",
                verb_fr="Votre département a été mentionné dans un post.",
                redirect="/announcement",
                icon="chatbox-ellipses",
            )

            notify.send(
                request.user.employee_get,
                recipient=emp_jobs,
                verb="Your job position was mentioned in a post.",
                verb_ar="تم ذكر وظيفتك في منشور.",
                verb_de="Ihre Arbeitsposition wurde in einem Beitrag erwähnt.",
                verb_es="Tu puesto de trabajo fue mencionado en una publicación.",
                verb_fr="Votre poste de travail a été mentionné dans un post.",
                redirect="/announcement",
                icon="chatbox-ellipses",
            )

            response = render(
                request, "announcement/announcement_update_form.html", {"form": form}
            )
            return HttpResponse(
                response.content.decode("utf-8") + "<script>location.reload();</script>"
            )
    return render(request, "announcement/announcement_update_form.html", {"form": form})


@login_required
def create_announcement_comment(request, anoun_id):
    """
    This method renders form and template to create Announcement comments
    """
    anoun = Announcement.objects.filter(id=anoun_id).first()
    emp = request.user.employee_get
    form = AnnouncementcommentForm(
        initial={"employee_id": emp.id, "request_id": anoun_id}
    )

    if request.method == "POST":
        form = AnnouncementcommentForm(request.POST)
        if form.is_valid():
            form.instance.employee_id = emp
            form.instance.announcement_id = anoun
            form.save()
            form = AnnouncementcommentForm(
                initial={"employee_id": emp.id, "request_id": anoun_id}
            )
            messages.success(request, _("You commented a post."))
            return HttpResponse("<script>window.location.reload()</script>")
    return render(
        request,
        "announcement/comment_form.html",
        {"form": form, "request_id": anoun_id},
    )


@login_required
def comment_view(request, anoun_id):
    """
    This method is used to view all comments in the announcements
    """
    comments = AnnouncementComment.objects.filter(announcement_id=anoun_id).order_by(
        "-created_at"
    )
    no_comments = False
    if not comments.exists():
        no_comments = True

    return render(
        request,
        "announcement/comment_view.html",
        {"comments": comments, "no_comments": no_comments},
    )
