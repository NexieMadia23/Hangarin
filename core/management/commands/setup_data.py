from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from core.models import Category, Priority, Task, SubTask, Note
import random

class Command(BaseCommand):
    help = 'Populates the database with manual and fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write("Seeding data...")

        # 1. Requirement: Manually add Category and Priority
        cat_names = ['Work', 'School', 'Personal', 'Finance', 'Projects']
        prio_names = ['High', 'Medium', 'Low', 'Critical', 'Optional']

        categories = [Category.objects.get_or_create(name=name)[0] for name in cat_names]
        priorities = [Priority.objects.get_or_create(name=name)[0] for name in prio_names]

        # 2. Requirement: Use Faker for Tasks, Notes, and SubTasks
        for _ in range(15):  # Creating 15 tasks
            task = Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                status=fake.random_element(elements=["Pending", "In Progress", "Completed"]),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                priority=random.choice(priorities),
                category=random.choice(categories),
            )

            # Seed SubTasks
            for _ in range(random.randint(1, 3)):
                SubTask.objects.create(
                    task=task,
                    title=fake.sentence(nb_words=3),
                    status=fake.random_element(elements=["Pending", "In Progress", "Completed"])
                )

            # Seed Notes
            Note.objects.create(
                task=task,
                content=fake.paragraph(nb_sentences=2)
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated Hangarin with professional data!'))