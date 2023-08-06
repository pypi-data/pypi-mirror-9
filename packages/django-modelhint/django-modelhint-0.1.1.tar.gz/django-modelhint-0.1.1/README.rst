django-annotation
========================================

when model definition

.. code-block:: python

   import django_annoation as d
   d.get_default_mapping().add_reserved_words(doc="")

   class Group(models.Model):
       name = d.CharField(max_length=255, verbose_name="Name", doc="名前")

   class User(models.Model):
       group = d.ForeignKey(Group)
       name = d.CharField(max_length=255, verbose_name="Name", doc="名前")


when view

.. code-block:: python

   import django_annotation as d
   user = User.objects.get()
   d.get_mapping(user)  # => ChainMap({}, {'name': ChainMap({}, {'doc': '名前'}), 'id': ChainMap({}, {'doc': ''}), 'group': ChainMap({}, {'doc': ''})})
   d.get_mapping(user)["name"]["doc"]  # => '名前'

   group = Group.objects.get()
   d.get_mapping(group.user_set)  # => ChainMap({}, {'name': ChainMap({}, {'doc': '名前'}), 'id': ChainMap({}, {'doc': ''}), 'group': ChainMap({}, {'doc': ''})})


