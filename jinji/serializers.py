from rest_framework import serializers
from jinji.models.ido.dkido import Dkido


class DkidoSerializer(serializers.ModelSerializer):
    """異動情報"""

    class Meta:
        model = Dkido
        fields = ('ido_syumoku', 'cshainno', 'cnamekna', 'cnameknj')
