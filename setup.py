import setuptools
from pathlib import Path

package_name = "app-page"
version = '0.0.51'
# 读取 README.md 作为长描述
long_description = open("README.md", encoding="utf-8").read()
# 读取 requirements.txt 文件
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=package_name,
    version=version,
    author="xiaohuicat",  # 作者名称
    author_email="1258702350@qq.com", # 作者邮箱
    description="PySide6 page application framework", # 库描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaohuicat/python-app-page", # 库的官方地址
    license="MIT",
    packages=setuptools.find_packages(),
    package_data={
        'app_page': ['*', 'assets/*', 'assets/*/*'],
    },
    install_requires=requirements,
    zip_safe=False,
)