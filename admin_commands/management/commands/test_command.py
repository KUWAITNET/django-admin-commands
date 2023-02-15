from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Recalculate net days for vacation request to consider changed holidays and weekends updates. \n' \
           'If no IDs are provided, all vacation requests will be updated. \n' \
           'Use --update to perform the update. Without it this is a test run. \n' \
           'Example: python manage.py recalculate_net_days --ids 1 2 3 --update '

    def add_arguments(self, parser):
        parser.add_argument('--ids', nargs='+', type=int, help='IDs of Vacation Requests to update.')
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            help='Perform the update',
        )

    def handle(self, *args, **options):
        for i in range(10):
            self.stdout.write(f'#{i} {i} Vacation Request from x to y log')
