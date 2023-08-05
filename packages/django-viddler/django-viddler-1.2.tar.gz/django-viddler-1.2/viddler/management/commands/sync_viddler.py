from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-s', '--since',
            action='store',
            dest='since',
            help='Synchronize all videos since the YYYY-MM-DD. Defaults'
                 ' to the latest "upload_time" value in the database.'
        ),
    )
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from viddler.models import ViddlerVideo, make_model_from_api
        from viddler.settings import get_viddler
        viddler = get_viddler()
        viddler_kwargs = {'per_page': 100}
        try:
            if options['since']:
                viddler_kwargs['min_upload_date'] = options['since']
            else:
                v = ViddlerVideo.objects.latest('upload_time')
                viddler_kwargs['min_upload_date'] = v.upload_time.strftime('%Y-%m-%d')
        except (ViddlerVideo.DoesNotExist, ValueError):
            pass

        results = viddler.videos.search_yourvideos(**viddler_kwargs)
        for item in results:
            self.stdout.write('Adding: %s' % item['title'])
            make_model_from_api(item)
