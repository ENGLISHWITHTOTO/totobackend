from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.content.models import Category, Subcategory, Lesson, Exercise

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category_data = {
            "name": "English Grammar",
            "description": "Learn English grammar fundamentals",
            "order": 1,
        }

    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, "English Grammar")
        self.assertEqual(category.description, "Learn English grammar fundamentals")
        self.assertTrue(category.is_active)
        self.assertEqual(category.order, 1)

    def test_category_str_representation(self):
        """Test category string representation"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), "English Grammar")

    def test_category_default_values(self):
        """Test category default values"""
        category = Category.objects.create(
            name="Test Category", description="Test description"
        )
        self.assertTrue(category.is_active)
        self.assertEqual(category.order, 0)

    def test_category_ordering(self):
        """Test category ordering"""
        Category.objects.create(name="B", description="B desc", order=2)
        Category.objects.create(name="A", description="A desc", order=1)
        Category.objects.create(name="C", description="C desc", order=3)

        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "A")
        self.assertEqual(categories[1].name, "B")
        self.assertEqual(categories[2].name, "C")


class SubcategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="English Grammar", description="Learn English grammar fundamentals"
        )
        self.subcategory_data = {
            "category": self.category,
            "name": "Present Tense",
            "description": "Learn about present tense",
            "order": 1,
        }

    def test_create_subcategory(self):
        """Test creating a subcategory"""
        subcategory = Subcategory.objects.create(**self.subcategory_data)
        self.assertEqual(subcategory.category, self.category)
        self.assertEqual(subcategory.name, "Present Tense")
        self.assertTrue(subcategory.is_active)

    def test_subcategory_str_representation(self):
        """Test subcategory string representation"""
        subcategory = Subcategory.objects.create(**self.subcategory_data)
        self.assertEqual(str(subcategory), "English Grammar - Present Tense")

    def test_subcategory_ordering(self):
        """Test subcategory ordering"""
        Subcategory.objects.create(
            category=self.category, name="B", description="B desc", order=2
        )
        Subcategory.objects.create(
            category=self.category, name="A", description="A desc", order=1
        )

        subcategories = Subcategory.objects.all()
        self.assertEqual(subcategories[0].name, "A")
        self.assertEqual(subcategories[1].name, "B")


class LessonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="teacher@example.com", username="teacher"
        )
        self.category = Category.objects.create(
            name="English Grammar", description="Learn English grammar fundamentals"
        )
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Present Tense",
            description="Learn about present tense",
        )
        self.lesson_data = {
            "subcategory": self.subcategory,
            "title": "Simple Present Tense",
            "description": "Learn the basics of simple present tense",
            "content": {"type": "lesson", "sections": []},
            "difficulty_level": "beginner",
            "estimated_duration": 30,
            "created_by": self.user,
        }

    def test_create_lesson(self):
        """Test creating a lesson"""
        lesson = Lesson.objects.create(**self.lesson_data)
        self.assertEqual(lesson.title, "Simple Present Tense")
        self.assertEqual(lesson.difficulty_level, "beginner")
        self.assertEqual(lesson.estimated_duration, 30)
        self.assertFalse(lesson.is_published)

    def test_lesson_str_representation(self):
        """Test lesson string representation"""
        lesson = Lesson.objects.create(**self.lesson_data)
        self.assertEqual(str(lesson), "Simple Present Tense")

    def test_lesson_difficulty_choices(self):
        """Test lesson difficulty level choices"""
        valid_levels = ["beginner", "intermediate", "advanced"]
        for level in valid_levels:
            lesson = Lesson.objects.create(
                subcategory=self.subcategory,
                title=f"Test {level}",
                description="Test description",
                content={"type": "lesson"},
                difficulty_level=level,
                estimated_duration=30,
                created_by=self.user,
            )
            self.assertEqual(lesson.difficulty_level, level)

    def test_lesson_ordering(self):
        """Test lesson ordering by created_at"""
        lesson1 = Lesson.objects.create(**self.lesson_data)
        lesson2 = Lesson.objects.create(
            subcategory=self.subcategory,
            title="Past Tense",
            description="Learn past tense",
            content={"type": "lesson"},
            difficulty_level="beginner",
            estimated_duration=30,
            created_by=self.user,
        )

        lessons = Lesson.objects.all()
        self.assertEqual(lessons[0], lesson2)  # Most recent first
        self.assertEqual(lessons[1], lesson1)


class ExerciseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="teacher@example.com", username="teacher"
        )
        self.category = Category.objects.create(
            name="English Grammar", description="Learn English grammar fundamentals"
        )
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Present Tense",
            description="Learn about present tense",
        )
        self.lesson = Lesson.objects.create(
            subcategory=self.subcategory,
            title="Simple Present Tense",
            description="Learn the basics of simple present tense",
            content={"type": "lesson", "sections": []},
            difficulty_level="beginner",
            estimated_duration=30,
            created_by=self.user,
        )
        self.exercise_data = {
            "lesson": self.lesson,
            "exercise_type": "multiple_choice",
            "question": 'What is the correct form of "to be" in present tense?',
            "options": ["am", "is", "are", "All of the above"],
            "correct_answer": "All of the above",
            "explanation": "All forms are correct depending on the subject",
        }

    def test_create_exercise(self):
        """Test creating an exercise"""
        exercise = Exercise.objects.create(**self.exercise_data)
        self.assertEqual(exercise.lesson, self.lesson)
        self.assertEqual(exercise.exercise_type, "multiple_choice")
        self.assertEqual(
            exercise.question, 'What is the correct form of "to be" in present tense?'
        )

    def test_exercise_str_representation(self):
        """Test exercise string representation"""
        exercise = Exercise.objects.create(**self.exercise_data)
        expected = 'Simple Present Tense - What is the correct form of "to be" in present tense?'
        self.assertEqual(str(exercise), expected)

    def test_exercise_type_choices(self):
        """Test exercise type choices"""
        valid_types = ["multiple_choice", "fill_blank", "voice_response", "drag_drop"]
        for ex_type in valid_types:
            exercise = Exercise.objects.create(
                lesson=self.lesson,
                exercise_type=ex_type,
                question="Test question",
                correct_answer="Test answer",
            )
            self.assertEqual(exercise.exercise_type, ex_type)

    def test_exercise_ordering(self):
        """Test exercise ordering"""
        exercise1 = Exercise.objects.create(
            lesson=self.lesson,
            exercise_type="multiple_choice",
            question="Question 1",
            correct_answer="Answer 1",
            order=2,
        )
        exercise2 = Exercise.objects.create(
            lesson=self.lesson,
            exercise_type="multiple_choice",
            question="Question 2",
            correct_answer="Answer 2",
            order=1,
        )

        exercises = Exercise.objects.all()
        self.assertEqual(exercises[0], exercise2)  # Lower order first
        self.assertEqual(exercises[1], exercise1)
