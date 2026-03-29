from django.db import migrations


def consolidate_locations(apps, schema_editor):
    Location = apps.get_model("api", "Location")
    Item = apps.get_model("api", "Item")
    Appointment = apps.get_model("api", "Appointment")

    # 1. Rename the 3 keepers to simple campus names
    Location.objects.filter(pk=1).update(name="Casa Loma", campus="Casa Loma", building="")
    Location.objects.filter(pk=4).update(name="St. James", campus="St. James", building="")
    Location.objects.filter(pk=5).update(name="Waterfront", campus="Waterfront", building="")

    # 2. Reassign items from locations being deleted → nearest campus
    #    pk=3  (Library - Casa Loma)      → pk=1  (Casa Loma)
    #    pk=7  (Room 200 - Casa Loma)     → pk=1  (Casa Loma)
    #    pk=8  (Parking Lot B - St. James) → pk=4  (St. James)
    #    pk=6  (Gym - Daniels Laing)      → pk=1  (Casa Loma)  closest campus
    Item.objects.filter(location__in=[3, 7, 6]).update(location=1)
    Item.objects.filter(location=8).update(location=4)

    # 3. Reassign appointments too
    Appointment.objects.filter(location__in=[3, 7, 6]).update(location=1)
    Appointment.objects.filter(location=8).update(location=4)

    # 4. Delete the surplus locations
    Location.objects.filter(pk__in=[3, 6, 7, 8]).delete()


def reverse_consolidate(apps, schema_editor):
    """Best-effort reverse: recreate deleted locations (items stay on campus)."""
    Location = apps.get_model("api", "Location")
    for pk, name, campus, building in [
        (3, "Library - Casa Loma", "GBC - Casa Loma Campus", "Main Building"),
        (6, "Gym - Daniels Laing", "GBC - Daniels Laing Campus", "Main Building"),
        (7, "Room 200 - Casa Loma", "GBC - Casa Loma Campus", "Main Building"),
        (8, "Parking Lot B - St. James", "GBC - St. James Campus", "Building B"),
    ]:
        Location.objects.create(pk=pk, name=name, campus=campus, building=building)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_passwordresettoken"),
    ]

    operations = [
        migrations.RunPython(consolidate_locations, reverse_consolidate),
    ]
