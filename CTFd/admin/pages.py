from flask import current_app as app, render_template, request, redirect, jsonify, url_for, Blueprint
from CTFd.utils.decorators import admins_only
from CTFd.models import db, Teams, Solves, Awards, Challenges, Fails, Flags, Tags, Files, Tracking, Pages, Configs

from CTFd.utils import config, validators, cache, markdown, uploads
from CTFd.admin import admin


@admin.route('/admin/pages', methods=['GET', 'POST'])
@admins_only
def admin_pages_list():
    pages = Pages.query.all()
    return render_template('admin/pages.html', pages=pages)


@admin.route('/admin/pages/new', methods=['GET', 'POST'])
@admins_only
def admin_pages_new():
    if request.method == 'GET':
        return render_template('admin/editor.html')
    elif request.method == 'POST':
        page_form_id = request.form.get('id')
        title = request.form['title']
        html = request.form['html']
        route = request.form['route'].lstrip('/')
        auth_required = 'auth_required' in request.form

        page_op = request.args.get('operation')

        if page_op == 'preview':
            page = Pages(title, route, html, draft=False)
            return render_template('page.html', content=markdown(page.content))

        page = Pages.query.filter_by(id=page_form_id).first()

        errors = []
        if not route:
            errors.append('Missing URL route')

        if errors:
            page = Pages(title, html, route)
            return render_template('/admin/editor.html', page=page)

        if page:
            page.title = title
            page.route = route
            page.content = html
            page.auth_required = auth_required

            if page_op == 'publish':
                page.draft = False

            db.session.commit()

            data = {
                'result': 'success',
                'operation': page_op,
                'page': {
                    'id': page.id,
                    'route': page.route,
                    'title': page.title
                }
            }

            db.session.close()
            cache.clear()
            return jsonify(data)

        if page_op == 'publish':
            page = Pages(title, route, html, draft=False, auth_required=auth_required)
        elif page_op == 'save':
            page = Pages(title, route, html, auth_required=auth_required)

        db.session.add(page)
        db.session.commit()

        data = {
            'result': 'success',
            'operation': page_op,
            'page': {
                'id': page.id,
                'route': page.route,
                'title': page.title
            }
        }

        db.session.close()
        cache.clear()

        return jsonify(data)


@admin.route('/admin/pages/<int:page_id>', methods=['GET', 'POST'])
@admins_only
def admin_pages_detail(page_id):
    page = Pages.query.filter_by(id=page_id).first_or_404()
    page_op = request.args.get('operation')

    if request.method == 'GET' and page_op == 'preview':
        return render_template('page.html', content=markdown(page.content))

    if request.method == 'GET' and page_op == 'create':
        return render_template('admin/editor.html')

    return render_template('admin/editor.html', page=page)


@admin.route('/admin/media', methods=['GET', 'POST', 'DELETE'])
@admins_only
def admin_pages_media():
    # TODO: Maybe move to API?
    if request.method == 'POST':
        files = request.files.getlist('files[]')

        uploaded = []
        for f in files:
            data = uploads.upload_file(file=f, chalid=None)
            if data:
                uploaded.append({'id': data[0], 'location': data[1]})
        return jsonify({'results': uploaded})
    elif request.method == 'DELETE':
        file_ids = request.form.getlist('file_ids[]')
        for file_id in file_ids:
            uploads.delete_file(file_id)
        return True
    else:
        files = [{'id': f.id, 'location': f.location} for f in Files.query.filter_by(chal=None).all()]
        return jsonify({'results': files})
