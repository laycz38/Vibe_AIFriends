from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from web.views.index import index
from web.views.note.create import create as create_note
from web.views.note.create_comment import create_comment
from web.views.note.favorite_list import favorite_list
from web.views.note.get_detail import get_detail
from web.views.note.get_list import get_list
from web.views.note.toggle_favorite import toggle_favorite
from web.views.note.toggle_like import toggle_like
from web.views.user.account.get_user_info import get_user_info
from web.views.user.account.login import login
from web.views.user.account.logout import logout
from web.views.user.account.refresh_token import refresh_token
from web.views.user.account.register import register
from web.views.user.account.update_profile import update_profile
from web.views.chat.send_message import send_message
from web.views.chat.interview import interview
from web.views.chat.sessions import list_sessions, get_session, save_session, delete_session
from web.views.tts.synthesize import synthesize_speech
from web.views.tts.stream import synthesize_stream_view

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/account/login/', login, name='user_account_login'),
    path('api/user/account/register/', register, name='user_account_register'),
    path('api/user/account/logout/', logout, name='user_account_logout'),
    path('api/user/account/refresh_token/', refresh_token, name='user_account_refresh_token'),
    path('api/user/account/info/', get_user_info, name='user_account_info'),
    path('api/user/account/update_profile/', update_profile, name='user_account_update_profile'),
    path('api/notes/', get_list, name='note_list'),
    path('api/notes/create/', create_note, name='note_create'),
    path('api/notes/favorites/', favorite_list, name='note_favorite_list'),
    path('api/notes/<int:note_id>/', get_detail, name='note_detail'),
    path('api/notes/<int:note_id>/toggle_like/', toggle_like, name='note_toggle_like'),
    path('api/notes/<int:note_id>/toggle_favorite/', toggle_favorite, name='note_toggle_favorite'),
    path('api/notes/<int:note_id>/comments/create/', create_comment, name='note_comment_create'),
    path('api/chat/send/', send_message, name='chat_send'),
    path('api/chat/interview/', interview, name='chat_interview'),
    path('api/chat/sessions/', list_sessions, name='chat_sessions_list'),
    path('api/chat/sessions/save/', save_session, name='chat_sessions_save'),
    path('api/chat/sessions/<int:session_id>/', get_session, name='chat_sessions_detail'),
    path('api/chat/sessions/<int:session_id>/delete/', delete_session, name='chat_sessions_delete'),
    path('api/tts/synthesize/', synthesize_speech, name='tts_synthesize'),
    path('api/tts/stream/', synthesize_stream_view, name='tts_stream'),
    path('', index, name='index'),
    re_path(r'^(?!media/|static/|assets/).*$', index, name='frontend_fallback'),
]
