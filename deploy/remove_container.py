#!/usr/bin/python

# import system libraries
import sys, getopt, commands

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

# @todo check exist docker-compose.override.yml.tmp, if exist sleeping
fout = open('/docker/' + DOCKER_COMPOSE_TMP_FILE, 'w+')

clearLine = False
with open('/docker/' + DOCKER_COMPOSE_FILE, 'r') as fin:
    for line in fin:
        if (clearLine == True) and (line == '\n'):
            clearLine = False
            continue
        elif clearLine == True:
            continue
        elif args['container'] in line:
            clearLine = True
            continue
        else:
            fout.write(line)

fout.close()

commands.getoutput("cp /docker/" + DOCKER_COMPOSE_TMP_FILE + " /docker/" + DOCKER_COMPOSE_FILE)

print commands.getoutput("cd /docker && sudo docker-compose kill " + args['container'])
print commands.getoutput("sudo docker rm $(docker ps | grep " + args['container'] + " | awk '{print $1}')")
print commands.getoutput("sudo docker rmi $(docker images | grep " + args['container'] + " | awk '{print $3}')")
print commands.getoutput("rm -rf /srv/www/" + args['container'])
print commands.getoutput("rm /docker/nginx/local/" + args['container'] + ".conf")

print commands.getoutput("cd /docker && sudo docker-compose up -d")

commands.getoutput("rm /docker/" + DOCKER_COMPOSE_TMP_FILE)
