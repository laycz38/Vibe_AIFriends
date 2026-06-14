from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    photo_base64 = models.TextField(blank=True, default='')
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
    cover_base64 = models.TextField(blank=True, default='')
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


class InterviewNoteFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_notes')
    note = models.ForeignKey(InterviewNote, on_delete=models.CASCADE, related_name='favorite_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'note'], name='unique_note_favorite')
        ]

    def __str__(self):
        return f'{self.user.username} ★ {self.note.title}'


class InterviewNoteComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_comments')
    note = models.ForeignKey(InterviewNote, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.note.title}'


class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    note = models.ForeignKey(InterviewNote, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    title = models.CharField(max_length=200)
    messages_json = models.TextField(default='[]')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.username}: {self.title}'


class StudyNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_notes')
    page_url = models.CharField(max_length=500)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'page_url'], name='unique_study_note')
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.username} @ {self.page_url}'


class InlineAnnotation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inline_annotations')
    page_url = models.CharField(max_length=500)
    selected_text = models.TextField()
    context_before = models.TextField()
    context_after = models.TextField()
    annotation_type = models.CharField(max_length=10, default='text')  # 'text' or 'image'
    content = models.TextField(blank=True, default='')
    color = models.CharField(max_length=20, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username} @ {self.page_url}: {self.selected_text[:30]}'
