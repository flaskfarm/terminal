from support import SupportYaml

from .setup import *

name = 'setting'

class ModuleSetting(PluginModuleBase):
    def __init__(self, P):
        super(ModuleSetting, self).__init__(P, name=name)
        self.yaml_path = os.path.join(F.config['path_data'], 'db', 'terminal.yaml')
        self.current_info = None

    def process_menu(self, page, req):
        arg = {'yaml_path': self.yaml_path}
        return render_template(f'{P.package_name}_{name}.html', arg=arg)

    def process_command(self, command, arg1, arg2, arg3, req):
        try:
            if command == 'get_info':
                return jsonify(self.get_info())
            elif command == 'run':
                #data = self.get_info()
                ins = P.logic.get_module('terminal')
                ins.wait_input(self.current_info[int(arg1)]['command'])
                return jsonify({'ret':'success'})
        except Exception as e: 
            P.logger.error(f'Exception: {str(e)}')
            P.logger.error(traceback.format_exc())


    def get_info(self):
        if os.path.exists(self.yaml_path) == False:
            with open(self.yaml_path, 'w', encoding='utf8') as f:
                f.write(yaml_templete)
        self.current_info = SupportYaml.read_yaml(self.yaml_path)
        return self.current_info


yaml_templete = '''
- title: 데이터 폴더별 크기 확인
  command: |
    cd /data
    du -h -d 1

- title: 메모리 사용량
  command: |
    top 

- title: 도커 재시작
  command: |
    ssh -i MY.pem ubuntu@172.17.0.1
    sudo docker restart flaskfarm

- title: PLEX 재시작
  command: |
    ssh -i MY.pem ubuntu@172.17.0.1
    sudo service plexmediaserver restart

- title: NGINX 재시작
  command: |
    nginx -s reload
'''
