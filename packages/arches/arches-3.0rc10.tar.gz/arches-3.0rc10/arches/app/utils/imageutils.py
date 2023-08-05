from PIL import Image, ImageOps
import io
import os
from django.core.files.uploadedfile import SimpleUploadedFile

def generate_thumbnail(file):
	#print file.content_type
	if 'image' in file.content_type:
		im = Image.open(file)
		thumb = ImageOps.fit(im, (128,128), Image.ANTIALIAS)
		f = io.BytesIO()
		thumb.save(f, 'JPEG')
		return SimpleUploadedFile('%s_%s.%s' % ('thumb', os.path.splitext(file.name)[0], 'jpg'), f.getvalue(), content_type='image/jpeg')
	else:
		pass
