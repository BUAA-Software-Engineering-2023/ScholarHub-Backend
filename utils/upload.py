import hashlib
import os


def upload_file(request, file_type):
    file = request.FILES.get('file').open('r')
    md5 = hashlib.md5(file.read()).hexdigest()
    extra_name = file.name.split('.')[-1]
    if file_type == 'image' and extra_name not in ['jpg', 'png', 'jpeg']:
        return None
    elif file_type == 'pdf' and extra_name != 'pdf':
        return None
    file_name = md5 + '.' + extra_name
    if not os.path.exists(f'./media/{file_name}'):
        file.seek(0)
        with open(f'./media/{file_name}', 'wb') as f:
            f.write(file.read())
        return request.build_absolute_uri(f'/media/{file_name}')
    else:
        return request.build_absolute_uri(f'/media/{file_name}')
