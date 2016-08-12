#!/usr/bin/python

# import system libraries
import sys, getopt, commands, os, time

def main(argv):
    container = False
    getoptComunicate = sys.argv[0] + " -h -c <container>"
    try:
        opts, args = getopt.getopt(argv,"hc:",["container="])
    except getopt.GetoptError:
        print getoptComunicate
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print getoptComunicate
            sys.exit()
        elif opt in ("-c", "--container"):
            container = arg
    if not container:
        print getoptComunicate
        sys.exit()
    return {
        'container': container
    }

args = {}
if __name__ == "__main__":
    args = main(sys.argv[1:])

DOCKER_COMPOSE_FILE = 'docker-compose.override.yml'
DOCKER_COMPOSE_TMP_FILE = 'docker-compose.override.yml.tmp'
QA_PREFIX = 'qa'

qaName = QA_PREFIX + '-' + args['container']

while(1):
    if os.path.isfile('/docker/' + DOCKER_COMPOSE_TMP_FILE):
        print DOCKER_COMPOSE_TMP_FILE + " exist, waiting 5 seconds ..."
        time.sleep(5)
    else:
        commands.getoutput('touch /docker/' + DOCKER_COMPOSE_FILE)
        print DOCKER_COMPOSE_TMP_FILE + " not exist"
        break

fout = open('/docker/' + DOCKER_COMPOSE_TMP_FILE, 'w')

clearLine = False
lines = 0
with open('/docker/' + DOCKER_COMPOSE_FILE, 'r') as fin:
    for line in fin:
        if (clearLine == True) and (line == '\n'):
            clearLine = False
            continue
        elif clearLine == True:
            continue
        elif ('- ' + qaName) in line:
            continue
        elif qaName in line:
            clearLine = True
            continue
        else:
            fout.write(line)
            lines += 1

fout.close()

if lines < 4:
    commands.getoutput("rm /docker/" + DOCKER_COMPOSE_FILE)
else:
    commands.getoutput("cp /docker/" + DOCKER_COMPOSE_TMP_FILE + " /docker/" + DOCKER_COMPOSE_FILE)

commands.getoutput("cd /docker && sudo docker-compose kill " + args['container'])
commands.getoutput("rm /docker/nginx/local/" + qaName + ".conf")
print commands.getoutput("cd /docker && sudo docker-compose up -d")

commands.getoutput("sudo docker kill $(docker ps | grep " + args['container'] + " | awk '{print $1}')")
commands.getoutput("sudo docker rm $(docker ps -a | grep " + args['container'] + " | awk '{print $1}')")
commands.getoutput("sudo docker rmi -f $(docker images | grep " + args['container'] + " | awk '{print $3}')")

commands.getoutput("rm -rf /srv/www/" + qaName)
commands.getoutput("rm -rf /srv/dbs/" + qaName)
commands.getoutput("sudo docker rmi $(docker images -q -f dangling=true)")

commands.getoutput("rm /docker/" + DOCKER_COMPOSE_TMP_FILE)
