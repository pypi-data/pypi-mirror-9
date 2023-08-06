__all__ = ['ClassContextManager']


class ClassContextManager(object):
    class __metaclass__(type):
        def __get__(self, instance, owner):
            self.parent = instance
            return self

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        self.enter(*self.args, **self.kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit(*self.args, **self.kwargs)

    def enter(self, *args, **kwargs):
        pass

    def exit(self, *args, **kwargs):
        pass


if __name__ == "__main__":
    class Git(object):
        def do_something(self, new_branch):
            print "Do Something with", new_branch

        class with_branch(ClassContextManager):
            def enter(self, branch_name):
                print "Create", branch_name
                self.parent.do_something(branch_name)

            def exit(self, branch_name):
                print "Delete", branch_name


    git = Git()
    with git.with_branch('origin/master'):
        print "Do Work in Branch"
