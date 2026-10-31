from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def atribuir_autor(apps, schema_editor):
    Post = apps.get_model('artigos', 'Post')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    banco = schema_editor.connection.alias
    if Post.objects.using(banco).filter(autor__isnull=True).exists():
        autor = User.objects.using(banco).filter(is_staff=True).order_by('pk').first()
        if autor is None:
            autor, _ = User.objects.using(banco).get_or_create(username='autor_legado', defaults={'password': '!', 'is_active': False})
        Post.objects.using(banco).filter(autor__isnull=True).update(autor_id=autor.pk)


class Migration(migrations.Migration):
    dependencies = [('artigos', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='post', name='autor', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
        migrations.RunPython(atribuir_autor, migrations.RunPython.noop),
        migrations.AlterField(model_name='post', name='autor', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
    ]
