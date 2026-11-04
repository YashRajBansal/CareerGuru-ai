import csv
import io
import json
from datetime import timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, Response, abort
from flask_login import current_user
from flask_mail import Message
from sqlalchemy import func, or_
from app import db, mail, limiter, now, User, Professional, Career, Knowledge, ReviewQuery, AuditLog, CareerView, Conversation, Assessment, Resume, SavedCareer
from routes import admin_required, field, audit
from services import ai

def register_admin(app):
    @app.route('/adlanding')
    @app.route('/admin')
    @admin_required
    def admin():
        return render_template('admin/dashboard.html', users=User.query.count(), bookings=Professional.query.count(), pending=ReviewQuery.query.filter_by(resolved=False).count(), career_count=Career.query.count(), audit=AuditLog.query.order_by(AuditLog.id.desc()).limit(8).all())

    @app.get('/api/admin/analytics')
    @admin_required
    def admin_analytics():
        days = [(now().date()-timedelta(days=i)).isoformat() for i in reversed(range(14))]
        def series(model, column):
            values = dict(db.session.query(func.date(column),func.count(model.id)).filter(column >= now()-timedelta(days=14)).group_by(func.date(column)).all())
            return [values.get(day,0) for day in days]
        popular = db.session.query(Career.title, func.count(CareerView.id)).join(CareerView, Career.id==CareerView.career_id).group_by(Career.id).order_by(func.count(CareerView.id).desc()).limit(5).all()
        return jsonify(labels=days, signups=series(User,User.created_at), bookings=series(Professional,Professional.timestamp), unanswered=series(ReviewQuery,ReviewQuery.created_at), popular=[{'title':title,'views':count} for title,count in popular])

    @app.route('/admin/careers', methods=['GET','POST'])
    @admin_required
    def admin_careers():
        if request.method == 'POST':
            row = db.session.get(Career, request.form.get('id', type=int)) if request.form.get('id') else Career()
            if row is None:
                abort(404)
            title = field('title', length=120)
            duplicate = Career.query.filter(Career.title==title, Career.id != row.id).first()
            if duplicate:
                flash('A career with that title already exists.', 'error')
                return redirect(url_for('admin_careers'))
            for key in ('title','cluster','skills','traits','education','description','outlook','source'):
                setattr(row,key,field(key,length=2000 if key not in ('title','cluster') else 120 if key=='title' else 100))
            row.embedding = None
            row.embedding_model = None
            db.session.add(row)
            audit('Saved career: '+title)
            db.session.commit()
            flash('Career saved. Local text matching uses the updated profile immediately.', 'success')
            return redirect(url_for('admin_careers'))
        edit = db.session.get(Career,request.args.get('edit',type=int)) if request.args.get('edit') else None
        return render_template('admin/content.html', kind='careers', rows=Career.query.order_by(Career.position, Career.title).all(), edit=edit)

    @app.post('/admin/careers/<int:identifier>/delete')
    @admin_required
    def admin_career_delete(identifier):
        row = db.get_or_404(Career,identifier)
        SavedCareer.query.filter_by(career_id=identifier).delete()
        CareerView.query.filter_by(career_id=identifier).delete()
        audit('Deleted career: '+row.title)
        db.session.delete(row)
        db.session.commit()
        flash('Career deleted.', 'success')
        return redirect(url_for('admin_careers'))

    @app.post('/api/admin/careers/reorder')
    @admin_required
    def reorder_careers():
        ids = (request.get_json() or {}).get('ids')
        existing = {r.id:r for r in Career.query.all()}
        if not isinstance(ids,list) or any(type(i) is not int for i in ids) or len(ids)!=len(existing) or set(ids)!=set(existing):
            return jsonify(error='Submit each career exactly once.'),400
        for index, identifier in enumerate(ids):
            existing[identifier].position = index
        audit('Reordered career library')
        db.session.commit()
        return jsonify(ok=True)

    @app.route('/admin/knowledge', methods=['GET','POST'])
    @admin_required
    def admin_knowledge():
        if request.method == 'POST':
            row = db.get_or_404(Knowledge,request.form.get('id',type=int)) if request.form.get('id') else Knowledge()
            row.title = field('title', length=160)
            row.content = field('content', length=6000)
            row.embedding = None
            row.embedding_model = None
            db.session.add(row)
            audit('Saved knowledge: '+row.title)
            db.session.commit()
            flash('Knowledge saved. Local text retrieval uses the updated entry immediately.', 'success')
            return redirect(url_for('admin_knowledge'))
        edit = db.session.get(Knowledge,request.args.get('edit',type=int)) if request.args.get('edit') else None
        return render_template('admin/content.html', kind='knowledge', rows=Knowledge.query.order_by(Knowledge.id).all(), edit=edit)

    @app.post('/admin/knowledge/<int:identifier>/delete')
    @admin_required
    def admin_knowledge_delete(identifier):
        row = db.get_or_404(Knowledge,identifier)
        audit('Deleted knowledge: '+row.title)
        db.session.delete(row)
        db.session.commit()
        flash('Knowledge entry deleted.', 'success')
        return redirect(url_for('admin_knowledge'))

    @app.post('/admin/embeddings')
    @admin_required
    @limiter.limit('2 per hour')
    def admin_embeddings():
        try:
            ai.refresh_embeddings(Career.query.all()+Knowledge.query.all())
            audit('Rebuilt local career and knowledge text index')
            db.session.commit()
            flash('Local text index rebuilt. No cloud service was used.', 'success')
        except Exception:
            db.session.rollback()
            flash('Could not rebuild the local text index. Please retry.', 'error')
        return redirect(url_for('admin_careers'))

    @app.route('/admin/users')
    @app.route('/userdisplay')
    @admin_required
    def userdisplay():
        search = request.args.get('q','')[:100]
        query = User.query
        if search:
            query = query.filter(or_(User.username.ilike('%'+search+'%'),User.email.ilike('%'+search+'%')))
        role = request.args.get('role','')
        if role in ('admin','student'):
            query = query.filter_by(is_admin=role=='admin')
        rows = query.order_by(User.id.desc()).all()
        if request.args.get('export') == 'csv':
            return export('career-guru-users.csv', ['id','username','email','role'], [[r.id,r.username,r.email,'admin' if r.is_admin else 'student'] for r in rows])
        return render_template('admin/table.html', kind='users', rows=rows, search=search)

    @app.route('/admin/bookings')
    @app.route('/calldisplay')
    @admin_required
    def display_professionals():
        search = request.args.get('q','')[:100]
        query = Professional.query
        if search:
            query = query.filter(or_(Professional.name.ilike('%'+search+'%'),Professional.area_of_interest.ilike('%'+search+'%'),Professional.email.ilike('%'+search+'%')))
        status = request.args.get('status','')
        if status in ('pending','confirmed','completed','cancelled'):
            query = query.filter_by(status=status)
        rows = query.order_by(Professional.id.desc()).all()
        if request.args.get('export') == 'csv':
            return export('career-guru-bookings.csv',['id','name','email','interest','availability','status'],[[r.id,r.name,r.email,r.area_of_interest,r.availability,r.status] for r in rows])
        return render_template('admin/table.html', kind='bookings', rows=rows, search=search)

    @app.post('/admin/bulk/<kind>')
    @admin_required
    def admin_bulk(kind):
        ids = request.form.getlist('ids',type=int)
        action = field('action',length=30)
        if not ids:
            flash('Select at least one row.', 'error')
        elif kind == 'bookings' and action in ('confirmed','completed','cancelled','pending'):
            for row in Professional.query.filter(Professional.id.in_(ids)):
                row.status = action
            audit(f'Updated booking IDs {ids[:50]} to {action}')
            db.session.commit()
            flash('Bookings updated.', 'success')
        elif kind == 'users' and action == 'delete':
            rows = User.query.filter(User.id.in_(ids)).all()
            if any(r.is_admin or r.id==current_user.id for r in rows):
                flash('Administrator accounts cannot be deleted here.', 'error')
            else:
                for row in rows:
                    for conversation in Conversation.query.filter_by(user_id=row.id):
                        db.session.delete(conversation)
                    for model in (Assessment,Resume,SavedCareer,ReviewQuery):
                        model.query.filter_by(user_id=row.id).delete()
                    # Preserve consultation records for staff; detach ownership.
                    Professional.query.filter_by(user_id=row.id).update({'user_id':None})
                    db.session.delete(row)
                audit(f'Deleted user IDs {ids[:50]}')
                db.session.commit()
                flash('Selected users and their private AI records deleted.', 'success')
        else:
            abort(400)
        return redirect(url_for('userdisplay' if kind=='users' else 'display_professionals'))

    @app.post('/delete/<int:identifier>')
    @admin_required
    def deletecall(identifier):
        row = db.get_or_404(Professional,identifier)
        db.session.delete(row)
        audit(f'Deleted consultation {identifier}')
        db.session.commit()
        flash('Consultation deleted.', 'success')
        return redirect(url_for('display_professionals'))

    @app.post('/deleteu/<int:identifier>')
    @admin_required
    def deleteuser(identifier):
        # Use the reviewed bulk workflow so private dependent records are removed too.
        abort(400, description='Select this user in the user table and use Delete selected.')

    @app.route('/admin/queue', methods=['GET','POST'])
    @admin_required
    def admin_queue():
        if request.method == 'POST':
            row = db.get_or_404(ReviewQuery,request.form.get('id',type=int))
            row.resolution = field('resolution',length=3000)
            row.resolved = True
            audit(f'Resolved review query {row.id}')
            db.session.commit()
            flash('Query resolved. Add any reusable guidance to the knowledge base.', 'success')
            return redirect(url_for('admin_queue'))
        return render_template('admin/queue.html', rows=ReviewQuery.query.order_by(ReviewQuery.resolved,ReviewQuery.id.desc()).all())

    @app.get('/admin/audit')
    @admin_required
    def admin_audit():
        return render_template('admin/audit.html', rows=AuditLog.query.order_by(AuditLog.id.desc()).limit(500).all())

    @app.route('/mail')
    @admin_required
    def mail_form():
        return render_template('admin/mail.html', booking=db.get_or_404(Professional,request.args.get('id',type=int)))

    @app.post('/send_mail')
    @admin_required
    @limiter.limit('10 per hour')
    def send_mail():
        booking = db.get_or_404(Professional,request.form.get('booking_id',type=int))
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            flash('Email is not configured. Add new mail credentials to app/.env.', 'error')
            return redirect(url_for('mail_form',id=booking.id))
        message = Message(subject='Career Guru consultation', recipients=[booking.email])
        message.body = f'Hello {booking.name},\n\nProposed date and time: '+field('datetime',length=120)+'\n\n'+field('message',length=3000)
        try:
            mail.send(message)
            booking.status = 'confirmed'
            audit(f'Sent consultation email for booking {booking.id}')
            db.session.commit()
            flash('Email sent and consultation confirmed.', 'success')
        except Exception:
            db.session.rollback()
            flash('Email delivery failed. Check mail configuration and try again.', 'error')
        return redirect(url_for('display_professionals'))

    @app.post('/admin/bookings/<int:identifier>/summarize')
    @admin_required
    @limiter.limit('10 per hour')
    def summarize_booking(identifier):
        row = db.get_or_404(Professional,identifier)
        if ai.GENERATION_LOCKED:
            flash(ai.FUTURE_MESSAGE, 'info')
            return redirect(url_for('display_professionals'))
        try:
            response = ai.complete(ai.SAFETY+'Return only JSON with summary (a short string) and urgency (normal or time-sensitive). Urgency refers only to an explicit near-term education or interview deadline. Do not infer medical urgency.', json.dumps({'interest':row.area_of_interest,'challenges':row.current_challenges,'outcome':row.desired_outcome,'availability':row.availability}))
            data = json.loads(response.removeprefix('```json').removesuffix('```').strip())
            row.summary = str(data['summary'])[:1500]
            row.urgency = data['urgency'] if data.get('urgency') in ('normal','time-sensitive') else 'normal'
            audit(f'AI triage for consultation {row.id}')
            db.session.commit()
            flash('Summary and urgency updated. Review the original request before acting.', 'success')
        except Exception:
            db.session.rollback()
            flash('Local AI triage unavailable. Start the local model and retry. The original request remains available.', 'error')
        return redirect(url_for('display_professionals'))

def export(filename, columns, rows):
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(columns)
    def safe(value):
        value = str(value if value is not None else '')
        return "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r')) else value
    writer.writerows([[safe(value) for value in row] for row in rows])
    audit('Exported '+filename)
    db.session.commit()
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition':f'attachment; filename="{filename}"'})
