
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Group(models.Model):
    """Represents a School, like 'School of Management'."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    """Represents an eligibility category, e.g., 'Girls', 'Category - A (UG)'."""
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=100)
    # This is the key change: an event can now belong to many categories.
    categories = models.ManyToManyField(Category, related_name='events')

    # We are removing the old 'category' ForeignKey and the 'is_general' BooleanField.

    def __str__(self):
        return self.name

class Contestant(models.Model):
    """Represents a registered student."""
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    state = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, verbose_name="School/Group")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Contestant Category (e.g., UG, PG, Girls)")
    course = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Registration(models.Model):
    """Links a Contestant to an Event they are participating in."""
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('contestant', 'event')

    def __str__(self):
        return f"{self.contestant.full_name} -> {self.event.name}"

class Result(models.Model):
    """Stores the result for a single registration."""
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    points = models.PositiveIntegerField(default=0, help_text="Points awarded by the judges.")

    resultNumber = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        # unique=True, 
        help_text="result number"
    )

    def __str__(self):
        return f"{self.registration} - {self.position} Place"

class GalleryImage(models.Model):
    caption = models.CharField(max_length=255)
    # --- ADD THIS FIELD ---
    year = models.IntegerField()
    image = models.ImageField(upload_to='gallery_images/')
    # Store the Cloudinary URL directly
    cloudinary_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If image is provided and cloudinary_url is not set, upload to Cloudinary
        if self.image and not self.cloudinary_url:
            try:
                import cloudinary.uploader
                import uuid
                
                # Read the image data
                self.image.seek(0)
                image_data = self.image.read()
                
                # Create a unique public_id to avoid conflicts
                unique_id = str(uuid.uuid4())[:8]
                safe_caption = ''.join(c for c in self.caption if c.isalnum() or c in '-_')[:20]
                
                # Upload to Cloudinary (same method as poster generation)
                upload_result = cloudinary.uploader.upload(
                    image_data,
                    folder="gallery_images",
                    public_id=f"gallery_{self.year}_{safe_caption}_{unique_id}",
                    overwrite=True
                )
                
                # Store the Cloudinary URL
                self.cloudinary_url = upload_result.get('secure_url')
                
                # Reset the image field position
                self.image.seek(0)
                
            except Exception as e:
                print(f"Error uploading to Cloudinary: {e}")
                # Continue saving even if Cloudinary upload fails
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.caption} ({self.year})"
    
class CarouselImage(models.Model):
    """Model for dashboard carousel images that auto-scroll."""
    title = models.CharField(max_length=255, help_text="Title or description for the carousel image")
    image = models.ImageField(upload_to='carousel_images/')
    cloudinary_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Whether this image should be shown in the carousel")
    order = models.PositiveIntegerField(default=0, help_text="Order in which images appear (lower numbers first)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = "Carousel Image"
        verbose_name_plural = "Carousel Images"

    def save(self, *args, **kwargs):
        # If image is provided and cloudinary_url is not set, upload to Cloudinary
        if self.image and not self.cloudinary_url:
            try:
                import cloudinary.uploader
                import uuid
                
                # Read the image data from the uploaded file
                if hasattr(self.image, 'read'):
                    # If it's an uploaded file object
                    self.image.seek(0)
                    image_data = self.image.read()
                    self.image.seek(0)  # Reset for Django to save it locally too
                else:
                    # If it's already saved locally, read from file path
                    with open(self.image.path, 'rb') as f:
                        image_data = f.read()
                
                # Create a unique public_id to avoid conflicts
                unique_id = str(uuid.uuid4())[:8]
                safe_title = ''.join(c for c in self.title if c.isalnum() or c in '-_')[:20]
                
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image_data,
                    folder="carousel_images",
                    public_id=f"carousel_{safe_title}_{unique_id}",
                    overwrite=True
                )
                
                # Store the Cloudinary URL
                self.cloudinary_url = upload_result.get('secure_url')
                
                print(f"✅ Successfully uploaded carousel image to Cloudinary: {self.cloudinary_url}")
                
            except Exception as e:
                print(f"❌ Error uploading carousel image to Cloudinary: {e}")
                # Don't set cloudinary_url if upload fails - this way we can retry later
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class IndividualChampion(Contestant):
    """A proxy model to show top individual champions in the admin."""
    class Meta:
        proxy = True
        verbose_name = "Individual Champion"
        verbose_name_plural = "Individual Champions"