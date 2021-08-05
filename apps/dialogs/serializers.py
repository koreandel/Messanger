from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.utils import model_meta
import traceback
from .models import Thread, Message


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = (
            "id",
            "participants",
        )

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)
        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        if not instance:
            raise NotFound("This object is not exist")
        instance.save()
        if instance.participant_users.count() < 1:
            instance.delete()
        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    def validate_participants(self, participants):
        if not (len(participants) <= 2):
            raise ValidationError("Not right quantity of participants")
        return participants

    def validate(self, attrs):
        if not attrs:
            raise ValidationError("Not right quantity of participants")
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id",
            "text",
            "sender",
            "thread",
            "is_read",
        )

    def validate_sender(self, sender):
        if not isinstance(sender.id, int):
            raise ValidationError("Not that type")
        return sender

    def validate_thread(self, thread):
        if not isinstance(thread.id, int):
            raise ValidationError("Not that type")
        return thread

    def validate_is_read(self, is_read):
        if not isinstance(is_read, bool):
            raise ValidationError("Not that type")
        return is_read

    def create(self, validated_data):
        ModelClass = self.Meta.model

        if not Thread.objects.filter(
            participants=self.context.get("request").user.id,
            id=validated_data.get("thread").id,
        ):
            raise NotFound("You have not permission")

        elif not (
            self.context.get("request").user.id == int(validated_data.get("sender").id)
        ):
            raise NotFound("You have not permission")
        try:
            instance = ModelClass._default_manager.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                "Got a `TypeError` when calling `%s.%s.create()`. "
                "This may be because you have a writable field on the "
                "serializer class that is not a valid argument to "
                "`%s.%s.create()`. You may need to make the field "
                "read-only, or override the %s.create() method to handle "
                "this correctly.\nOriginal exception was:\n %s"
                % (
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    ModelClass.__name__,
                    ModelClass._default_manager.name,
                    self.__class__.__name__,
                    tb,
                )
            )
            raise TypeError(msg)

        return instance

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)
        if isinstance(validated_data.get("is_read"), list):
            for value in validated_data.get("is_read"):
                message = Message.objects.filter(
                    pk=value, thread=validated_data.get("pk")
                ).first()
                if not message:
                    continue
                if not Message.objects.filter(sender=validated_data.get("user")):
                    raise NotFound("You have not permission")
                instance.save()
        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        if not instance:
            raise NotFound("This object is not exist")
        if not (self.context.get("request").user.id == instance.sender.id):
            raise NotFound("You have not permission")
        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class ThreadListSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    count_unread = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ("id", "last_message", "count_unread")

    def get_last_message(self, instance):
        if instance.thread_message.last():
            return instance.thread_message.order_by("created_at").last().text
        return None

    def get_count_unread(self, instance):
        if instance.thread_message.last():
            return instance.thread_message.filter(is_read=False).count()
        return None
