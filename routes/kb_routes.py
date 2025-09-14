import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from models import db
from models.knowledge_base import KnowledgeBase
from utils.file_parser import parse_file

kb_bp = Blueprint('kb', __name__)

UPLOAD_FOLDER = 'uploads/knowledge'
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'csv', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@kb_bp.route('/upload')
@login_required
def upload():
    # Get current knowledge base file if any
    current_kb = KnowledgeBase.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).order_by(KnowledgeBase.uploaded_at.desc()).first()
    
    return render_template('upload_kb.html', current_file=current_kb)

@kb_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash(_('Fayl tanlanmadi'), 'error')
        return redirect(request.url)
    
    file = request.files['file']
    additional_text = request.form.get('additional_text', '').strip()
    
    if file.filename == '':
        flash(_('Fayl tanlanmadi'), 'error')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        flash(_('Faqat PDF, DOCX, CSV, TXT fayllar qabul qilinadi'), 'error')
        return redirect(request.url)
    
    try:
        # Create user folder
        user_folder = os.path.join(UPLOAD_FOLDER, f'user_{current_user.id}')
        os.makedirs(user_folder, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        
        # Check file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        if file_size > MAX_FILE_SIZE_MB:
            os.remove(file_path)
            flash(_(f'Fayl hajmi {MAX_FILE_SIZE_MB}MB dan oshmasin'), 'error')
            return redirect(request.url)
        
        # Parse file content
        try:
            file_content = parse_file(file.read(), filename)
            file.seek(0)  # Reset file pointer after reading
        except Exception as e:
            os.remove(file_path)
            flash(_(f'Faylni tahlil qilishda xatolik: {str(e)}'), 'error')
            return redirect(request.url)
        
        # Add additional text if provided
        if additional_text:
            file_content = f"{file_content}\n\nQo'shimcha ma'lumot:\n{additional_text}"
        
        # Deactivate old knowledge base entries
        KnowledgeBase.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).update({'is_active': False})
        
        # Create new knowledge base entry
        kb = KnowledgeBase(
            user_id=current_user.id,
            file_name=filename,
            file_path=file_path,
            content=file_content
        )
        db.session.add(kb)
        db.session.commit()
        
        flash(_('Fayl muvaffaqiyatli yuklandi!'), 'success')
        
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        flash(_(f'Fayl yuklashda xatolik: {str(e)}'), 'error')
    
    return redirect(url_for('kb.upload'))

@kb_bp.route('/delete')
@login_required
def delete_file():
    # Get current knowledge base
    kb = KnowledgeBase.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).first()
    
    if kb:
        # Remove file from disk
        if os.path.exists(kb.file_path):
            os.remove(kb.file_path)
        
        # Remove from database
        db.session.delete(kb)
        db.session.commit()
        
        flash(_('Fayl o\'chirildi'), 'info')
    else:
        flash(_('Fayl topilmadi'), 'error')
    
    return redirect(url_for('kb.upload'))