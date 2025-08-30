from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from typing import Optional
from app.utils.files import allowed_file, UPLOAD_DIR, MAX_FILE_SIZE
import os
import zipfile
from app import schema

router = APIRouter(prefix='/api/files', tags=['files'])

@router.post('/upload', summary='파일 업로드')
async def upload_file(file:Optional[UploadFile] = File(None)):
    '''
    1. 파일 첨부하지 않은 경우  
    status 400, {'error' : 'No file part'}

    2. 허용하지 않는 확장자의 파일이 업로드 된 경우  
    status 400, {'error' : 'Invalid file type'}

    3. 파일 이름이 중복된 경우  
    status 400, {'error' : 'File already exists'}

    4. 파일 크기가 16MB를 초과 하는 경우  
    status 409, {'error' : 'File too large'}
    '''

    # 파일을 첨부하지 않은 경우
    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail={'error':  'No file part'})
    
    # 허용하지 않는 확장자의 파일이 업로드 된 경우
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail={'error': 'Invalid file type'})
    
    # 파일 이름이 중복된 경우
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail={'error': 'File already exists'})
    
    # 파일 크기가 16MB를 초과 하는 경우
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=433, detail={'error': 'File too large'})
    
    # 파일 저장
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return {'message': 'File Upload Successfuly'}

@router.get('/download', summary='파일 다운로드')
async def download_file(background: BackgroundTasks, filenames: Optional[str] = Query(None)):
    '''
    ### 두개 이상 요청시 ,로 구분  
    ex) file1.txt,file2.txt  
    
    1. filenames 누락 한 경우  
    status 400, {'message' : 'No filenames'}

    2. 다운로드 파일이 없는 경우
    status 404, {'message' : 'File not found'}

    3. 두 개 이상의 파일 다운로드시 
    files.zip으로 압축  
    '''
    # file name이 누락된 경우
    if not filenames:
        raise HTTPException(status_code=400, detail={'error': 'No filenames'})
    
    file_list = filenames.split(',')
    paths = [os.path.join(UPLOAD_DIR, name) for name in file_list]

    # 다운로드 하려는 파일이 없는 경우
    for p in paths:
        if not os.path.exists(p):
            raise HTTPException(status_code=404, detail={'error': f'{os.path.basename(p)} File not found'})
    
    # 하나의 파일 다운로드
    if len(paths) == 1:
        return FileResponse(paths[0], filename=file_list[0])
    
    # 두개 이상의 파일 다운로드
    zip_name = 'files.zip'
    zip_path = os.path.join(UPLOAD_DIR, f'__tmp__{os.getpid()}_{id(paths)}.zip')

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in paths:
            zipf.write(p, arcname=os.path.basename(p))
    
    # 응답 후 임시zip 파일 제거
    background.add_task(os.remove, zip_path)

    return FileResponse(path = zip_path, filename=zip_name)

@router.get('/list', summary='파일 리스트 확인')
async def file_list():
    '''
    파일 리스트 확인
    '''
    files = sorted(os.listdir(UPLOAD_DIR))
    
    return schema.FileListRes(files=files)
