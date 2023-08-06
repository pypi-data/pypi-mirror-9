#!/bin/bash -ux

here=$(readlink -f $(dirname $0))

jenkins_war_url=${JENKINS_WAR_URL:-"http://mirrors.jenkins-ci.org/war/latest/jenkins.war"}
jenkins_version='release'

jenkins_home=${JENKINS_HOME:-"${here}/../tmp/${jenkins_version}/jenkins"}
jenkins_port=${JENKINS_PORT:-"60888"}
jenkins_cport=${JENKINS_CPORT:-"60887"}
jenkins_addr=${JENKINS_ADDR:-"127.0.0.1"}

jenkins_war="${here}/../tmp/${jenkins_version}/jenkins.war"
jenkins_cli="${here}/../tmp/${jenkins_version}/jenkins-cli.jar"

function shutdown () {
    echo 0 | nc $jenkins_addr $jenkins_cport
}

if [[ ! -e $jenkins_war ]]; then
    echo "Downloading jenkins.war ..."
    curl -L $jenkins_war_url > $jenkins_war
fi

if [[ ! -e $jenkins_cli ]]; then
    echo "Extracting jenkins-cli.jar ..."
    unzip -qqc $jenkins_war WEB-INF/jenkins-cli.jar > $jenkins_cli
fi

trap shutdown SIGINT SIGTERM

echo "Starting jenkins on ${jenkins_addr}:${jenkins_port} ..."
java -DJENKINS_HOME=${jenkins_home} -jar ${jenkins_war} \
     --httpListenAddress=${jenkins_addr} \
     --httpPort=${jenkins_port} \
     --controlPort=${jenkins_cport} &

java_pid=$!
jenkins_running=1

echo "Waiting for jenkins to start ..."
for i in `seq 10`; do
    if curl --retry 5 -s ${jenkins_addr}:${jenkins_port} &>/dev/null; then
        jenkins_running=0
        break
    fi
    sleep 2
done

[[ $jenkins_running -ne 0 ]] && exit 1

wait $java_pid
