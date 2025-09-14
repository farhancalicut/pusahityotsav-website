
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
    """Represents a single competition, linked to a Category."""
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    rules = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"

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

    def __str__(self):
        return f"{self.registration} - {self.position} Place"

class GalleryImage(models.Model):
    caption = models.CharField(max_length=255)
    # --- ADD THIS FIELD ---
    year = models.IntegerField()
    image = models.ImageField(upload_to='gallery_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caption} ({self.year})"