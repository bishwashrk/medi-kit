"""
Serializers for doctor-patient chat.
"""

from rest_framework import serializers

from .models import ChatThread, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'thread',
            'sender_id',
            'sender_name',
            'sender_role',
            'content',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'thread',
            'sender_id',
            'sender_name',
            'sender_role',
            'is_read',
            'read_at',
            'created_at',
        ]


class ChatThreadListSerializer(serializers.ModelSerializer):
    appointment_id = serializers.IntegerField(source='appointment.id', read_only=True)
    appointment_reference = serializers.CharField(source='appointment.reference_number', read_only=True)
    appointment_date = serializers.DateField(source='appointment.appointment_date', read_only=True)
    other_party = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_at = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = [
            'id',
            'appointment_id',
            'appointment_reference',
            'appointment_date',
            'other_party',
            'last_message',
            'last_message_at',
            'unread_count',
            'updated_at',
            'created_at',
        ]

    def _get_other_user(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.patient
        return obj.doctor if request.user.id == obj.patient_id else obj.patient

    def get_other_party(self, obj):
        user = self._get_other_user(obj)
        return {
            'id': user.id,
            'name': user.get_full_name(),
            'role': user.role,
            'avatar': user.avatar.url if user.avatar else None,
        }

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        return msg.content if msg else ''

    def get_last_message_at(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        return msg.created_at if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=request.user).count()


class ChatThreadDetailSerializer(serializers.ModelSerializer):
    appointment_id = serializers.IntegerField(source='appointment.id', read_only=True)
    appointment_reference = serializers.CharField(source='appointment.reference_number', read_only=True)
    appointment_date = serializers.DateField(source='appointment.appointment_date', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = ChatThread
        fields = [
            'id',
            'appointment_id',
            'appointment_reference',
            'appointment_date',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
