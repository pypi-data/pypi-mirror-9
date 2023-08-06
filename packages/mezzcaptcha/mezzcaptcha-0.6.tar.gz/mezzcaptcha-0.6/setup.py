from setuptools import setup, find_packages

setup(name="mezzcaptcha",
      version="0.6",
      description="Mezzanine forms with captchas",
      long_description="""\
Includes a comment form and a sign-up form with captchas. The comment form will 
display a captcha to guest users but will not display a captcha to logged in uers.

See https://github.com/phookit/phookitmezz-captcha for usage instructions.
""",
      author="Paul Hunt",
      author_email="paul@phookit.com",
      url="https://github.com/phookit/phookitmezz-captcha",
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      install_requires=['django-simple-captcha>=0.4.4',],
)

