from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Candidature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.Text, nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    code_postal = db.Column(db.String(20), nullable=False)
    
    # Noms des fichiers uploadés
    piece_identite_recto = db.Column(db.String(255), nullable=False)
    piece_identite_verso = db.Column(db.String(255), nullable=False)
    justificatif_domicile = db.Column(db.String(255), nullable=False)
    lettre_motivation = db.Column(db.Text, nullable=True)
    lettre_motivation_file = db.Column(db.String(255), nullable=True)
    
    date_candidature = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Candidature {self.prenom} {self.nom}>'

    def to_dict(self):
        return {
            'id': self.id,
            'prenom': self.prenom,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'adresse': self.adresse,
            'ville': self.ville,
            'code_postal': self.code_postal,
            'piece_identite_recto': self.piece_identite_recto,
            'piece_identite_verso': self.piece_identite_verso,
            'justificatif_domicile': self.justificatif_domicile,
            'lettre_motivation': self.lettre_motivation,
            'lettre_motivation_file': self.lettre_motivation_file,
            'date_candidature': self.date_candidature.isoformat() if self.date_candidature else None
        }
