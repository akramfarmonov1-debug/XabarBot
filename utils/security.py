import bcrypt

def generate_password_hash(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password_hash(password_hash, password):
    """Check if a password matches its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))