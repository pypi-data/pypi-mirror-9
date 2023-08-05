# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
    
class FSVersion(models.Model):
    class Meta:
        verbose_name = "File System Version"
        verbose_name_plural = "File System Versions"
        db_table = 'py_versioning_fs_version'
    
    id = models.AutoField(primary_key = True)        
    name = models.CharField(max_length = 255, verbose_name = u"Name / Number")
    json = models.TextField(verbose_name = u"JSON data")
    hash = models.CharField(max_length = 255, verbose_name = u"Hash data")
    date = models.DateField(verbose_name = u"Created")
        
    def __unicode__(self):
        return self.name
    
    
    
class DBVersion(models.Model):
    class Meta:
        verbose_name = "Database Version"
        verbose_name_plural = "Database Versions"
        db_table = 'py_versioning_db_version'
    
    id = models.AutoField(primary_key = True)        
    name = models.CharField(max_length=255, verbose_name = u"Name / Number")
    json = models.TextField(verbose_name = u"JSON data")
    date = models.DateField(verbose_name = u"Created")
        
    def __unicode__(self):
        return self.name
       
    