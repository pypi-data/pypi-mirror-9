#[MEMPIRE Python Distribution 'setup.py' Style]
#
# <Directory Structure>
# ==================================== 
# mempy/
#     setup.py
#     mempy/
#             __init__.py
#             lifecode.py
#             ichingbase.py
#             .............
#             lib/
#                 transdate.py
#                 ...........
#     __doc__/
#     __tst__/
#     __powered by Python 3.4.1__.txt
# ====================================

from setuptools import setup, find_packages  

setup(
    name = 'mempy',
    version='0.1.0',
    description='MEMPIRE Python Library',    
    long_description = 
    """
Mempy is a Python Library of MEMPIRE. It provides an interface to manipulate 
Time, System, OS and many things about Iching, LifeCode(Saju) etc.
""",
    author='Herokims',
    author_email='herokims@gmail.com',
    license = 'BSD',
    url = 'http://treeinsight.org/',
    #packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages=find_packages(),
    #package_data = {'':['*.xml']},
)
