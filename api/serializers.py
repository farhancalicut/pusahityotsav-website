from rest_framework import serializers
from .models import Group, Category, Event, Contestant, Registration, Result, GalleryImage

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class EventSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta:
        model = Event
        fields = ['id', 'name', 'category', 'rules']

class ContestantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contestant
        fields = [
            'id', 'full_name', 'email', 'state', 'gender', 
            'group', 'category', 'course', 'phone_number'
        ]

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'contestant', 'event']

class ResultSerializer(serializers.ModelSerializer):
    # --- ADD these lines to get related data for the poster ---
    contestant_name = serializers.CharField(source='registration.contestant.full_name', read_only=True)
    event_name = serializers.CharField(source='registration.event.name', read_only=True)
    group_name = serializers.CharField(source='registration.contestant.group.name', read_only=True)
    # -----------------------------------------------------------

    class Meta:
        model = Result
        # Add 'resultNumber' and the new fields above
        fields = [
            'id', 
            'position', 
            'points', 
            'resultNumber',  # <-- Our new field
            'contestant_name', 
            'event_name',
            'group_name'
        ]
class GalleryImageSerializer(serializers.ModelSerializer):
    # Add this new line to define how the 'image' field should be serialized
    image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ('id', 'image', 'caption', 'year') # List fields explicitly

    # Add this new function to the class
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None