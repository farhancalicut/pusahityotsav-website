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
    # Override the image field to return the full Cloudinary URL
    image = serializers.SerializerMethodField()

    class Meta:
        model = GalleryImage
        fields = ['id', 'image', 'caption', 'year']

    def get_image(self, obj):
        """
        Return the full Cloudinary URL for the image.
        This forces the generation of proper Cloudinary URLs in production.
        """
        if obj.image:
            image_url = obj.image.url
            
            # If the URL is already a full Cloudinary URL, return it
            if 'cloudinary.com' in str(image_url):
                return image_url
            
            # Try to construct Cloudinary URL manually
            try:
                import os
                from django.conf import settings
                
                # Get cloud name from environment variables (same as poster generation)
                cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
                
                if cloud_name:
                    # Extract the file path from the image name
                    # obj.image.name contains the path like 'gallery_images/1757813627456.jpeg'
                    image_path = str(obj.image.name)
                    
                    # Remove the file extension to get the public_id
                    if '.' in image_path:
                        public_id = image_path.rsplit('.', 1)[0]
                    else:
                        public_id = image_path
                    
                    # Construct the Cloudinary URL (same format as working poster generation)
                    cloudinary_url = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
                    return cloudinary_url
                else:
                    # If no cloud name, log this for debugging
                    print(f"WARNING: No CLOUDINARY_CLOUD_NAME found for image {obj.id}")
                
            except Exception as e:
                # Log the error for debugging
                print(f"Error generating Cloudinary URL for image {obj.id}: {e}")
            
            # Return the original URL as fallback
            return str(image_url)
        return None