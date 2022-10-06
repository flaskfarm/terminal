import traceback, threading, time
import os
import platform
import pty
import subprocess
import base64
import select
import struct
import fcntl
import termios

from .setup import *

class ModuleTerminal(PluginModuleBase):
    pty_list = {}
    sid_list = []


    def __init__(self, P):
        super(ModuleTerminal, self).__init__(P)
        self.route()

    def route(self):
        @P.blueprint.route('/')
        @login_required
        def home():
            arg = {'package_name': P.package_name}
            return render_template(f'{P.package_name}_terminal.html', arg=arg)

        
        # 터미널 실행
        @login_required
        @F.socketio.on('connect', namespace=f'/{P.package_name}')
        def connect():
            try:
                cmd = 'bash' if platform.system() != 'Windows' else 'cmd.exe'
                (master, slave) = pty.openpty()  # 터미널 생성
                popen = subprocess.Popen(
                    cmd, stdin=slave, stdout=slave, stderr=slave, start_new_session=True)  # 셸 실행
                P.logger.debug('cmd: %s, child pid: %s', cmd, popen.pid)
                self.pty_list[request.sid] = {
                    'popen': popen, 'master': master, 'slave': slave}
                self.sid_list.append(request.sid)
                F.socketio.start_background_task(
                    self.output_emit, master, request.sid)
            except Exception as e:
                P.logger.error('Exception:%s', e)
                P.logger.error(traceback.format_exc())

        # 터미널 종료
        @F.socketio.on('disconnect', namespace=f'/{P.package_name}')
        def disconnect():
            try:
                P.logger.debug('socketio: /%s, disconnect, %s', P.package_name, request.sid)
                popen = ModuleTerminal.pty_list[request.sid]['popen']
                if popen.poll():
                    popen.kill()
                os.close(ModuleTerminal.pty_list[request.sid]['master'])
                os.close(ModuleTerminal.pty_list[request.sid]['slave'])
                del ModuleTerminal.pty_list[request.sid]
            except Exception as e:
                P.logger.error('Exception:%s', e)
                P.logger.error(traceback.format_exc())

        # 커맨드 입력
        @F.socketio.on('input', namespace=f'/{P.package_name}')
        def input(data):
            try:
                #logger.debug('socketio: /%s/%s, input, %s, %s', package_name, name, request.sid, data)
                fd = self.pty_list[request.sid]['master']
                os.write(fd, base64.b64decode(data))
            except Exception as e:
                P.logger.error('Exception:%s', e)
                P.logger.error(traceback.format_exc())

        # 크기조절
        @F.socketio.on('resize', namespace=f'/{P.package_name}')
        def resize(data):
            try:
                P.logger.debug('socketio: /%s, resize, %s, %s',
                            P.package_name, request.sid, data)
                fd = self.pty_list[request.sid]['master']
                self.set_winsize(fd, data['rows'], data['cols'])
            except Exception as e:
                P.logger.error('Exception:%s', e)
                P.logger.error(traceback.format_exc())

    # 출력 전송
    def output_emit(self, fd, room):
        try:
            max_read_bytes = 1024 * 20
            while True:
                F.socketio.sleep(0.01)
                if select.select([fd], [], [], 0)[0]:
                    output = os.read(fd, max_read_bytes).decode()
                    F.socketio.emit(
                        'output', output, namespace=f'/{P.package_name}', room=room)
        except OSError as e:    # 터미널 종료
            pass
        except Exception as e:
            P.logger.error('Exception:%s', e)
            P.logger.error(traceback.format_exc())

    # 터미널 사이즈 설정
    def set_winsize(self, fd, row, col, xpix=0, ypix=0):
        winsize = struct.pack('HHHH', row, col, xpix, ypix)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


    def plugin_unload(self):
        for key, value in ModuleTerminal.pty_list.items():
            try:
                popen = value['popen']
                if popen.poll():
                    popen.kill()
                os.close(value['master'])
                os.close(value['slave'])
            except Exception as e:
                P.logger.error('Exception:%s', e)
                P.logger.error(traceback.format_exc())
    

    def wait_input(self, command):
        def func(command):
            current = len(ModuleTerminal.sid_list)
            while True:
                if len(ModuleTerminal.sid_list) != current:
                    break
                time.sleep(0.1)
            fd = ModuleTerminal.pty_list[ModuleTerminal.sid_list[-1]]['master']
            command += "\n"
            os.write(fd, command.encode('utf8'))
        
        t = threading.Thread(target=func, args=(command,))
        t.setDaemon(True)
        t.start()
