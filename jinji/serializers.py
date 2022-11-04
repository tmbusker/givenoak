from rest_framework import serializers
from jinji.models.ido.dkido import Dkido


class TodoSerializer(serializers.ModelSerializer):
 
    # create a meta class
    class Meta:
        model = Dkido
        fields = ('ido_syumoku', 'cshainno', 'cnamekna', 'cnameknj')