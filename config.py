import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MAHJOUB_SMART_MARKET_2026_SECURE'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mahjoub_market.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # حد أقصى 16 ميجا للصور
