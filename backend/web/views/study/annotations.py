from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from web.models import InlineAnnotation


def serialize_annotation(ann):
    return {
        'id': ann.id,
        'page_url': ann.page_url,
        'selected_text': ann.selected_text,
        'context_before': ann.context_before,
        'context_after': ann.context_after,
        'content': ann.content,
        'color': ann.color,
        'created_at': ann.created_at.isoformat(),
        'updated_at': ann.updated_at.isoformat(),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_annotations(request):
    page_url = request.GET.get('page_url', '').strip()
    if not page_url:
        return Response({'result': 'error', 'message': 'page_url 不能为空'}, status=400)
    annotations = InlineAnnotation.objects.filter(user=request.user, page_url=page_url)
    return Response({
        'result': 'success',
        'annotations': [serialize_annotation(a) for a in annotations],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_annotation(request):
    page_url = str(request.data.get('page_url', '')).strip()
    selected_text = str(request.data.get('selected_text', ''))
    context_before = str(request.data.get('context_before', ''))
    context_after = str(request.data.get('context_after', ''))
    content = str(request.data.get('content', ''))
    color = str(request.data.get('color', 'yellow'))

    if not page_url or not selected_text:
        return Response({'result': 'error', 'message': 'page_url 和 selected_text 不能为空'}, status=400)

    ann = InlineAnnotation.objects.create(
        user=request.user,
        page_url=page_url,
        selected_text=selected_text,
        context_before=context_before,
        context_after=context_after,
        content=content,
        color=color,
    )
    return Response({'result': 'success', 'annotation': serialize_annotation(ann)},
                    status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_annotation(request, annotation_id):
    try:
        ann = InlineAnnotation.objects.get(id=annotation_id)
    except InlineAnnotation.DoesNotExist:
        return Response({'result': 'error', 'message': '批注不存在'}, status=404)

    if ann.user != request.user:
        return Response({'result': 'error', 'message': '无权修改此批注'}, status=403)

    content = str(request.data.get('content', ann.content))
    color = str(request.data.get('color', ann.color))
    ann.content = content
    ann.color = color
    ann.save(update_fields=['content', 'color', 'updated_at'])
    return Response({'result': 'success', 'annotation': serialize_annotation(ann)})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_annotation(request, annotation_id):
    try:
        ann = InlineAnnotation.objects.get(id=annotation_id)
    except InlineAnnotation.DoesNotExist:
        return Response({'result': 'error', 'message': '批注不存在'}, status=404)

    if ann.user != request.user:
        return Response({'result': 'error', 'message': '无权删除此批注'}, status=403)

    ann.delete()
    return Response({'result': 'success'}, status=status.HTTP_200_OK)
