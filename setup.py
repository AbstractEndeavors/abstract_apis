import setuptools,glob,os
def make_list(obj:any) -> list:
    if isinstance(obj, list):
        return obj
    return [obj]
def read_from_file(file_path) -> str:
    with open(file_path, 'r', encoding='UTF-8') as f:
        return f.read()
def get_abs_path():
    return os.path.abspath(__name__)
def get_abs_dir():
    return os.path.dirname(get_abs_path())
def get_readme_file_paths(abs_dir=None):
    abs_dir = abs_dir or get_abs_dir()
    if os.path.isfile(abs_dir):
        abs_dir = os.path.dirname(abs_dir)

    pattern = os.path.join(abs_dir, '**', f'README.md')
    readme_file_paths = make_list(glob.glob(pattern, recursive=True) or '')
    return readme_file_paths
def get_readme_path(abs_path=None):
    readme_file_paths = get_readme_file_paths(abs_path)
    for readme_file_path in readme_file_paths:
        if os.path.isfile(readme_file_path):
            return readme_file_path
def get_readme_data(readme_file_path=None,abs_path=None):
    readme_file_path = readme_file_path or get_readme_path(abs_path)
    long_description = ''
    if os.path.isfile(readme_file_path):
        long_description = read_from_file(readme_file_path)
    return long_description
setuptools.setup(
    name='abstract_apis',
    version='0.0.0.81',
    author='putkoff',
    author_email='partners@abstractendeavors.com',
    description='The abstract_apis module is a Python library for simplifying HTTP request management. It abstracts common tasks such as header management, URL construction, and response parsing. It also provides support for handling Solana Blockchain API via RPC calls.',
    long_description=get_readme_data(),
    long_description_content_type='text/markdown',
    url='https://github.com/AbstractEndeavors/abstract_apis',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=['Development Status :: 3 - Alpha', 'Intended Audience :: Developers', 'Topic :: Software Development :: Libraries', 'License :: OSI Approved :: MIT License', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7', 'Programming Language :: Python :: 3.8', 'Programming Language :: Python :: 3.9'],
    install_requires=['requests', 'abstract_utilities', 'aiohttp'],
    python_requires='>=3.6',
    setup_requires=['wheel'],
)
