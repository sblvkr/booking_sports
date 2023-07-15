from rest_framework import serializers

from api.serializers.fields import Base64ImageField
from api.serializers.users import UserReadSerializer
from playground.models import (
    Covering, Sport, Playground,
    ImagePlayground
)


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'sport_name', 'sport_slug')
        model = Sport


class CoveringSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'covering_name', 'covering_slug')
        model = Covering


class ImageWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        required=True,
    )

    class Meta:
        fields = (
            'id', 'image', 'main_image',
            'description_image',
        )
        model = ImagePlayground


class PlaygroundReadSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(
        many=False, read_only=True,
    )
    images = ImageWriteSerializer(
        read_only=True,
        many=True,
        source='playground_images',
    )
    sports = SportSerializer(
        read_only=True,
        many=True,
    )
    covering = CoveringSerializer(
        read_only=True,
    )

    class Meta:
        fields = (
            'id', 'playground_name', 'playground_type',
            'size', 'playground_price', 'address',
            'owner', 'description', 'sports', 'covering',
            'shower', 'changing_rooms', 'lighting', 'parking',
            'stands', 'playground_slug', 'images',
        )
        model = Playground


class PlaygroundWriteSerializer(serializers.ModelSerializer):
    owner = UserReadSerializer(
        many=False, read_only=True
    )
    sports = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Sport.objects.all(),
    )
    covering = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True,
        queryset=Covering.objects.all(),
    )
    images = ImageWriteSerializer(
        required=False,
        many=True,
    )

    class Meta:
        fields = (
            'id', 'playground_name', 'playground_type',
            'size', 'playground_price', 'address',
            'owner', 'description', 'sports', 'covering',
            'shower', 'changing_rooms', 'lighting', 'parking',
            'stands', 'playground_slug', 'images',
        )
        model = Playground

    def create(self, validated_data):
        if 'images' not in self.initial_data:
            return Playground.objects.create(**validated_data)
        images = validated_data.pop('images')
        sports = validated_data.pop('sports')
        playground = Playground.objects.create(**validated_data)
        playground.sports.set(sports)
        for image in images:
            status = ImagePlayground.objects.get_or_create(
                **image, playground=playground,
            )
        playground.save()
        return playground

    def update(self, instance, validated_data):
        images = validated_data.get('images')
        sports = validated_data.get('sports')
        covering = validated_data.get('covering')
        if sports:
            instance.sports.set(sports)
        if covering:
            instance.covering = covering
        if images:
            ImagePlayground.objects.filter(playground=instance).delete()
            for image in images:
                ImagePlayground.objects.create(playground=instance, **image)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return PlaygroundReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data