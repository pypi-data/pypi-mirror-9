from setuptools import setup, find_packages
import version

setup(
    name = "m4pomodoro",
    version = version.getVersion(),
    author = "Marc Siegenthaler",
    author_email = "shin@marcsi.ch",
    description = "simple pomodoro app",
    keywords = "tray pomodoro",
    license="MIT",
    packages = find_packages(),
    install_requires = ['pygobject'],
    entry_points= {
        'console_scripts': [
            'm4pomodoro = m4pomodoro.main:main',
        ]
    },
    include_package_data = True,
)
