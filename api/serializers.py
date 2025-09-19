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
    # We specify that we want to see the names of the categories, not just their IDs.
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Event
        # We explicitly list the fields we want to send.
        fields = ['id', 'name', 'categories']

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
    # This new field will contain our full, absolute URL
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        # We specify the fields we want, including our new one
        fields = ['id', 'image_url', 'caption', 'year']

    # This function generates the value for the 'image_url' field
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            # request.build_absolute_uri() is the key to creating the full URL
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url)
        return "" # Return an empty string if there's no image