from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0006_class_year_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='submission_type',
            field=models.CharField(
                choices=[('file_upload', 'File Upload'), ('text_entry', 'Text Entry'), ('both', 'File or Text')],
                default='file_upload',
                max_length=20,
            ),
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='content',
            new_name='text_content',
        ),
    ]
