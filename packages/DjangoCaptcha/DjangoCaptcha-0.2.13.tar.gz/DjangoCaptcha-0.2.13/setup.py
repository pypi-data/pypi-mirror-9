#encoding:utf-8
from distutils.core import setup  
setup(name='DjangoCaptcha',  
      author='TY(pythoner.org)',  
      author_email='tianyu0915@gmail.com',  
      version='0.2.13',  
      description='在django中生成英文/数字公式验证码',  
      keywords ='django captcha 验证码',
      url='http://github.com/tianyu0915/DjangoCaptcha',  
      packages=['DjangoCaptcha'],  
      install_requires=['pillow'],
      package_data={'DjangoCaptcha':['*.*','DjangoCaptcha/*.*']},

)  
