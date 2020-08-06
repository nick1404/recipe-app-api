import time
from django.db import connections
from django.db.utils import OperationalError # Error to be shown if DB is not available
from django.core.management.base import BaseCommand # Parent class

class Command(BaseCommand):
    '''Django Command to pause execution until DB is available'''
    
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database') # Prints to terminal
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 sec')
                time.sleep(1) # Sleep for one sec
        self.stdout.write(self.style.SUCCESS('Database available!')) # If connection succeeds