import os


ALLOWED_EXTENSIONS = {'.txt', '.png'}
UPLOAD_DIR = 'app/uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024 # 16MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename: str) -> bool:
    '''
    확장자 확인 함수
    '''
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
