import os
import sh


# noinspection PyUnresolvedReferences
class Shell(object):

    #    @classmethod
    #    def ls(cls, arguments=None):
    #        return cls._execute(sh.ls, arguments)

    @classmethod
    def _execute(cls, f, *args, **kwargs):
        """
        internal method to execute a command with args and kwargs and passed to an sh command
        :param cls: the classmethod
        :param f: the function to be executed
        """
        args = args or []
        kws = kwargs or {}
        return f(*args, **kws)
#        args = list(*arguments)
#        if len(args) == 0:
#            return f().rstrip('\n')
#       else:
#           return f(args).rstrip('\n')

    @classmethod
    def cat(cls, *args, **kwargs):
        """
        the cat command
        :param cls:
        """
        return cls._execute(sh.cat, *args, **kwargs)

    @classmethod
    def git(cls, *args, **kwargs):
        """
        the git command
        :param cls:
        """
        return cls._execute(sh.git, *args, **kwargs)
        
    @classmethod
    def VBoxManage(cls, *args, **kwargs):
        """
        the virtualbox management command
        :param cls:
        """
        return cls._execute(sh.VBoxManage, *args, **kwargs)

    @classmethod
    def blockdiag(cls, *args, **kwargs):
        """
        the blockdiag command
        :param cls:
        """
        return cls._execute(sh.blockdiag	, *args, **kwargs)
    
    @classmethod
    def cm(cls, *args, **kwargs):
        """
        the cloudmesh command
        :param cls:
        """
        return cls._execute(sh.cm, *args, **kwargs)
        
    @classmethod
    def fgmetric(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.fgmetric, *args, **kwargs)
        
    @classmethod
    def fgrep(cls, *args, **kwargs):
        """
        the fgrep command
        :param cls:
        """
        return cls._execute(sh.fgrep, *args, **kwargs)
            
    @classmethod
    def gchproject(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.gchproject, *args, **kwargs)
            
    @classmethod
    def gchuser(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.gchuser, *args, **kwargs)
                
    @classmethod
    def glusers(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.glusers, *args, **kwargs)
                    
    @classmethod
    def gmkproject(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.gmkproject, *args, **kwargs)
                    
    @classmethod
    def grep(cls, *args, **kwargs):
        """
        the grep command
        :param cls:
        """
        return cls._execute(sh.grep, *args, **kwargs)
                        
    @classmethod
    def gstatement(cls, *args, **kwargs):
        """
        TODO: document
        :param cls:
        """
        return cls._execute(sh.gstatement, *args, **kwargs)
                        
    @classmethod
    def head(cls, *args, **kwargs):
        """
        the head command
        :param cls:
        """
        return cls._execute(sh.head, *args, **kwargs)
                            
    @classmethod
    def keystone(cls, *args, **kwargs):
        """
        the OpenStack keystone command
        :param cls:
        """
        return cls._execute(sh.keystone, *args, **kwargs)
                            
    @classmethod
    def kill(cls, *args, **kwargs):
        """
        the kill command
        :param cls:
        """
        return cls._execute(sh.kill, *args, **kwargs)

    @classmethod
    def ls(cls, *args, **kwargs):
        """
        the ls command
        :param cls:
        """
        return cls._execute(sh.ls, *args, **kwargs)
                                        
    @classmethod
    def mkdir(cls, newdir):
        """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
        """
        """http://code.activestate.com/recipes/82465-a-friendly-mkdir/"""
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired "
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                os.mkdir(head)
            if tail:
                os.mkdir(newdir)

    @classmethod
    def mongoimport(cls, *args, **kwargs):
        """
        the mongoimport command
        :param cls:
        """
        return cls._execute(sh.mongoimport, *args, **kwargs)
                                    
    @classmethod
    def mysql(cls, *args, **kwargs):
        """
        the mysql command
        :param cls:
        """
        return cls._execute(sh.mysql, *args, **kwargs)
                                        
    @classmethod
    def nosetests(cls, *args, **kwargs):
        """
        the nosetest command
        :param cls:
        """
        return cls._execute(sh.nosetests, *args, **kwargs)
                                        
    @classmethod
    def nova(cls, *args, **kwargs):
        """
        the nova command
        :param cls:
        """
        return cls._execute(sh.nova, *args, **kwargs)
                                            
    @classmethod
    def ping(cls, *args, **kwargs):
        """
        the ping command
        :param cls:
        """
        return cls._execute(sh.ping, *args, **kwargs)
                                            
    @classmethod
    def pwd(cls, *args, **kwargs):
        """
        the pwd command
        :param cls:
        """
        return cls._execute(sh.pwd, *args, **kwargs)
                                            
    @classmethod
    def rackdiag(cls, *args, **kwargs):
        """
        the rackdiag command
        :param cls:
        """
        return cls._execute(sh.rackdiag, *args, **kwargs)
                                                
    @classmethod
    def rm(cls, *args, **kwargs):
        """
        the rm command
        :param cls:
        """
        return cls._execute(sh.rm, *args, **kwargs)
                                                
    @classmethod
    def rsync(cls, *args, **kwargs):
        """
        the rsync command
        :param cls:
        """
        return cls._execute(sh.rsync, *args, **kwargs)
                                                    
    @classmethod
    def scp(cls, *args, **kwargs):
        """
        the scp command
        :param cls:
        """
        return cls._execute(sh.scp, *args, **kwargs)
                                                    
    @classmethod
    def sort(cls, *args, **kwargs):
        """
        the sort command
        :param cls:
        """
        return cls._execute(sh.sort, *args, **kwargs)
                                                        
    @classmethod
    def ssh(cls, *args, **kwargs):
        """
        the ssh command
        :param cls:
        """
        return cls._execute(sh.ssh, *args, **kwargs)
                                                        
    @classmethod
    def sudo(cls, *args, **kwargs):
        """
        the sudo command
        :param cls:
        """
        return cls._execute(sh.sudo, *args, **kwargs)
                                                            
    @classmethod
    def tail(cls, *args, **kwargs):
        """
        the tail command
        :param cls:
        """
        return cls._execute(sh.tail, *args, **kwargs)
                                                            
    @classmethod
    def vagrant(cls, *args, **kwargs):
        """
        the vargant command
        :param cls:
        """
        return cls._execute(sh.vagrant, *args, **kwargs)  
        
    @classmethod
    def mongod(cls, *args, **kwargs):
        """
        the mongod command
        :param cls:
        """
        return cls._execute(sh.mongod, *args, **kwargs)
    
    @classmethod
    def which(cls, *args, **kwargs):
        """
        the which command
        :param cls:
        """
        try:
            path = cls._execute(sh.which, *args, **kwargs)
        except:
            path = None
        return path
    
    @classmethod
    def grep(cls, *args, **kwargs):
        """
        the grep command
        :param cls:
        """
        try:
            path = cls._execute(sh.grep, *args, **kwargs)
        except:
            path = None
        return path
    
                                                                    
if __name__ == "__main__":
    print Shell.ls("-1")
    print Shell.ls()
    print Shell.ls("-A", "-G")    

    print Shell.pwd()

