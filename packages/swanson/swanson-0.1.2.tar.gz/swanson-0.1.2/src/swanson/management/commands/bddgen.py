from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *paths, **options):
        import importlib
        import os
        import os.path
        import re

        from swanson import settings
        from swanson.data import Feature

        def main(paths):
            generated_filenames = []

            module_name, cls_name = settings.CODE_GENERATOR.rsplit('.', 1)
            code_gen_cls = getattr(importlib.import_module(module_name), cls_name)()

            for path in paths:
                for feature_filename in iter_feature_filenames(path):
                    feature = Feature.from_filename(feature_filename)

                    test_filename = re.sub(r'\.feature$', '.py', feature_filename)
                    test_filename = os.path.join(
                        os.path.dirname(test_filename),
                        'test_{}'.format(os.path.basename(test_filename))
                    )
                    
                    if not os.path.isfile(test_filename):
                        test_module_source = code_gen_cls.generate_test_module(feature)
                        with open(test_filename, 'w') as fp:
                            fp.write(test_module_source)
                        generated_filenames.append(test_filename)

            if generated_filenames:
                self.stdout.write('Generated code:\n{}'.format('\n'.join(
                    ' * {}'.format(os.path.relpath(filename))
                    for filename in generated_filenames
                )))
            else:
                self.stdout.write('No files to generate')

        def iter_feature_filenames(path):
            for path, _, basenames in os.walk(path):
                for basename in basenames:
                    if basename.endswith('.feature'):
                        yield os.path.join(path, basename)

        main(paths or ('.',))
