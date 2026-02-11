from flask import request, jsonify, g
from functools import wraps
import jwt
from app.config import Config
from app.Models.Prof import Prof

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Chercher le token dans les headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Format attendu: "Bearer <token>"
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Enlever 'Bearer '
                
        if not token:
            return jsonify({'message': 'Token manquant'}), 401

        try:
            # Décoder le token
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = Prof.query.filter_by(id=data['id']).first()
            if not current_user:
                return jsonify({'message': 'Utilisateur non trouvé'}), 401
            
            # Stocker l'utilisateur dans g pour y accéder dans la vue
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token invalide'}), 401

        return f(*args, **kwargs)

    return decorated 