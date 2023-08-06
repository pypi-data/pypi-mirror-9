from setuptools import setup

setup(
    name='thread_safe_vk',
    version='0.1.1',
    packages=['thread_safe_vk', 'thread_safe_vk.utils'],
    url='https://github.com/soon/ThreadSafeVk',
    license='MIT',
    author='Andrew Kuchev',
    author_email='kuchevad@gmail.com',
    description='',
    keywords='thread safe vk api',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities'
    ],

    install_requires=['vk'],
)
