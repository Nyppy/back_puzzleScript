import mimetypes
import os

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import viewsets

from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper

from . import serializers
from . import models
from .short_text import make_sort_text

from .main import MainManager


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProfileSerializer
    queryset = models.User.objects.all()

    def list(self, request, *args, **kwargs):
        raise serializers.exceptions.PermissionDenied()

    def retrieve(self, request, *args, **kwargs):
        authorization = request.query_params.get("authorization", None)
        if not authorization:
            raise serializers.exceptions.AuthenticationFailed()
        user = models.User.objects.filter(authorization=authorization).first()
        if not user:
            raise serializers.exceptions.NotAuthenticated()

        return JsonResponse(user.get_data())

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        instance = super().create(request)
        return JsonResponse(models.User.objects.get(id=instance.data['id']).get_data(), status=201)


class LoginAPIView(APIView):
    """
    Logs in an existing user.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        """
        Checks is user exists.
        Email and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return JsonResponse(
            models.User.objects.get(id=serializer.validated_data['id']).get_data()
        )


class FileManagerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FileManagerSerializer
    queryset = models.FileManager.objects.all()

    def list(self, request, *args, **kwargs):
        profile_id = request.query_params.get("profile", None)
        file_instance = models.FileManager.objects.filter(profile=int(profile_id)).first()

        if not profile_id:
            raise serializers.exceptions.AuthenticationFailed()

        response = HttpResponse(
            file_instance.full_text,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=file.docx'
        return response

    def create(self, request, *args, **kwargs):
        instance = super().create(request)
        file_instance = models.FileManager.objects.filter(profile=instance.data['profile']).first()
        full_text = MainManager().get_text_from_video(instance.data['video'].split('/')[-1])

        short_text = make_sort_text(full_text)
        file_instance.full_text = full_text
        if short_text:
            file_instance.short_text = short_text[0]
        file_instance.save()

        return JsonResponse({'full_text': full_text, 'short_text': short_text})


class FileView(APIView):

    def get(self, request):
        profile_id = request.query_params.get("profile_id", None)
        if profile_id:
            data_set = models.FileManager.objects.filter(profile=int(profile_id)).all()

            if data_set:
                data = [instance.get_data for instance in data_set]
                return JsonResponse({'data': data})
            else:
                return JsonResponse({'data': None})

        doc_id = request.query_params.get("doc_id", None)
        if doc_id:
            doc_inst = models.FileManager.objects.filter(pk=int(doc_id)).first()
            if doc_inst:
                doc = doc_inst.text_doc
                if doc:
                    doc = doc.split('/')
                    doc = doc[-1]
                    path = os.path.dirname(os.path.abspath(__file__)) + f'/media/doc/{doc}'

                    chunk_size = 8192
                    response = StreamingHttpResponse(FileWrapper(open(path, 'rb'), chunk_size),
                                                     content_type=mimetypes.guess_type(path)[0])
                    response['Content-Length'] = os.path.getsize(path)
                    response['Content-Disposition'] = "attachment; filename=%s" % 'file.docx'
                    return response
                else:
                    response = HttpResponse(
                        doc_inst.full_text,
                        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
                    response['Content-Disposition'] = 'attachment; filename=file.docx'
                    return response
