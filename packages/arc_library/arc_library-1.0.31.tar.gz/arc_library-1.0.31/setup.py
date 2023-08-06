from distutils.core import setup
 
setup(
    name = 'arc_library',
    version = '1.0.31',
    # py_modules = ['arc_django_models', 'arc_functions', 'arc_jsonobject', 'arc_storage', 'arc_tag'],
	#py_modules = ['arc_library'],
    packages = ['arclib', 'arclib/django', 'arclib/gae', 'arclib/http'],
    author = 'Arcanelux',
    author_email = 'Arcanelux@gmail.com',
    url = 'iiii.so',
    description = 'Arcanelux Python Library',
)


