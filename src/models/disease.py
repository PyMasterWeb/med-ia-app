from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Disease(db.Model):
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'severity': self.severity
        }

