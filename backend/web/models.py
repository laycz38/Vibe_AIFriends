from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    photo = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return self.user.username


class InterviewNote(models.Model):
    DIFFICULTY_CHOICES = (
        ('简单', '简单'),
        ('中等', '中等'),
        ('困难', '困难'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    cover = models.ImageField(upload_to='notes/covers/', blank=True, null=True)
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='中等')
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class InterviewNoteLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_notes')
    note = models.ForeignKey(InterviewNote, on_delete=models.CASCADE, related_name='like_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'note'], name='unique_note_like')
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.note.title}'


class InterviewNoteComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_comments')
    note = models.ForeignKey(InterviewNote, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.note.title}'
