Add this to your project's urls.py to read the custom admin index
file:

from django.contrib import admin
admin.site.index_template = 'admin/admin_index.html'
