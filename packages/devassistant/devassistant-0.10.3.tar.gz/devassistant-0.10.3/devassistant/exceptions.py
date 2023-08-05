class ExecutionException(BaseException):
    pass


class DependencyException(ExecutionException):
    pass


class RunException(ExecutionException):
    pass


class ClException(RunException):
    def __init__(self, command, returncode, output):
        self.command = command
        self.returncode = returncode
        self.output = output
        self.message = output.splitlines()[-1] if output else ""

    def __str__(self):
        return self.output


class CommandException(RunException):
    pass


class YamlError(ExecutionException):
    pass


class YamlTypeError(YamlError):
    pass


class YamlSyntaxError(YamlError):
    pass


class AssistantNotFoundException(ExecutionException):
    pass


class SnippetNotFoundException(ExecutionException):
    pass


class NoPackageManagerOperationalException(DependencyException):
    """
    Should be thrown when no package manager for given dependency type works.
    """
    pass


class NoPackageManagerException(DependencyException):
    """
    No manager exists for a type of dependency.
    """
    pass


class DapError(ExecutionException):
    """
    Mother of all dap related exceptions
    """
    pass


class DapFileError(DapError):
    """
    Exception that indicates something wrong with dap file
    """
    pass


class DapMetaError(DapError):
    """
    Exception that indicates something wrong with dap's metadata
    """
    pass


class DapInvalid(DapError):
    """
    Exception that indicates invalid dap
    """
    pass
