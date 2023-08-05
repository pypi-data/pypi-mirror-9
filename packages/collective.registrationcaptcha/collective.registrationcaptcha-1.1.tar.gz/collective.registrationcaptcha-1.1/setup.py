from setuptools import setup
from setuptools import find_packages

version = '1.1'
description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

setup(
    name='collective.registrationcaptcha',
    version=version,
    description="Add a captcha field to the registration form.",
    long_description=description,
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='plone user captcha',
    author='Johannes Raggam',
    author_email='raggam-nl@adm.at',
    url='https://github.com/collective/collective.registrationcaptcha',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFCore',
        'plone.app.discussion',
        'plone.app.users>=2.0',
        'plone.protect',
        'plone.registry',
        'plone.z3cform',
        'z3c.form',
        'zope.component',
        'zope.interface',
        'zope.publisher',
    ],
    extras_require={
        'captchawidgets': [
            'plone.formwidget.captcha',
            'plone.formwidget.recaptcha',
            'collective.z3cform.norobots',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
