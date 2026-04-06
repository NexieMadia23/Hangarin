import os
import django
import random
from faker import Faker

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()

# 2. Import models (Removed 'Status' since the error says it's not a model)
from core.models import Task, Category, Priority 

def seed_tasks(num_tasks=25):
    fake = Faker()
    
    # Get existing relations from your DB
    categories = list(Category.objects.all())
    priorities = list(Priority.objects.all())

    # Standard Django choices for Status (if it's a CharField)
    status_options = ['Pending', 'In Progress', 'Completed']

    if not priorities or not categories:
        print("Error: Your Priority or Category tables are empty in the DB.")
        print("Check your Django Admin to make sure at least one exists!")
        return

    print(f"Generating {num_tasks} fake tasks...")

    for _ in range(num_tasks):
        # We grab a RANDOM Priority OBJECT from your database
        random_priority = random.choice(priorities)
        random_category = random.choice(categories)
        
        Task.objects.create(
            title=fake.sentence(nb_words=4).rstrip("."),
            description=fake.paragraph(nb_sentences=3),
            status=random.choice(status_options), # Using the string list here
            priority=random_priority,             # Using the actual DB object here
            category=random_category,
        )

    print(f"✅ Success! Generated {num_tasks} tasks.")

if __name__ == "__main__":
    seed_tasks(25)