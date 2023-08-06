from setuptools import setup

setup(
    name='pyClients',
    version = '0.1',
    description='Clientes (fuente y consumidor) para https://github.com/matias-martinez/internetworking-streaming',
    author='Rodrigo',
    author_email='jacznik.rodrigo@gmail.com',
    packages = ['pyClients'],
    license='GPL2',
    install_requires=['pySerial'],
    use_2to3 = True,
)
