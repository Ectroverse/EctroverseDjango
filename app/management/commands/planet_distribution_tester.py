from django.core.management.base import BaseCommand
import matplotlib.pyplot as plt

from app.calculations import planet_size_distribution


class Command(BaseCommand):  # must be called command, use file name to name the functionality
    def handle(self, *args, **options):
        samples = []
        for i in range(100000):
            samples.append(planet_size_distribution())
        print(samples)
        count, bins, ignored = plt.hist(samples, 50)
        plt.show()
