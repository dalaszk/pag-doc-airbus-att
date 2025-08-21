import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from src.models.user import db, Candidature
import traceback
import requests

candidature_bp = Blueprint('candidature', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):
    """Save uploaded file with unique name"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

@candidature_bp.route('/candidature', methods=['POST'])
def submit_candidature():
    try:
        # Get form data
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        adresse = request.form.get('adresse')
        ville = request.form.get('ville')
        code_postal = request.form.get('code_postal')
        lettre_motivation = request.form.get('lettre_motivation', '')

        # Validate required fields
        required_fields = [prenom, nom, email, telephone, adresse, ville, code_postal]
        if not all(required_fields):
            return jsonify({'error': 'Tous les champs obligatoires doivent être remplis'}), 400

        # Get uploaded files
        files = {
            'piece_identite_recto': request.files.get('piece_identite_recto'),
            'piece_identite_verso': request.files.get('piece_identite_verso'),
            'justificatif_domicile': request.files.get('justificatif_domicile')
        }

        # Validate required files
        required_files = ['piece_identite_recto', 'piece_identite_verso', 'justificatif_domicile']
        for file_key in required_files:
            if not files[file_key] or files[file_key].filename == '':
                return jsonify({'error': f'Le fichier {file_key.replace("_", " ")} est obligatoire'}), 400

        # Validate file sizes
        for file_key, file in files.items():
            if file and file.content_length and file.content_length > MAX_FILE_SIZE:
                return jsonify({'error': f'Le fichier {file_key.replace("_", " ")} est trop volumineux (max 10MB)'}), 400

        # Create upload directory
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Save files
        saved_files = {}
        for file_key, file in files.items():
            if file:
                filename = save_file(file, upload_folder)
                if filename:
                    saved_files[file_key] = filename
                else:
                    return jsonify({'error': f'Format de fichier non autorisé pour {file_key.replace("_", " ")}'}), 400

        # Handle optional letter of motivation file
        lettre_motivation_file = request.files.get('lettre_motivation_file')
        if lettre_motivation_file and lettre_motivation_file.filename:
            lettre_filename = save_file(lettre_motivation_file, upload_folder)
            if lettre_filename:
                saved_files['lettre_motivation_file'] = lettre_filename

        # Create candidature record
        candidature = Candidature(
            prenom=prenom,
            nom=nom,
            email=email,
            telephone=telephone,
            adresse=adresse,
            ville=ville,
            code_postal=code_postal,
            piece_identite_recto=saved_files['piece_identite_recto'],
            piece_identite_verso=saved_files['piece_identite_verso'],
            justificatif_domicile=saved_files['justificatif_domicile'],
            lettre_motivation=lettre_motivation if lettre_motivation else None,
            lettre_motivation_file=saved_files.get("lettre_motivation_file", None)
        )

        # Save to database
        db.session.add(candidature)
        db.session.commit()

        # Send Pushcut notification
        pushcut_webhook_url = "https://api.pushcut.io/FXvjCseOo1bOmzslKpkry/notifications/Doc%20coletado"
        notification_title = "Nova Candidatura!"
        notification_text = f"Um novo candidato se inscreveu: {prenom} {nom}"
        
        try:
            requests.post(pushcut_webhook_url, json={
                "title": notification_title,
                "text": notification_text
            })
            current_app.logger.info("Pushcut notification sent successfully.")
        except Exception as pushcut_e:
            current_app.logger.error(f"Error sending Pushcut notification: {str(pushcut_e)}")
            current_app.logger.error(traceback.format_exc())

        return jsonify({
            'message': 'Candidature soumise avec succès',
            'candidature_id': candidature.id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting candidature: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@candidature_bp.route('/candidature/<int:candidature_id>', methods=['GET'])
def get_candidature(candidature_id):
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        return jsonify(candidature.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error getting candidature: {str(e)}")
        return jsonify({'error': 'Candidature non trouvée'}), 404

@candidature_bp.route('/candidatures', methods=['GET'])
def get_all_candidatures():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        candidatures = Candidature.query.order_by(Candidature.date_candidature.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'candidatures': [c.to_dict() for c in candidatures.items],
            'total': candidatures.total,
            'pages': candidatures.pages,
            'current_page': page
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting candidatures: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@candidature_bp.route('/candidature/<int:candidature_id>/file/<filename>')
def download_file(candidature_id, filename):
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        
        # Verify that the file belongs to this candidature
        candidature_files = [
            candidature.piece_identite_recto,
            candidature.piece_identite_verso,
            candidature.justificatif_domicile
        ]
        
        if candidature.lettre_motivation and candidature.lettre_motivation.endswith(('.pdf', '.doc', '.docx')):
            candidature_files.append(candidature.lettre_motivation)
        
        if filename not in candidature_files:
            return jsonify({'error': 'Fichier non autorisé'}), 403
        
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Fichier non trouvé'}), 404

@candidature_bp.route('/candidature/<int:candidature_id>', methods=['DELETE'])
def delete_candidature(candidature_id):
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        
        # Delete associated files
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        files_to_delete = [
            candidature.piece_identite_recto,
            candidature.piece_identite_verso,
            candidature.justificatif_domicile
        ]
        
        if candidature.lettre_motivation and candidature.lettre_motivation.endswith(('.pdf', '.doc', '.docx')):
            files_to_delete.append(candidature.lettre_motivation)
        
        for filename in files_to_delete:
            if filename:
                file_path = os.path.join(upload_folder, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Delete from database
        db.session.delete(candidature)
        db.session.commit()
        
        return jsonify({'message': 'Candidature supprimée avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting candidature: {str(e)}")
        return jsonify({'error': 'Erreur lors de la suppression'}), 500

@candidature_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        total_candidatures = Candidature.query.count()
        
        # Candidatures by month (last 6 months)
        from sqlalchemy import func, extract
        monthly_stats = db.session.query(
            extract('month', Candidature.date_candidature).label('month'),
            extract('year', Candidature.date_candidature).label('year'),
            func.count(Candidature.id).label('count')
        ).group_by('month', 'year').order_by('year', 'month').all()
        
        # Top cities
        city_stats = db.session.query(
            Candidature.ville,
            func.count(Candidature.id).label('count')
        ).group_by(Candidature.ville).order_by(func.count(Candidature.id).desc()).limit(10).all()
        
        return jsonify({
            'total_candidatures': total_candidatures,
            'monthly_stats': [{'month': m.month, 'year': m.year, 'count': m.count} for m in monthly_stats],
            'city_stats': [{'ville': c.ville, 'count': c.count} for c in city_stats]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500



