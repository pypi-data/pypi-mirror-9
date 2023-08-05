from json_resource import Collection


class AggregateResource(Collection):
    def load(self):
        self['items'] = self.objects.collection.aggregate(
            self.pipeline
        )['result']

        return self
