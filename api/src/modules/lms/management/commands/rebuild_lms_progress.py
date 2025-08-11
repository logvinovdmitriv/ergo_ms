from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from modules.lms.models import Enrollment, Topic, Lesson, TopicProgress, LessonProgress

User = get_user_model()

class Command(BaseCommand):
    help = "Rebuild LMS progress (topics/lessons) for all enrollments"

    def handle(self, *args, **opts):
        qs = Enrollment.objects.filter(is_active=True).select_related('user', 'course')
        with transaction.atomic():
            for en in qs:
                user = en.user
                course = en.course
                for lesson in Lesson.objects.filter(module__course=course, is_published=True):
                    LessonProgress.objects.get_or_create(user=user, lesson=lesson)
                for topic in Topic.objects.filter(lesson__module__course=course, is_published=True):
                    TopicProgress.objects.get_or_create(user=user, topic=topic)
