from django.contrib import admin
from .models import InterviewNote, InterviewNoteComment, InterviewNoteLike, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bio')
    search_fields = ('user__username',)


@admin.register(InterviewNote)
class InterviewNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'company', 'position', 'difficulty', 'created_at')
    search_fields = ('title', 'user__username', 'company', 'position')
    list_filter = ('difficulty', 'company', 'position')


@admin.register(InterviewNoteLike)
class InterviewNoteLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'note', 'created_at')
    search_fields = ('user__username', 'note__title')


@admin.register(InterviewNoteComment)
class InterviewNoteCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'note', 'created_at')
    search_fields = ('user__username', 'note__title', 'content')
