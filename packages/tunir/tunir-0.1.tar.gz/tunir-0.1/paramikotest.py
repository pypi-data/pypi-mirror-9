import paramiko
from tunirlib.tunirdocker import Result

def execute_shell(host='127.0.0.1', port=22, user='root',
                  password='passw0rd', command='/bin/true', bufsize=-1):
    """
    Excecutes a command using paramiko and returns the result.
    :param host: Host to connect
    :param port: The port number
    :param user: The username of the system
    :param password: User password
    :param command: The command to run
    :return:
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port,
                   username=user, password=password)
    chan = client.get_transport().open_session()
    chan.settimeout(None)
    chan.exec_command(command)
    stdout = chan.makefile('r', bufsize)
    stderr = chan.makefile_stderr('r', bufsize)
    stdout_text = stdout.read()
    stderr_text = stderr.read()
    out = Result(stdout_text)
    err = Result(stderr_text)
    status = int(chan.recv_exit_status())
    client.close()
    out.return_code = status
    out.errmsg = err
    return out


if __name__ == '__main__':
    print execute_shell(command='/usr/bin/ls /', user='kdas', password='asjnam;')
