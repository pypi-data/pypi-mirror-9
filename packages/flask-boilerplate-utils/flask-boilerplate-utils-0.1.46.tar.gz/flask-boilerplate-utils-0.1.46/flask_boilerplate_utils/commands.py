from flask.ext.script import Option, Manager, Command
import re
import json
import os
import zipfile
from io import BytesIO
from urllib.request import urlopen


# Manager Factory.
def MainManager(app, **kwargs):
    """
    A factory which creates a flask-script manager and configure it for use
    with the boilerplate. 

    :param kwargs: keyword arguments to send to flask-script's Manager
                   class initialiser
    """

    manager = Manager(app,**kwargs)
    manager.add_command('server', Run(app))
    manager.add_command('meinheld', Host(app))
    manager.add_command('install', InstallFramework(app))
    manager.add_command('import', Import(app))
    return manager


class BaseCommand(Command):
    """
    Base command class which comes with the default options
    """

    option_list = (Option('--config', '-c', dest='config', nargs=1, action='store', help='Provide'\
            'a configuation class defined in config.'),)

    def __init__(self, app):
        super(Command, self).__init__()
        self.app = app


class Run(BaseCommand):
    "Run the Flask Builtin Server (Not for production)"

    option_list = (
        Option('--hostname', '-h', dest='hostname', default='0.0.0.0', type=str),
        Option('--port', '-p', dest='port', default=None, type=int),
        Option('--debug', '-d', dest='debug', default=True, action='store_true'),       
    ) + BaseCommand.option_list

    def run(self, port, hostname, debug, config, **kwargs):
        if port is None and 'LISTEN_PORT' in self.app.config:
            port = self.app.config['LISTEN_PORT']
        else:
            port = 8000

        if hostname is None and 'LISTEN_HOST' in self.app.config:
            hostname = self.app.config['LISTEN_HOST']
        else:
            hostname = '0.0.0.0'

        self.app.run(debug=debug, host=hostname, port=port)

class Import(BaseCommand):
    def run(self):
        pass

class Host(BaseCommand):
    """
    Run a Web Server for Hosting using meinheld.
    """

    option_list = (
        Option('--hostname', '-h', dest='hostname', default='0.0.0.0', type=str),
        Option('--port', '-p', dest='port', default=8000, type=int),
    ) + BaseCommand.option_list
    def run(self, port, hostname, **kwargs):
        if port is None and 'LISTEN_PORT' in self.app.config:
            port = self.app.config['LISTEN_PORT']
        else:
            port = 8000

        if hostname is None and 'LISTEN_HOST' in self.app.config:
            hostname = self.app.config['LISTEN_HOST']
        else:
            hostname = '0.0.0.0'

        from meinheld import server, patch
        patch.patch_all()
        print(" - Running Hosting Server using Meinheld")
        print(" - http://%s:%s/" % (hostname, port))
        server.listen((hostname, port))
        server.run(self.app)


github_suffix = ''

def extract(f,dist='dist', destination='./'):
    # Destination is relative to app root.
    with zipfile.ZipFile(f, mode='r') as zf:
        zip_prefix = zf.namelist()[0]
        dist_folder =  os.path.join(zip_prefix, dist + "/" if dist != '' else dist)
        extractable = filter(lambda f: f.startswith(dist_folder) and not f.endswith('/'), zf.namelist())
        prefix = os.path.realpath(os.path.join('.', destination))

        for member in extractable:
            with zf.open(member, 'r') as m:
                output_name = os.path.join(prefix, member.replace(dist_folder, ''))
                if output_name.strip() != '':
                    output_directory = os.path.dirname(output_name)
                    if not os.path.exists(output_directory):
                        os.makedirs(output_directory)
                    with open(output_name, 'wb') as o:
                        d = m.read()
                        o.write(d)

class InstallFramework(BaseCommand):
    """
    Install a CSS/JS package listed on bower OR A 
    package from a github repository
    """
    option_list = (
        Option('packages', action='store', metavar='PACKAGE',nargs='+', help="A package listed on bower OR A github repository. (user/repo)."),
        Option('--version', '-v', dest='version', type=str, help="Supply a version to use (Github tag or release)"),
        Option('--with-link', '-l', dest='with_link', default=False, action='store_true', help="Automatically include this package in the WebApp's header (Experimental - Only includes minifies CSS/JS ending in .min.css)"),
    )
    def run(self, packages, version, with_link):
        root_folder = os.path.realpath('.')
        print(root_folder)
        git_package = re.compile(r'^([A-Za-z0-9\-_\.]+/[A-Za-z0-9_\-\.]+)$')
        bower_package = re.compile(r'^([A-Za-z0-9\._\-]+)$')


        for package in packages:

            github_resolved = None
            version = None

            if git_package.match(package):
                m = git_package.match(package)
                github_resolved = m.group(1)

            elif bower_package.match(package):
                m = bower_package.match(package)
                # Resolve this into a github package
                try:
                    data = urlopen("http://bower.herokuapp.com/packages/%s" % (package)).read()
                    data = json.loads(data.decode('UTF-8'))
                    # Get the github url
                    github_resolved = re.match(r'^git://github\.com/([A-Za-z0-9\._\-]+/[A-Za-z0-9\._\-]+)\.git$', data['url'])
                    if not github_resolved:
                        raise Exception('Unable to resolve github url: %s' % (data['url']))
                    github_resolved = github_resolved.group(1)

                except Exception as e:
                    print("Error loading package:")
                    print(e)
                    exit(1)

            else:
                print("Not a valid package name/formation")
                print("Please provide a package in the form of (<bower package>|<<github user>/<github repo>>)[#<tag name>]")
                exit(1)

            print("Found Package %s" % (github_resolved))

            package_name = github_resolved.replace('/', '-')

            try:
                data = urlopen("https://api.github.com/repos/%s/releases%s" % (github_resolved, github_suffix)).read()
                data = json.loads(data.decode('UTF-8'))
                if len(data) > 0:
                    found = False
                    active_release = None
                    if version:
                        for release in data:
                            if re.search(version, release['tag_name']):
                                active_release = release
                                break
                        if not found:
                            print("Could not find a release with that tag.")
                            exit(1)
                    else:
                        # Use the latest release
                        active_release = data[0]

                    response = urlopen(active_release['assets'][0]['browser_download_url'] + github_suffix)
                    zipcontent= response.read()
                    f = BytesIO()
                    f.write(zipcontent)
                    f.seek(0)

                    # Extract all because this is dist
                    extract(f, dist='', destination='./Application/static/vendor/%s/' % (package_name))

                else:
                    # We couldn't find a release. repo probably doesn't use github's release tags.
                    # Fallback to standard tags, use the standard zipball and find the dist folder

                    data = urlopen("https://api.github.com/repos/%s/tags%s" % (github_resolved, github_suffix)).read()
                    data = json.loads(data.decode('UTF-8'))
                    active_tag = None
                    if version:
                        for tag in data:
                            if version == tag['name']:
                                active_tag = tag
                                break
                    else:
                        active_tag = data[0]

                    if not active_tag:
                        print("Could not find a tag with the name: %s" % (version))
                        exit(1)

                    response = urlopen(active_tag['zipball_url'] + github_suffix)
                    zipcontent= response.read()

                    f = BytesIO()
                    f.write(zipcontent)
                    f.seek(0)


                    # Use the dist folder because thats where things /should/ be.
                    extract(f, dist='dist', destination='./Application/static/vendor/%s/' % (package_name))

                print("Installed: %s" % (package_name))

                if with_link:
                    print("Linking: %s" % (package_name))

                    # We need to link it up
                    scripts = []
                    stylesheets = []

                    def cleanname(name):
                        g = re.search(r'(/static/vendor/.*)', name).group(1)
                        return g

                    for dirname, dirnames, filenames in os.walk('./Application/static/vendor/%s/' % (package_name)):
                        for filename in filenames:
                            fullpath =  os.path.join(dirname, filename)
                            if "i18n" in fullpath:
                                continue

                            if re.search('\.min\.css$', filename):
                                stylesheets.append(cleanname(fullpath))
                            elif re.search("\.min\.js$", filename):
                                scripts.append(cleanname(fullpath))

                    f = './Application/static/vendor/'
                    f = os.path.join(f, 'autoinclude.json')

                    data = {'scripts':[], 'stylesheets':[]}

                    if os.path.isfile(f):
                        with open(f, 'r') as fh:
                            data = json.loads(fh.read())
                    
                    for script in scripts:
                        if not script in data['scripts']:
                            data['scripts'].append(script)
                            print(" - Linked: %s" % (script))

                    for stylesheet in stylesheets:
                        if not stylesheet in data['stylesheets']:
                            data['stylesheets'].append(stylesheet)
                            print(" - Linked: %s" % (stylesheet))


                    with open(f, 'w+') as fh:
                        fh.write(json.dumps(data))


            except Exception as e:
                print(e)
