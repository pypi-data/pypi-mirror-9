import django.dispatch


state_change = django.dispatch.Signal(
    providing_args=["instance", "state_from", "state_to"])
