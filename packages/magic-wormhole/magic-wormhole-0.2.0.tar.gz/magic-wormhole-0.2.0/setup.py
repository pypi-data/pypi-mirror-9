
from setuptools import setup

import versioneer
versioneer.VCS = "git"
versioneer.versionfile_source = "src/wormhole/_version.py"
versioneer.versionfile_build = "wormhole/_version.py"
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = "magic-wormhole"

commands = versioneer.get_cmdclass()

setup(name="magic-wormhole",
      version=versioneer.get_version(),
      description="Securely transfer data between computers",
      author="Brian Warner",
      author_email="warner-magic-wormhole@lothar.com",
      license="MIT",
      url="https://github.com/warner/magic-wormhole",
      package_dir={"": "src"},
      packages=["wormhole",
                "wormhole.blocking", "wormhole.twisted",
                "wormhole.scripts", "wormhole.test", "wormhole.util",
                "wormhole.servers"],
      entry_points={"console_scripts":
                    ["wormhole = wormhole.scripts.runner:entry"]},
      install_requires=["spake2==0.2", "pynacl", "requests", "argparse"],
      test_suite="wormhole.test",
      cmdclass=commands,
      )
