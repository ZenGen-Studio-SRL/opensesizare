from django.shortcuts import get_object_or_404, redirect, render

from .forms import PetitionForm
from .models import Municipality, Petition


def municipality_list(request):
    municipalities = Municipality.objects.filter(is_active=True)
    return render(request, "petitions/index.html", {"municipalities": municipalities})


def submit(request, slug):
    municipality = get_object_or_404(Municipality, slug=slug, is_active=True)
    form = PetitionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        petition = form.save(commit=False)
        petition.municipality = municipality
        petition.save()
        return redirect("petitions:status", code=petition.tracking_code)
    return render(request, "petitions/submit.html", {"form": form, "municipality": municipality})


def status(request, code):
    petition = get_object_or_404(Petition, tracking_code=code)
    return render(request, "petitions/status.html", {"petition": petition})
