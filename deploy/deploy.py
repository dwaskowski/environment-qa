#!/usr/bin/python

# import system libraries
import md5, random, commands, sys, getopt, os, time

def main(argv):
    build = 'php5.6'
    name = False
    getoptComunicate = sys.argv[0] + " -h [-n <name>] [-b <build>]"
    try:
        opts, args = getopt.getopt(argv,"hn:b:",["name=", "build="])
    except getopt.GetoptError:
        print getoptComunicate
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print getoptComunicate
            sys.exit()
        elif opt in ("-b", "--build"):
            build = arg
        elif opt in ("-n", "--name"):
            name = arg
    return {
        'build': build,
        'name': name
    }

args = {}
if __name__ == "__main__":
    args = main(sys.argv[1:])

# settings
DOCKER_COMPOSE_FILE = 'docker-compose.override.yml'
DOCKER_COMPOSE_TMP_FILE = 'docker-compose.override.yml.tmp'
QA_PREFIX = 'qa'

while(1):
    if os.path.isfile('/docker/' + DOCKER_COMPOSE_TMP_FILE):
        print DOCKER_COMPOSE_TMP_FILE + " exist, waiting 5 seconds ..."
        time.sleep(5)
    else:
        commands.getoutput('touch /docker/' + DOCKER_COMPOSE_FILE)
        print DOCKER_COMPOSE_TMP_FILE + " not exist"
        break

if args['name']:
    qaName = QA_PREFIX + '-' + args['name']
else:
    randomHex = md5.new(str(random.randint(0, 10000))).hexdigest()
    qaName = QA_PREFIX + '-' + randomHex[0:10]

nginxConfig = '/docker/nginx/local/' + qaName + '.conf'
commands.getoutput("mkdir /srv/www/" + qaName)
commands.getoutput("cp -R /srv/dbs/global /srv/dbs/" + qaName)

# @todo deploy stuff

fout = open('/docker/' + DOCKER_COMPOSE_TMP_FILE, 'w+')

nginxSet = nginxSetLink = False
with open('/docker/' + DOCKER_COMPOSE_FILE, 'r') as fin:
    for line in fin:
        fout.write(line)
        if 'nginx:' in  line:
            nginxSet = True
        if (nginxSet == True) and ('links:' in line) and (nginxSetLink == False):
            fout.write('    - ' + qaName + '\n')
            nginxSetLink = True

if nginxSet==False:
    fout.write('nginx:\n')
    fout.write('  links:\n')
    fout.write('    - ' + qaName + '\n')
    fout.write('\n')

fout.write(qaName + ':\n')
fout.write('  build: ./' + args['build'] + '\n')
fout.write('  command: php -S 0.0.0.0:8000 -t /web\n')
fout.write('  links:\n')
fout.write('    - db-' + qaName + ':localhost\n')
fout.write('  volumes:\n')
fout.write('    - /srv/www/' + qaName + ':/web\n')
fout.write('  restart: always\n')
fout.write('\n')
fout.write('db-' + qaName + ':\n')
fout.write('  build: ./mysql5.7\n')
fout.write('  ports:\n')
fout.write('    - "3306:3306"\n')
fout.write('  volumes:\n')
fout.write('    - /srv/dbs/' + qaName + ':/var/lib/mysql\n')
fout.write('  environment:\n')
fout.write('    MYSQL_ROOT_PASSWORD: xBXHyS5br5D45by6A5b3eKVz6\n')
#fout.write('    MYSQL_ALLOW_EMPTY_PASSWORD: yes\n')
fout.write('\n')
fout.close()

fout = open(nginxConfig, 'w+')
fout.write('\n')
fout.write('server {\n')
fout.write('\n')
fout.write('    listen 80;\n')
fout.write('    server_name ' + qaName + '.arilo.qa;\n')
fout.write('\n')
fout.write('    location / {\n')
fout.write('        proxy_pass http://' + qaName + ':8000;\n')
fout.write('        proxy_set_header Host $host;\n')
fout.write('        proxy_set_header X-Real-IP $remote_addr;\n')
fout.write('        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n')
fout.write('    }\n')
fout.write('\n')
fout.write('    access_log /var/log/nginx/' + qaName + '.access.log;\n')
fout.write('    error_log /var/log/nginx/' + qaName + '.error.log;\n')
fout.write('\n')
fout.write('}\n')
fout.write('\n')
fout.close()

commands.getoutput("cp /docker/" + DOCKER_COMPOSE_TMP_FILE + " /docker/" + DOCKER_COMPOSE_FILE)

print commands.getoutput("cd /docker && sudo docker-compose build")
print commands.getoutput("cd /docker && sudo docker-compose up -d")

commands.getoutput("rm /docker/" + DOCKER_COMPOSE_TMP_FILE)
