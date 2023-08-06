# -*- coding: utf-8 -*-
#Common
import os

# file_cleanup
from django.core.files.storage import default_storage
from django.db.models import FileField

# OverwriteStorage
from django.conf import settings
 
def file_cleanup(sender, **kwargs):
    """
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.
 
    Usage:
    >>> from django.db.models.signals import post_delete
    >>> post_delete.connect(file_cleanup, sender=MyModel, dispatch_uid="mymodel.file_cleanup")
    """
    for fieldname in sender._meta.get_all_field_names():
        try:
            field = sender._meta.get_field(fieldname)
        except:
            field = None
        if field and isinstance(field, FileField):
            inst = kwargs['instance']
            f = getattr(inst, fieldname)
            m = inst.__class__._default_manager
            if hasattr(f, 'path') and os.path.exists(f.path)\
            and not m.filter(**{'%s__exact' % fieldname: getattr(inst, fieldname)})\
            .exclude(pk=inst._get_pk_val()):
                try:
                    default_storage.delete(f.path)
                except:
                    pass


from django.core.files.storage import FileSystemStorage
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.
 
        Found at http://djangosnippets.org/snippets/976/
 
        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):
 
        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name