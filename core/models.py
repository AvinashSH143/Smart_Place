from django.db import models


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='blog_images/', blank=True, null=True)
    short_article = models.TextField(help_text="Approximately 70-90 words")
    category = models.CharField(max_length=80, default="Career Guidance")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def word_count(self):
        return len(self.short_article.split())


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name} ({self.email})"
