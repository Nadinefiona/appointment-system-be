from django.core.validators import MaxValueValidator
from django.db import migrations, models

MAX_BUFFER_MINUTES = 480


def cap_buffer_times(apps, schema_editor):
    ServiceProvider = apps.get_model("providers", "ServiceProvider")
    ServiceProvider.objects.filter(buffer_time__gt=MAX_BUFFER_MINUTES).update(
        buffer_time=MAX_BUFFER_MINUTES
    )


class Migration(migrations.Migration):

    dependencies = [
        ("providers", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(cap_buffer_times, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="serviceprovider",
            name="buffer_time",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Buffer in minutes (max 480)",
                validators=[MaxValueValidator(MAX_BUFFER_MINUTES)],
            ),
        ),
    ]
