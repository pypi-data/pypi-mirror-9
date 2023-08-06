from cloudmesh_base.util import banner

def auto_create_version(class_name, version):
    with open("{0}/__init__.py".format(class_name), "r") as f:
        content = f.read()

    if content != 'version = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open("{0}/__init__.py".format(class_name), "w") as text_file:
            text_file.write(u'version = "{0:s}"'.format(version))