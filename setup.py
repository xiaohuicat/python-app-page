import setuptools
import re

package_name = "app-page"

def curr_version():
    # 方法1：通过文件临时存储版本号
    with open('VERSION') as f:
        version_str = f.read()
    return version_str

def get_version():
    # 从版本号字符串中提取三个数字并将它们转换为整数类型
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", curr_version())
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    # 对三个数字进行加一操作
    patch += 1
    if patch > 9:
        patch = 0
        minor += 1
        if minor > 9:
            minor = 0
            major += 1
    new_version_str = f"{major}.{minor}.{patch}"
    return new_version_str

def upload():
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    with open("requirements.txt", "r", encoding="utf-8") as f:
        required = f.read().splitlines()

    setuptools.setup(
        name=package_name,
        version=get_version(),
        author="xiaohuicat",  # 作者名称
        author_email="1258702350@qq.com", # 作者邮箱
        description="python page application framework", # 库描述
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/xiaohuicat/python-app-page", # 库的官方地址
        license="MIT",
        packages=setuptools.find_packages(),
        data_files=["requirements.txt"], # app-page库依赖的其他库
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
        install_requires=required,
        zip_safe=False,
    )

def main():
    try:
        upload()
        print("Upload success , Current VERSION:", curr_version())
    except Exception as e:
        raise Exception("Upload package error", e)

if __name__ == '__main__':
    main()