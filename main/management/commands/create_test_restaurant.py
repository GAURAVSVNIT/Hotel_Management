from django.core.management.base import BaseCommand
from main.models import Restaurant

class Command(BaseCommand):
    help = 'Creates a test restaurant'

    def handle(self, *args, **kwargs):
        restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            location='Test Location',
            description='A test restaurant with delicious food and great ambiance.'
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created restaurant: {restaurant.name}'))
