import json

from django.core.management.base import BaseCommand


class BaseLoadCommand(BaseCommand):
    model = None

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Путь к JSON-файлу'
        )

    class Command(BaseCommand):
        help = 'Импорт данных из JSON-файла'

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, encoding='utf-8') as file:
                data = json.load(file)
        except Exception as err:
            self.stderr.write(self.style.ERROR(
                f'Ошибка при обработке файла {file_path}: {err}'
            ))
            return

        created = self.model.objects.bulk_create(
            (self.model(**item) for item in data),
            ignore_conflicts=True
        )
        count = len(created)
        self.stdout.write(
            self.style.SUCCESS(
                f'Добавлено {count} объектов из файла "{file_path}"'
            )
        )
