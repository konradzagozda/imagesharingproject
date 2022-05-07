from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase


class APITestCase(APITestCase):
    client = None

    def setUp(self):
        self.client = APIClient()

    def test_user_can_upload_images(self):
        # can upload png, jpg, jpeg
        # can't upload for example
        self.client.login(username='basic', password='basic')

        # uploading images is permitted:
        for ext in ('jpeg', 'png', 'jpg'):
            with open(f'api/test_assets/{ext}.{ext}', 'rb') as img:
                res = self.client.post('/api/images/', {'name': f'{ext}_file', 'image': img})
                self.assertEqual(201, res.status_code)

        # uploading different formats is not permitted:
        with open('api/test_assets/random.txt', 'rb') as file:
            res = self.client.post('/api/images/', {'name': 'txt_file', 'image': file})
            self.assertNotEqual(201, res.status_code)


    def test_unautorized_user_can_download_image(self):
        self.client.login(username='basic', password='basic')

        self._upload_test_images(self.client)
        res = self.client.get('/api/images/')
        link = res.data[0]['links']['200px']

        self.client.logout()
        res = self.client.get(link)
        self.assertEqual(200, res.status_code)


    def test_basic_tier(self):
        # data's links attribute has 200px key
        # data's links attribute has no 400px / orig key
        # access to 200px thumbnail
        # no access to original image
        # no access to 400px thumbnail
        # no access to get_temp_link action

        self.client.login(username='basic', password='basic')
        self._upload_test_images(self.client)
        res = self.client.get('/api/images/')
        links = res.data[0]['links']
        self.assertTrue('200px' in links)
        for size in ('400px', 'orig'):
            self.assertTrue(size not in links)

        uuid = res.data[0]['uuid']

        orig_link = f'/api/images/{uuid}/'

        res = self.client.get(orig_link)
        self.assertEqual(404, res.status_code)

        res = self.client.get(f'{orig_link}?height=200')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}?height=400')
        self.assertEqual(404, res.status_code)

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=300')
        self.assertEqual(403, res.status_code)

    def test_premium_tier(self):
        # access to 200 / 400 / original
        # no access to get_temp_link action
        self.client.login(username='premium', password='premium')
        self._upload_test_images(self.client)
        res = self.client.get('/api/images/')
        links = res.data[0]['links']
        for size in ('200px', '400px', 'orig'):
            self.assertTrue(size in links)

        uuid = res.data[0]['uuid']

        orig_link = f'/api/images/{uuid}/'

        res = self.client.get(orig_link)
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}?height=200')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}?height=400')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=300')
        self.assertEqual(403, res.status_code)



    def test_enterprise_tier(self):
        # access to 200 / 400 / original / get_temp_link action
        self.client.login(username='enterprise', password='enterprise')
        self._upload_test_images(self.client)
        res = self.client.get('/api/images/')
        links = res.data[0]['links']
        for size in ('200px', '400px', 'orig'):
            self.assertTrue(size in links)

        self.assertTrue('temp' in links)

        uuid = res.data[0]['uuid']

        orig_link = f'/api/images/{uuid}/'

        res = self.client.get(orig_link)
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}?height=200')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}?height=400')
        self.assertEqual(200, res.status_code)

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=300')
        self.assertEqual(200, res.status_code)

    def test_temporary_links(self):
        # ttl < 300 fails
        # ttl > 30_000 fails
        # 300 =< ttl =< 30_000 ok
        # can download image using temporary link

        self.client.login(username='enterprise', password='enterprise')
        self._upload_test_images(self.client)
        res = self.client.get('/api/images/')
        links = res.data[0]['links']

        uuid = res.data[0]['uuid']

        orig_link = f'/api/images/{uuid}/'

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=299')
        self.assertEqual(400, res.status_code)

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=30001')
        self.assertEqual(400, res.status_code)

        res = self.client.get(f'{orig_link}get_temp_link/?ttl=300')
        self.assertEqual(200, res.status_code)
        temp_link = res.data['link']
        res = self.client.get(temp_link)
        self.assertEqual(200, res.status_code)

        self.client.logout()
        res = self.client.get(temp_link)
        self.assertEqual(200, res.status_code)


    @staticmethod
    def _upload_test_images(logged_client):
        for ext in ('jpeg', 'png', 'jpg'):
            with open(f'api/test_assets/{ext}.{ext}', 'rb') as img:
                logged_client.post('/api/images/', {'name': f'{ext}_file', 'image': img})