# -*- coding: utf-8 -*-
from django.contrib import admin

from models import FSVersion, DBVersion

# Register your models here.

@admin.register(FSVersion)
class FSVersionAdmin(admin.ModelAdmin):
    model = FSVersion


@admin.register(DBVersion)
class DBVersionAdmin(admin.ModelAdmin):
    model = DBVersion


