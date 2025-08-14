from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import (
    UserRole,
    Subject,
    Theme,
    Lesson,
    Enrollment,
    Badge,
    UserBadge,
)


class StatsBadgesAPITest(APITestCase):
    def setUp(self):
        # create users
        self.student = User.objects.create_user(username="student", password="pass")
        self.teacher = User.objects.create_user(username="teacher", password="pass")

        UserRole.objects.create(user=self.student, role="student")
        UserRole.objects.create(user=self.teacher, role="teacher")

        # create courses
        self.subject1 = Subject.objects.create(name="Course 1", teacher=self.teacher)
        self.subject2 = Subject.objects.create(name="Course 2", teacher=self.teacher)

        # themes and lessons
        theme1 = Theme.objects.create(name="T1", subject=self.subject1)
        theme2 = Theme.objects.create(name="T2", subject=self.subject2)
        for i in range(3):
            Lesson.objects.create(name=f"L1-{i}", theme=theme1)
        for i in range(4):
            Lesson.objects.create(name=f"L2-{i}", theme=theme2)

        # enrollments
        Enrollment.objects.create(
            student=self.student,
            subject=self.subject1,
            status="completed",
            progress_percentage=100,
        )
        Enrollment.objects.create(
            student=self.student,
            subject=self.subject2,
            status="active",
            progress_percentage=50,
        )

        # badges
        self.badge1 = Badge.objects.create(
            name="Badge 1", badge_type="course_completion", subject=self.subject1
        )
        self.badge2 = Badge.objects.create(
            name="Badge 2", badge_type="course_completion", subject=self.subject2
        )
        UserBadge.objects.create(user=self.student, badge=self.badge1)

    def test_student_stats(self):
        self.client.force_authenticate(self.student)
        url = "/api/lms/stats/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_courses_enrolled"], 2)
        self.assertEqual(data["total_courses_completed"], 1)
        self.assertIn("courses", data)
        self.assertEqual(len(data["courses"]), 2)

    def test_badges(self):
        self.client.force_authenticate(self.student)
        resp = self.client.get("/api/lms/badges/")
        self.assertEqual(resp.status_code, 200)
        cats = resp.json()
        self.assertEqual(len(cats), 1)
        cat = cats[0]
        self.assertEqual(cat["earned_count"], 1)
        self.assertEqual(len(cat["badges"]), 2)

    def test_teacher_can_view_student(self):
        self.client.force_authenticate(self.teacher)
        resp = self.client.get("/api/lms/stats/", {"user_id": self.student.id})
        self.assertEqual(resp.status_code, 200)

    def test_student_cannot_view_other(self):
        other = User.objects.create_user(username="other", password="pass")
        UserRole.objects.create(user=other, role="student")
        self.client.force_authenticate(self.student)
        resp = self.client.get("/api/lms/stats/", {"user_id": other.id})
        self.assertEqual(resp.status_code, 403)

