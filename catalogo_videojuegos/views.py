from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.db import connection


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())