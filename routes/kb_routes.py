import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models.knowledge_base import KnowledgeBase
from utils.file_parser import parse_file_content, is_allowed_file, get_file_size_mb

kb_bp = Blueprint('kb', __name__)

MAX_FILE_SIZE_MB = 10

@kb_bp.route('/upload-kb', methods=['GET', 'POST'])
def upload_kb():
    # Foydalanuvchi tizimga kirganligini tekshirish
    if 'user_id' not in session:
        flash('Fayl yuklash uchun tizimga kiring', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        # Fayl va matn maydonini olish
        file = request.files.get('file')
        additional_text = request.form.get('additional_text', '').strip()
        
        if not file or not file.filename or file.filename == '':
            flash('Fayl tanlanmadi', 'error')
            return render_template('upload_kb.html')
        
        # Fayl turi tekshirish
        if not is_allowed_file(file.filename):
            flash('Faqat PDF, DOCX, CSV, TXT fayllar qabul qilinadi', 'error')
            return render_template('upload_kb.html')
        
        # Xavfsiz fayl nomi yaratish
        filename = secure_filename(file.filename)
        
        # Foydalanuvchi papkasini yaratish
        user_folder = os.path.join('uploads', 'knowledge', f'user_{user_id}')
        os.makedirs(user_folder, exist_ok=True)
        
        # Fayl yo'lini aniqlash
        file_path = os.path.join(user_folder, filename)
        
        try:
            # Faylni vaqtincha saqlash
            file.save(file_path)
            
            # Fayl hajmini tekshirish
            file_size_mb = get_file_size_mb(file_path)
            if file_size_mb > MAX_FILE_SIZE_MB:
                os.remove(file_path)  # Faylni o'chirish
                flash(f'Fayl hajmi {MAX_FILE_SIZE_MB}MB dan oshmasin. Sizning faylingiz: {file_size_mb}MB', 'error')
                return render_template('upload_kb.html')
            
            # Faylni matnga aylantiradigan
            try:
                file_content = parse_file_content(file_path, filename)
            except Exception as e:
                os.remove(file_path)  # Faylni o'chirish
                flash(f'Faylni tahlil qilishda xatolik: {str(e)}', 'error')
                return render_template('upload_kb.html')
            
            # Qo'shimcha matn qo'shish
            if additional_text:
                file_content = f"{file_content}\n\nQo'shimcha ma'lumot:\n{additional_text}"
            
            # Eski faylni o'chirish (foydalanuvchi faqat bitta fayl saqlashi kerak)
            old_kb = KnowledgeBase.find_by_user_id(user_id)
            if old_kb and old_kb.file_path:
                # Eski faylni disk dan o'chirish
                try:
                    if os.path.exists(old_kb.file_path):
                        os.remove(old_kb.file_path)
                except:
                    pass  # Fayl allaqachon o'chirilgan bo'lishi mumkin
                
                # Ma'lumotlar bazasidan o'chirish
                KnowledgeBase.delete_by_user_id(user_id)
            
            # Yangi faylni ma'lumotlar bazasiga saqlash
            kb = KnowledgeBase(
                user_id=user_id,
                file_name=filename,
                file_path=file_path,
                content=file_content
            )
            kb.save()
            
            flash(f'Fayl muvaffaqiyatli yuklandi! Hajmi: {file_size_mb}MB', 'success')
            return render_template('upload_kb.html', 
                                 current_file=kb,
                                 file_size=file_size_mb)
        
        except Exception as e:
            # Xatolik bo'lsa faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
            flash(f'Fayl yuklashda xatolik: {str(e)}', 'error')
            return render_template('upload_kb.html')
    
    # GET so'rovi uchun - mavjud faylni ko'rsatish
    current_kb = KnowledgeBase.find_by_user_id(user_id)
    file_size = None
    if current_kb and current_kb.file_path and os.path.exists(current_kb.file_path):
        file_size = get_file_size_mb(current_kb.file_path)
    
    return render_template('upload_kb.html', 
                         current_file=current_kb,
                         file_size=file_size)