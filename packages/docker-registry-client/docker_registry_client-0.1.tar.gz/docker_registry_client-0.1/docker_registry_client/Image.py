class Image(object):
    def __init__(self, image_id, client):
        self.image_id = image_id
        self._client = client

    def get_layer(self):
        return self._client.get_images_layer(self.image_id)

    def put_layer(self, data):
        # return self._client.put_images_layer(self.image_id, data)
        raise NotImplementedError()

    def get_json(self):
        return self._client.get_image_layer(self.image_id)

    def get_data(self, field):
        return self.get_json()[field]

    def put_json(self, data):
        #return self._client.put_image_layer(self.image_id, data)
        raise NotImplementedError()

    def ancestry(self):
        return self._client.get_image_ancestry(self.image_id)
