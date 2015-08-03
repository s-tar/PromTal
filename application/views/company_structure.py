from application import Module, ldap, db
from flask import request, render_template, redirect, url_for, abort


structure = Module('company_structure', __name__, url_prefix='/structure')


@structure.get("/show")
def show_structure():
    return render_template('company_structure/show.html')