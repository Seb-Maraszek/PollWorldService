from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from polls.models import Poll, Question, QuestionOption, Answer


class pollSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Poll
        exclude = ['assigned_users']


class answerSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    options = serializers.ListField()
    text_answer = serializers.CharField()

    def create(self, validated_data):
        answer = Answer.objects.create(
            user=self.context['user'],
            question_id=validated_data['question'],
            text_answer=validated_data['text_answer'],
        )

        answer.set_options(options=validated_data['options'])
        return answer

    def validate(self, attrs):
        try:
            question = Question.objects.get(id=attrs['question'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Question, with that id does not exist!")
        available_options_ids = [option_id.get('id') for option_id in
                                 QuestionOption.objects.filter(question=question).values('id')]
        for item in attrs['options']:
            if item not in available_options_ids:
                raise serializers.ValidationError("Wrong ID in options!")
        if question.type == 'SINGLE' and len(attrs['options']) > 1:
            raise serializers.ValidationError("More than one option in single choice field!")
        if question.type == 'TEXT' and len(attrs['options']) != 0:
            raise serializers.ValidationError("An option was sent to a text answer")
        return attrs

    def update(self, instance, validated_data):
        return instance


class questionOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class questionWithOptionSerializer(serializers.ModelSerializer):
    options = questionOptionSerializer(source='questionoption_set', many=True)

    class Meta:
        model = Question
        exclude = ['poll']


class questionInputSerializer(serializers.Serializer):
    type = serializers.CharField()
    name = serializers.CharField()
    required = serializers.BooleanField()
    options = serializers.ListField()


class questionOptionStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    popularity = serializers.IntegerField()


class questionStatsSerializer(serializers.ModelSerializer):
    options = questionOptionStatsSerializer(source='questionoption_set', many=True)

    class Meta:
        model = Question
        fields = ['id', 'name', 'options']


class questionWithPollSerializer(serializers.ModelSerializer):
    questions = questionInputSerializer(source='question_set', many=True)

    class Meta:
        model = Poll
        exclude = ['assigned_users', 'user']

    def validate(self, attrs):
        for question in attrs['question_set']:
            if question['type'] not in [question_type[0] for question_type in Question.QUESTION_TYPES]:
                raise serializers.ValidationError("Unknown question type")
            if question['type'] == 'TEXT' and question['options']:
                raise serializers.ValidationError("You cant add option to question with TEXT type")
            elif question['type'] != 'TEXT' and not question['options']:
                raise serializers.ValidationError(
                    "You have to add option to question with " + question['type'] + " type")
        return attrs

    def create(self, validated_data):
        poll = Poll.objects.create(user=self.context['user'],
                                   name=validated_data['name'],
                                   description=validated_data['description'],
                                   short_description=validated_data['short_description'],
                                   category=validated_data['category'])

        for question in validated_data['question_set']:
            Question.objects.create(
                poll=poll,
                required=question['required'],
                name=question['name'],
                type=question['type'],
            ).generate_options_from_names(question['options'])

        return validated_data
