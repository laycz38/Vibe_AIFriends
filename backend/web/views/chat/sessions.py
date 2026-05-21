import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InterviewSession, InterviewNote


def serialize_session(session):
    return {
        'id': session.id,
        'title': session.title,
        'note_id': session.note_id,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat(),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-updated_at')

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total = sessions.count()
    page_sessions = sessions[start:end]

    return Response({
        'result': 'success',
        'sessions': [serialize_session(s) for s in page_sessions],
        'total': total,
        'page': page,
        'page_size': page_size,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session(request, session_id):
    try:
        session = InterviewSession.objects.get(pk=session_id, user=request.user)
    except InterviewSession.DoesNotExist:
        return Response({'result': 'error', 'message': '记录不存在'}, status=404)

    return Response({
        'result': 'success',
        'session': {
            **serialize_session(session),
            'messages': json.loads(session.messages_json),
        },
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_session(request):
    messages = request.data.get('messages', [])
    if not messages:
        return Response({'result': 'error', 'message': 'messages 不能为空'}, status=400)

    note_id = request.data.get('note_id')
    note = None
    if note_id:
        try:
            note = InterviewNote.objects.get(pk=note_id)
        except InterviewNote.DoesNotExist:
            pass

    title = request.data.get('title', '')
    if not title:
        if note:
            title = f'{note.company} - {note.title} 模拟面试'
        else:
            title = f'自由对话 {request.user.username}'

    session_id = request.data.get('session_id')
    if session_id:
        try:
            session = InterviewSession.objects.get(pk=session_id, user=request.user)
            session.messages_json = json.dumps(messages, ensure_ascii=False)
            session.title = title
            session.note = note
            session.save()
        except InterviewSession.DoesNotExist:
            session = InterviewSession.objects.create(
                user=request.user,
                note=note,
                title=title,
                messages_json=json.dumps(messages, ensure_ascii=False),
            )
    else:
        session = InterviewSession.objects.create(
            user=request.user,
            note=note,
            title=title,
            messages_json=json.dumps(messages, ensure_ascii=False),
        )

    return Response({
        'result': 'success',
        'session': serialize_session(session),
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    try:
        session = InterviewSession.objects.get(pk=session_id, user=request.user)
        session.delete()
        return Response({'result': 'success'})
    except InterviewSession.DoesNotExist:
        return Response({'result': 'error', 'message': '记录不存在'}, status=404)
