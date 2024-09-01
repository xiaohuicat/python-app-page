import setuptools

package_name = "app-page"
version = '0.0.2'
long_description = open("README.md", encoding="utf-8").read()

setuptools.setup(
    name=package_name,
    version=version,
    author="xiaohuicat",  # 作者名称
    author_email="1258702350@qq.com", # 作者邮箱
    description="python page application framework", # 库描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaohuicat/python-app-page", # 库的官方地址
    license="MIT",
    packages=["app_page"],
    install_requires=[
        "nanoid"
    ],
    zip_safe=False,
)