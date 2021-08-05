from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.pagination import PageNumberPagination
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, ThreadListSerializer


class CreateThreadView(generics.CreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)


class GetThreadListView(generics.ListAPIView):
    serializer_class = ThreadListSerializer
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        self.queryset = Thread.objects.filter(participants=request.user.id)
        return super().get(request, *args, **kwargs)


class GetSingleObjectView(generics.RetrieveAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Find only user thread"""
        return super().get_queryset().filter(participants=self.request.user.id)


class UpdateThreadView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    authentication_classes = (
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    )
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Find only user thread"""
        return super().get_queryset().filter(participants=self.request.user.id)

    def delete(self, request, *args, **kwargs):
        instance = Thread.objects.filter(pk=kwargs["pk"]).first()
        if not instance:
            raise NotFound("This object is not exist")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JSONWebTokenAuthentication,
        SessionAuthentication,
        BasicAuthentication,
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Message.objects.filter(pk=self.kwargs.get("pk"))

    def list(self, request, *args, **kwargs):
        queryset = Message.objects.filter(thread=self.kwargs.get("pk"))
        if not queryset:
            raise NotFound("This thread is empty")
        if not Thread.objects.filter(
            participants=self.request.user.id, id=self.kwargs.get("pk")
        ):
            raise NotFound("You have not permission")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        message = Message.objects.filter(pk=kwargs.get("pk")).first()
        if not message:
            raise NotFound("This object is not exist")
        if not (request.user == message.sender):
            raise NotFound("You have not permission")
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
