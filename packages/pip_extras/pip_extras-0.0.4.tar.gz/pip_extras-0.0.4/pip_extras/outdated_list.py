from pip.commands import ListCommand
from pip.commands import InstallCommand


class OutdatedList(object):
    def __init__(self):
        self.list_cmd = ListCommand()
        self.options, self.args = self.list_cmd.parse_args(['-o'])
        
    def display_version(self, version):
        if isinstance(version, tuple):
            return ".".join(part.lstrip('0') or '0' for part in version)
        return version.public

    @property
    def outdated(self):
        for package_data in self.list_cmd.find_packages_latests_versions(self.options):
            dist, remote_version = package_data[0], package_data[1:]
            if len(remote_version) == 1:  # Later versions of pip
                remote_version_parsed = remote_version[0]
            else:
                remote_version_parsed = remote_version[-1]
            if remote_version_parsed > dist.parsed_version:
                yield dist.project_name, dist.parsed_version, remote_version_parsed
                
    def update(self, package_name):
        print("Would install " + package_name)
        install_command = InstallCommand()
        install_command.main(['-U', package_name])
