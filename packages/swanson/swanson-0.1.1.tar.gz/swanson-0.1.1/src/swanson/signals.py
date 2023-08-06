import django.dispatch

pre_scenario_test = django.dispatch.Signal(providing_args=('feature_filename', 'scenario_title'))
