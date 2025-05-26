import json
from django.core.management.base import BaseCommand
from kal_app.models import Alimento

class Command(BaseCommand):
    help = 'Importa alimentos desde un archivo JSON a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('ruta_json', type=str, help='Ruta al archivo JSON con los alimentos')

    def handle(self, *args, **kwargs):
        ruta_json = kwargs['ruta_json']

        try:
            with open(ruta_json, 'r', encoding='utf-8') as file:
                data = json.load(file)

            count = 0
            for item in data:
                alimento, creado = Alimento.objects.get_or_create(
                    codigo=item['codigo'],
                    defaults={
                        'nombre_es': item['nombre_es'],
                        'nombre_en': item['nombre_en'],
                        'calorias': item['calorias'],
                        'grasas': item['grasas'],
                        'proteinas': item['proteinas'],
                        'carbohidratos': item['carbohidratos'],
                        'medida': item['medida'],
                    }
                )
                if creado:
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'{count} alimentos importados correctamente.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error al importar: {str(e)}'))