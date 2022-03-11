from rest_framework import mixins, viewsets


class ModelSetCLD(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass
