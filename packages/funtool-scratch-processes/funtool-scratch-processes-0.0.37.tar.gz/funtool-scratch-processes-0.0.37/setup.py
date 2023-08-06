from setuptools import setup

setup(name='funtool-scratch-processes',
        version='0.0.37',
        description='process to be used with the FUN Tool to analyze Scratch projects',
        author='Active Learning Lab',
        author_email='pjanisiewicz@gmail.com',
        license='MIT',
        packages=[
            'funtool_scratch_processes',
            'funtool_scratch_processes.adaptors',
            'funtool_scratch_processes.analysis_selectors',
            'funtool_scratch_processes.group_measures',
            'funtool_scratch_processes.grouping_selectors',
            'funtool_scratch_processes.reporters',
            'funtool_scratch_processes.state_measures'
        ],
        install_requires=['funtool'],
        classifiers=[ 
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],  
        zip_safe=False)
