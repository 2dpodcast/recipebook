from flask import render_template

from recipebook.admin import admin

@admin.route('/')
def adminindex():
    return render_template('admin/admin.html')
