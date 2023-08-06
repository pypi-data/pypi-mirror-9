try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from PIL import Image
from requests.auth import HTTPBasicAuth
from .bind import bind_method, build_parameters, build_path
from .bind import ViSearchClientError


class ViSearchAPI(object):
    def __init__(self, access_key, secret_key):
        self.host = "http://visearch.visenze.com/"
        self.access_key = access_key
        self.secret_key = secret_key
        self.auth_info = HTTPBasicAuth(self.access_key, self.secret_key)

    def insert(self, images, **kwargs):
        if type(images).__name__ != 'list':
            images = [images, ]

        path = 'insert'
        method = 'POST'
        raw_parameters = {
            'images': images,
        }
        raw_parameters.update(kwargs)
        parameters = build_parameters(path, raw_parameters)
        resp = bind_method(self, path, method, parameters)
        return resp

    def update(self, images):
        self.insert(images)

    def remove(self, image_names):
        if type(image_names).__name__ != 'list':
            image_names = [image_names, ]
        path = 'remove'
        method = 'post'
        parameters = build_parameters(path, image_names)
        resp = bind_method(self, path, method, parameters)
        return resp

    def insert_status(self, trans_id):
        path = 'insert/status/{trans_id}'
        path_parameters = {
            'trans_id': str(trans_id)
        }
        path = build_path(path, path_parameters)
        resp = bind_method(self, path, 'GET')
        return resp

    def _search(self, path, parameters):
        parameters = build_parameters(path, parameters)
        resp = bind_method(self, path, 'GET', parameters)
        return resp

    def search(self, im_name, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0):
        parameters = {
            'im_name': im_name,
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})

        path = 'search'
        return self._search(path, parameters)

    def colorsearch(self, color, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0):
        # _rgbstr = re.compile(r'^(?:[0-9a-fA-F]{3}){1,2}$')
        if color.startswith('#'):
            color = color[1:]
        # if not bool(_rgbstr.match(color)):
        #     raise ViSearchClientError("the color {} is not in 6 character hex format".format(color))
        parameters = {
            'color': color,
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})

        path = 'colorsearch'
        return self._search(path, parameters)

    def _read_image(self, image_path, resize_settings):
        if resize_settings == 'STANDARD':
            dimensions, quality = (512, 512), 75
        elif resize_settings == 'HIGH':
            dimensions, quality = (1024, 1024), 75
        else:
            resize_type_name = type(resize_settings).__name__
            if (resize_type_name == 'list' or resize_type_name == 'tuple') and len(resize_settings) == 3:
                dimensions, quality = (resize_settings[0], resize_settings[1]), resize_settings[2]
            else:
                raise ViSearchClientError("invalid resize settings: {0}".format(resize_settings))
        image = Image.open(image_path)
        image = image.resize(dimensions, Image.ANTIALIAS)

        output = StringIO()
        image.save(output, 'JPEG', quality=quality)
        contents = output.getvalue()
        output.close()
        fp = (image_path, contents)
        files = {'image': fp}
        return files

    def uploadsearch(self, image_path=None, image_url=None, box=None, page=1, limit=30, fl=None, fq=None, score=False, score_max=1, score_min=0, resize='STANDARD'):
        parameters = {
            'page': page,
            'limit': limit,
            'score_max': score_max,
            'score_min': score_min
        }
        if fl:
            parameters.update({'fl': fl})
        if fq:
            parameters.update({'fq': fq})
        if score:
            parameters.update({'score': score})
        if box:
            if (type(box).__name__ == 'list' or type(box).__name__ == 'tuple') and len(box) == 4:
                parameters.update({'box': ','.join(map(str, box))})
            else:
                raise ViSearchClientError("invalid box: {0}".format(box))

        path = 'uploadsearch'

        if not (image_path or image_url):
            raise ViSearchClientError("either provide image_path or image_url")
        elif image_url:
            parameters.update({'im_url': image_url})
            return self._search(path, parameters)
        else:
            files = self._read_image(image_path, resize)
            parameters = build_parameters(path, parameters)
            return bind_method(self, path, 'POST', parameters, files=files)
