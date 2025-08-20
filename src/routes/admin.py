import os
from flask import Blueprint, render_template_string, request, jsonify, current_app, send_from_directory, session, redirect, url_for
from src.models.user import db, Candidature
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Credenciais de login
ADMIN_USERNAME = 'senhalogin'
ADMIN_PASSWORD = 'senha'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# Simple admin template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airbus - Painel Administrativo</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #0066cc, #004499);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 1.5rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #0066cc;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #6c757d;
            font-weight: 500;
        }
        
        .controls {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            min-width: 300px;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #0066cc;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: #0066cc;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0052a3;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .candidatures-table {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .table-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e9ecef;
            font-weight: 600;
            color: #495057;
        }
        
        .table-content {
            max-height: 600px;
            overflow-y: auto;
        }
        
        .candidature-row {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #f1f3f4;
            transition: background 0.2s ease;
        }
        
        .candidature-row:hover {
            background: #f8f9fa;
        }
        
        .candidature-info {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: 1rem;
            align-items: center;
        }
        
        .candidate-name {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .candidate-email {
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .candidate-phone {
            color: #495057;
            font-size: 0.9rem;
        }
        
        .candidate-date {
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .actions {
            display: flex;
            gap: 0.5rem;
        }
        
        .btn-sm {
            padding: 0.4rem 0.8rem;
            font-size: 0.8rem;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 2rem;
        }
        
        .page-btn {
            padding: 0.5rem 1rem;
            border: 1px solid #dee2e6;
            background: white;
            color: #495057;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .page-btn:hover {
            background: #e9ecef;
        }
        
        .page-btn.active {
            background: #0066cc;
            color: white;
            border-color: #0066cc;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #6c757d;
        }
        
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6c757d;
        }
        
        .detail-grid {
            display: grid;
            gap: 1rem;
        }
        
        .detail-item {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 1rem;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .detail-label {
            font-weight: 600;
            color: #495057;
        }
        
        .detail-value {
            color: #2c3e50;
        }
        
        .file-link {
            color: #0066cc;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .file-link:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 0 1rem;
            }
            
            .candidature-info {
                grid-template-columns: 1fr;
                gap: 0.5rem;
            }
            
            .controls {
                flex-direction: column;
                align-items: stretch;
            }
            
            .search-input {
                min-width: auto;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <i class="fas fa-plane"></i>
            Airbus - Painel Administrativo
        </h1>
    </div>
    
    <div class="container">
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-number" id="totalCandidatures">-</div>
                <div class="stat-label">Total de Candidaturas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="todayCandidatures">-</div>
                <div class="stat-label">Hoje</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="weekCandidatures">-</div>
                <div class="stat-label">Esta Semana</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="monthCandidatures">-</div>
                <div class="stat-label">Este Mês</div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-input" id="searchInput" placeholder="Buscar por nome, email ou telefone...">
            <button class="btn btn-primary" onclick="searchCandidatures()">
                <i class="fas fa-search"></i> Buscar
            </button>
            <button class="btn btn-secondary" onclick="exportData()">
                <i class="fas fa-download"></i> Exportar
            </button>
            <button class="btn btn-primary" onclick="refreshData()">
                <i class="fas fa-sync-alt"></i> Atualizar
            </button>
        </div>
        
        <div class="candidatures-table">
            <div class="table-header">
                Candidaturas Recebidas
            </div>
            <div class="table-content" id="candidaturesContent">
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Carregando candidaturas...
                </div>
            </div>
        </div>
        
        <div class="pagination" id="pagination"></div>
    </div>
    
    <!-- Modal for candidature details -->
    <div class="modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Detalhes da Candidatura</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalContent"></div>
        </div>
    </div>
    
    <script>
        let currentPage = 1;
        let totalPages = 1;
        let searchQuery = '';
        
        // Load initial data
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadCandidatures();
        });
        
        // Search functionality
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchCandidatures();
            }
        });
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('totalCandidatures').textContent = data.total_candidatures || 0;
                
                // Calculate today, week, month stats (simplified)
                document.getElementById('todayCandidatures').textContent = '0';
                document.getElementById('weekCandidatures').textContent = '0';
                document.getElementById('monthCandidatures').textContent = data.total_candidatures || 0;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadCandidatures(page = 1) {
            try {
                currentPage = page;
                const url = `/api/candidatures?page=${page}&per_page=10${searchQuery ? '&search=' + encodeURIComponent(searchQuery) : ''}`;
                const response = await fetch(url);
                const data = await response.json();
                
                displayCandidatures(data.candidatures || []);
                updatePagination(data.current_page || 1, data.pages || 1);
            } catch (error) {
                console.error('Error loading candidatures:', error);
                document.getElementById('candidaturesContent').innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erro ao carregar candidaturas</p>
                    </div>
                `;
            }
        }
        
        function displayCandidatures(candidatures) {
            const content = document.getElementById('candidaturesContent');
            
            if (candidatures.length === 0) {
                content.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>Nenhuma candidatura encontrada</p>
                    </div>
                `;
                return;
            }
            
            content.innerHTML = candidatures.map(candidature => `
                <div class="candidature-row">
                    <div class="candidature-info">
                        <div>
                            <div class="candidate-name">${candidature.prenom} ${candidature.nom}</div>
                            <div class="candidate-email">${candidature.email}</div>
                        </div>
                        <div class="candidate-phone">${candidature.telephone}</div>
                        <div>${candidature.ville}</div>
                        <div class="candidate-date">${new Date(candidature.date_candidature).toLocaleDateString('fr-FR')}</div>
                        <div class="actions">
                            <button class="btn btn-primary btn-sm" onclick="viewDetails(${candidature.id})">
                                <i class="fas fa-eye"></i> Ver
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="deleteCandidature(${candidature.id})">
                                <i class="fas fa-trash"></i> Excluir
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        function updatePagination(current, total) {
            totalPages = total;
            const pagination = document.getElementById('pagination');
            
            if (total <= 1) {
                pagination.innerHTML = '';
                return;
            }
            
            let html = '';
            
            // Previous button
            if (current > 1) {
                html += `<button class="page-btn" onclick="loadCandidatures(${current - 1})">
                    <i class="fas fa-chevron-left"></i>
                </button>`;
            }
            
            // Page numbers
            for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
                html += `<button class="page-btn ${i === current ? 'active' : ''}" onclick="loadCandidatures(${i})">
                    ${i}
                </button>`;
            }
            
            // Next button
            if (current < total) {
                html += `<button class="page-btn" onclick="loadCandidatures(${current + 1})">
                    <i class="fas fa-chevron-right"></i>
                </button>`;
            }
            
            pagination.innerHTML = html;
        }
        
        async function viewDetails(candidatureId) {
            try {
                const response = await fetch(`/api/candidature/${candidatureId}`);
                const candidature = await response.json();
                
                const modalContent = document.getElementById('modalContent');
                modalContent.innerHTML = `
                    <div class="detail-grid">
                        <div class="detail-item">
                            <div class="detail-label">Nome:</div>
                            <div class="detail-value">${candidature.prenom} ${candidature.nom}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Email:</div>
                            <div class="detail-value">${candidature.email}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Telefone:</div>
                            <div class="detail-value">${candidature.telephone}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">SIP:</div>
                            <div class="detail-value">${candidature.sip}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Endereço:</div>
                            <div class="detail-value">${candidature.adresse}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Cidade:</div>
                            <div class="detail-value">${candidature.ville}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">CEP:</div>
                            <div class="detail-value">${candidature.code_postal}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Data:</div>
                            <div class="detail-value">${new Date(candidature.date_candidature).toLocaleString('fr-FR')}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Documentos:</div>
                            <div class="detail-value">
                                <a href="/api/candidature/${candidature.id}/file/${candidature.piece_identite_recto}" class="file-link" target="_blank">
                                    <i class="fas fa-file"></i> Identidade (frente)
                                </a><br>
                                <a href="/api/candidature/${candidature.id}/file/${candidature.piece_identite_verso}" class="file-link" target="_blank">
                                    <i class="fas fa-file"></i> Identidade (verso)
                                </a><br>
                                <a href="/api/candidature/${candidature.id}/file/${candidature.justificatif_domicile}" class="file-link" target="_blank">
                                    <i class="fas fa-file"></i> Comprovante de residência
                                </a><br>
                                <a href="/api/candidature/${candidature.id}/file/${candidature.cv}" class="file-link" target="_blank">
                                    <i class="fas fa-file"></i> CV
                                </a>
                            </div>
                        </div>
                        ${candidature.lettre_motivation ? `
                        <div class="detail-item">
                            <div class="detail-label">Carta de motivação:</div>
                            <div class="detail-value">${candidature.lettre_motivation}</div>
                        </div>
                        ` : ''}
                    </div>
                `;
                
                document.getElementById('detailModal').style.display = 'block';
            } catch (error) {
                console.error('Error loading candidature details:', error);
                alert('Erro ao carregar detalhes da candidatura');
            }
        }
        
        function closeModal() {
            document.getElementById('detailModal').style.display = 'none';
        }
        
        async function deleteCandidature(candidatureId) {
            if (!confirm('Tem certeza que deseja excluir esta candidatura?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/candidature/${candidatureId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('Candidatura excluída com sucesso');
                    loadCandidatures(currentPage);
                    loadStats();
                } else {
                    alert('Erro ao excluir candidatura');
                }
            } catch (error) {
                console.error('Error deleting candidature:', error);
                alert('Erro ao excluir candidatura');
            }
        }
        
        function searchCandidatures() {
            searchQuery = document.getElementById('searchInput').value;
            loadCandidatures(1);
        }
        
        function refreshData() {
            loadStats();
            loadCandidatures(currentPage);
        }
        
        function exportData() {
            // Simple export functionality
            window.open('/api/candidatures?export=csv', '_blank');
        }
        
        // Close modal when clicking outside
        document.getElementById('detailModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    </script>
</body>
</html>
"""

@admin_bp.route('/')
@login_required
def admin_dashboard():
    """Admin dashboard page"""
    return render_template_string(ADMIN_TEMPLATE)

@admin_bp.route('/api/candidatures')
@login_required
def api_candidatures():
    """API endpoint for candidatures with search and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Candidature.query
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Candidature.prenom.ilike(search_filter),
                    Candidature.nom.ilike(search_filter),
                    Candidature.email.ilike(search_filter),
                    Candidature.telephone.ilike(search_filter),
                    Candidature.ville.ilike(search_filter)
                )
            )
        
        candidatures = query.order_by(Candidature.date_candidature.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'candidatures': [c.to_dict() for c in candidatures.items],
            'total': candidatures.total,
            'pages': candidatures.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.error(f"Error in admin API: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@admin_bp.route('/api/candidature/<int:candidature_id>')
@login_required
def api_candidature_detail(candidature_id):
    """API endpoint for single candidature details"""
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        return jsonify(candidature.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error getting candidature details: {str(e)}")
        return jsonify({'error': 'Candidature non trouvée'}), 404

@admin_bp.route('/api/candidature/<int:candidature_id>/file/<filename>')
@login_required
def api_download_file(candidature_id, filename):
    """API endpoint for downloading files"""
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        
        # Verify that the file belongs to this candidature
        candidature_files = [
            candidature.piece_identite_recto,
            candidature.piece_identite_verso,
            candidature.justificatif_domicile,
            candidature.cv
        ]
        
        if candidature.lettre_motivation and candidature.lettre_motivation.endswith(('.pdf', '.doc', '.docx')):
            candidature_files.append(candidature.lettre_motivation)
        
        if filename not in candidature_files:
            return jsonify({'error': 'Fichier non autorisé'}), 403
        
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Fichier non trouvé'}), 404

@admin_bp.route('/api/candidature/<int:candidature_id>', methods=['DELETE'])
@login_required
def api_delete_candidature(candidature_id):
    """API endpoint for deleting candidatures"""
    try:
        candidature = Candidature.query.get_or_404(candidature_id)
        
        # Delete associated files
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        files_to_delete = [
            candidature.piece_identite_recto,
            candidature.piece_identite_verso,
            candidature.justificatif_domicile,
            candidature.cv
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
        
        return jsonify({'message': 'Candidature supprimée avec succès'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting candidature: {str(e)}")
        return jsonify({'error': 'Erreur lors de la suppression'}), 500

@admin_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    try:
        total_candidatures = Candidature.query.count()
        
        # Get candidatures from today
        today = datetime.now().date()
        today_candidatures = Candidature.query.filter(
            db.func.date(Candidature.date_candidature) == today
        ).count()
        
        # Get candidatures from this week
        week_start = today - timedelta(days=today.weekday())
        week_candidatures = Candidature.query.filter(
            Candidature.date_candidature >= week_start
        ).count()
        
        # Get candidatures from this month
        month_start = today.replace(day=1)
        month_candidatures = Candidature.query.filter(
            Candidature.date_candidature >= month_start
        ).count()
        
        return jsonify({
            'total_candidatures': total_candidatures,
            'today_candidatures': today_candidatures,
            'week_candidatures': week_candidatures,
            'month_candidatures': month_candidatures
        })
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500


# Importar template de login
from .login_template import LOGIN_TEMPLATE

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Usuário ou senha incorretos')
    
    return render_template_string(LOGIN_TEMPLATE)

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))

