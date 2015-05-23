import sys
import json
import subprocess

def processShell(command,isShell=True):
        print "executing command",command
        output = None
        status = True
        try:
                output = subprocess.check_output(command,shell=isShell)
        except subprocess.CalledProcessError, e:
                print "Exception:\n", e.output
                status = False
        print "__________________________________________________________________________________________________________________"
        print output
        print "__________________________________________________________________________________________________________________"
        return output,status

print "Check if Docker installed"
if processShell('which docker')[1] is False:
        print "installing docker"
        if processShell('sudo apt-get update ')[1] and processShell('sudo wget -qO- https://get.docker.com/ | sh ')[1]:
                        print 'Docker Installed'
        else:
                print 'Docker install Failed'
                sys.exit('Docker install Failed')
print "Check if docker-compose is installed"
if processShell('which docker-compose')[1] is False:
        print "intalling docker-compose"
        if processShell('sudo curl -L https://github.com/docker/compose/releases/download/1.2.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose')[1] and processShell('sudo chmod +x /usr/local/bin/docker-compose')[1]:
                        print 'Docker compose Installed'
        else:
                print 'Docker compose install Failed'
                sys.exit('Docker-compose install Failed')

print "Install Rancher server"
if processShell('docker run -d --restart=always -p 8080:8080 rancher/server')[1] is False:
        print 'Docker Rancher install Failed'
        sys.exit('Docker Rancher install Failed')

print "Dont kknow why we need this"
processShell("sleep 100")
containerID,status =processShell(" docker ps | grep 'rancher\/server' | awk -F' ' '{print $1}'")
containerID = containerID.rstrip('\n')
if status:
         processShell('docker exec -t '+containerID+ " curl http://localhost:8080")

print "Make a Dummy curl request"
processShell('curl -XPOST "http://localhost:8080/v1/registrationtoken" -H "authorization: None" -H "X-Requested-With: XMLHttpRequest" -H "Connection: keep-alive" -H "x-api-project-id: 1a5" -H "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36" -H "Content-Type: application/json" -H "x-api-no-challenge: true" -H "Accept: application/json"' + "--data " + "'{" + '"type":"registrationToken","state":null,"transitioning":null,"transitioningMessage":null,"transitioningProgress":null,"id":null,"headers":null}' + "' --compressed")
print "Install rancher cattle client"
result,status = processShell('curl "http://localhost:8080/v1/registrationtokens" -H "authorization: None" -H "x-api-project-id: 1a5" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: en-US,en;q=0.8" --compressed')

print type(result)
result = str(result).strip('\n')
if status:
        curlOut = json.loads(result)
        print "##################################################################"
        cmd = curlOut['data'][0]['command']
        if processShell(cmd)[1] is False:
                print 'cattle agent failed to install'
        else:
                print 'Docker Rancher cattle installed'

print "Launching ELK"
if processShell('docker-compose -f elk.yml up -d')[1] is False:
        print 'ELK failed to start in containers'
        sys.exit('Docker elk install Failed')


