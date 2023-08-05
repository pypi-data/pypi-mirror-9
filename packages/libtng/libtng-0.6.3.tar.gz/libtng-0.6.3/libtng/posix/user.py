import collections
import os
import pwd
import grp
import syslog
import platform

try:
    import spwd
    HAVE_SPWD=True
except:
    HAVE_SPWD=False

from libtng.posix.utils import run_command, get_bin_path
from libtng.exceptions import DuplicateResource


class UserAlreadyExists(DuplicateResource):
    """
    Raises when trying to create a user that already exists.
    """
    pass


class User(object):
    """
    This is a generic User manipulation class that is subclassed
    based on platform.

    A subclass may wish to override the following action methods:-
      - :meth:`User.create_user()`
      - :meth:`User.remove_user()`
      - :meth:`User.modify_user()`
      - :meth:`User.ssh_key_gen()`
      - :meth:`User.ssh_key_fingerprint()`
      - :meth:`User.user_exists()`

    All subclasses MUST define :attr:`User.platform` and
    :attr:`User.distribution` (which may be ``None``).
    """

    #: Specifies the platform :class:`User` can operate on.
    platform = 'Generic'

    #: Specifies the distribution :class:`User` can operate on.
    distribution = None
    SHADOWFILE = '/etc/shadow'

    # def __new__(cls, *args, **kwargs):
    #     return load_platform_subclass(User, args, kwargs)

    def __init__(self, name, **kwargs):
        """
        Manage user accounts and user attributes.

        :param name:
            Name of the user to create, remove or modify.
        :param comment:
            Optionally sets the description (aka I(GECOS)) of user account.
        :param uid:
            Optionally sets the I(UID) of the user.
        :param non_unique:
            default: "no"
            choices: [ "yes", "no" ]
            Optionally when used with the -u option, this option allows to
                  change the user ID to a non-unique value.
            version_added: "1.1"
        :param group:
            Optionally sets the user's primary group (takes a group name).
        :param groups:
            Puts the user in this comma-delimited list of groups. When set to
                  the empty string ('groups='), the user is removed from all groups
                  except the primary group.
        :param append:
            If C(yes), will only add groups, not set them to just the list
                  in I(groups).
        :param shell:
            Optionally set the user's shell.
        :param home:
            Optionally set the user's home directory.
        :param password:
            Optionally set the user's password to this crypted value.  See
            the user example in the github examples directory for what this looks
            like in a playbook. The `FAQ <http://docs.ansible.com/faq.html#how-do-i-generate-crypted-passwords-for-the-user-module>`_
            contains details on various ways to generate these password values.
        :param state:
            default: "present"
            choices: [ present, absent ]
            Whether the account should exist.  When C(absent), removes
                  the user account.
        :param createhome:
            default: "yes"
            choices: [ "yes", "no" ]
            Unless set to C(no), a home directory will be made for the user
                  when the account is created or if the home directory does not
                  exist.
        :param move_home:
            default: "no"
            choices: [ "yes", "no" ]
            If set to C(yes) when used with C(home=), attempt to move the
                  user's home directory to the specified directory if it isn't there
                  already.
        :param system:
            default: "no"
            choices: [ "yes", "no" ]
            When creating an account, setting this to C(yes) makes the user a
                  system account.  This setting cannot be changed on existing users.
        :param force:
            default: "no"
            choices: [ "yes", "no" ]
            When used with C(state=absent), behavior is as with
                  C(userdel --force).
        :param login_class:
            Optionally sets the user's login class for FreeBSD, OpenBSD and NetBSD systems.
        :param remove:
            default: "no"
            choices: [ "yes", "no" ]
            When used with C(state=absent), behavior is as with
                  C(userdel --remove).
        :param generate_ssh_key:
            default: "no"
            choices: [ "yes", "no" ]
            version_added: "0.9"
            Whether to generate a SSH key for the user in question.
                  This will B(not) overwrite an existing SSH key.
        :param ssh_key_bits:
            default: 2048
            version_added: "0.9"
            Optionally specify number of bits in SSH key to create.
        :param ssh_key_type:
            default: rsa
            version_added: "0.9"
            Optionally specify the type of SSH key to generate.
                  Available SSH key types will depend on implementation
                  present on target host.
        :param ssh_key_file:
            default: $HOME/.ssh/id_rsa
            version_added: "0.9"
            Optionally specify the SSH key filename.
        :param ssh_key_comment:
            default: ansible-generated
            version_added: "0.9"
            Optionally define the comment for the SSH key.
        :param ssh_key_passphrase:
            version_added: "0.9"
            Set a passphrase for the SSH key.  If no
                  passphrase is provided, the SSH key will default to
                  having no passphrase.
        :param update_password:
            default: always
            choices: ['always', 'on_create']
            version_added: "1.3"
            C(always) will update passwords if they differ.  C(on_create) will only set the password for newly created users.
        """
        kwargs = collections.defaultdict(lambda: None, kwargs)
        self.state      = kwargs['state']
        self.name       = name
        self.uid        = kwargs['uid']
        self.non_unique  = kwargs['non_unique']
        self.group      = kwargs['group']
        self.groups     = kwargs['groups']
        self.comment    = kwargs['comment']
        self.home       = kwargs['home']
        self.shell      = kwargs['shell']
        self.password   = kwargs['password']
        self.force      = kwargs['force']
        self.remove     = kwargs['remove']
        self.createhome = kwargs['createhome']
        self.move_home  = kwargs['move_home']
        self.system     = kwargs['system']
        self.login_class = kwargs['login_class']
        self.append     = kwargs['append']
        self.sshkeygen  = kwargs['generate_ssh_key']
        self.ssh_bits   = kwargs['ssh_key_bits']
        self.ssh_type   = kwargs['ssh_key_type']
        self.ssh_comment = kwargs['ssh_key_comment']
        self.ssh_passphrase = kwargs['ssh_key_passphrase']
        self.update_password = kwargs['update_password']
        if kwargs['ssh_key_file'] is not None:
            self.ssh_file = kwargs['ssh_key_file']
        else:
            self.ssh_file = os.path.join('.ssh', 'id_%s' % self.ssh_type)

        # select whether we dump additional debug info through syslog
        self.syslogging = False

    def execute_command(self, cmd):
        if self.syslogging:
            syslog.openlog('libtouchngo-%s' % os.path.basename(__file__))
            syslog.syslog(syslog.LOG_NOTICE, 'Command %s' % '|'.join(cmd))

        return run_command(cmd)

    def remove(self, force=False, remove=False):
        """
        Removes a user from the local machine.

        :param force:
            Force removal of files even if not owned by user.
        :type force: :class:`boolean`
        :param remove:
            Remove home directory and mail spool
        :type remove: :class:`boolean`
        """
        cmd = [self.module.get_bin_path('userdel', True)]
        if force:
            cmd.append('-f')
        if remove:
            cmd.append('-r')
        cmd.append(self.name)
        self.execute_command(cmd)

    def exists(self):
        """
        Return a bool indicating if the :class:`User` exists.
        """
        try:
            if pwd.getpwnam(self.name):
                return True
        except KeyError:
            return False

    def create(self, command_name='useradd'):
        """
        Creates the user.
        """
        cmd = [get_bin_path(command_name)]

        if self.uid is not None:
            cmd.append('-u')
            cmd.append(self.uid)

            if self.non_unique:
                cmd.append('-o')

        if self.group is not None:
            if not self.group_exists(self.group):
                msg="Group {0} does not exist".format(self.group)
            cmd.append('-g')
            cmd.append(self.group)
        elif group_exists(self.name):
            # use the -N option (no user group) if a group already
            # exists with the same name as the user to prevent
            # errors from useradd trying to create a group when
            # USERGROUPS_ENAB is set in /etc/login.defs.
            cmd.append('-N')

        if self.groups is not None and len(self.groups):
            groups = self.get_groups_set()
            cmd.append('-G')
            cmd.append(','.join(groups))

        if self.comment is not None:
            cmd.append('-c')
            cmd.append(self.comment)

        if self.home is not None:
            cmd.append('-d')
            cmd.append(self.home)

        if self.shell is not None:
            cmd.append('-s')
            cmd.append(self.shell)

        if self.password is not None:
            cmd.append('-p')
            cmd.append(self.password)

        if self.createhome:
            cmd.append('-m')
        else:
            cmd.append('-M')

        if self.system:
            cmd.append('-r')

        cmd.append(self.name)
        return self.execute_command(cmd)



def group_exists(name):
    try:
        if name.isdigit():
            if grp.getgrgid(name):
                return True
        else:
            if grp.getgrnam(name):
                return True
    except KeyError:
        return False



def get_user_key():
    return os.path.expanduser('~/.ssh/id_rsa')