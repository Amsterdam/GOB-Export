#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node('GOBBUILD') {
    withEnv(["DOCKER_IMAGE_NAME=datapunt/gob_export:${env.BUILD_NUMBER}"]) {

        stage("Checkout") {
            checkout scm
        }

        stage('Test') {
            lock("gob-export-test") {
                tryStep "test", {
                    sh "docker-compose -p gob_export_service -f src/.jenkins/test/docker-compose.yml build --no-cache && " +
                    "docker-compose -p gob_export_service -f src/.jenkins/test/docker-compose.yml run --rm test"
                }, {
                    sh "docker-compose -p gob_export_service -f src/.jenkins/test/docker-compose.yml down"
                }
            }
        }

        stage("Build image") {
            tryStep "build", {
                docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                    def image = docker.build("${DOCKER_IMAGE_NAME}",
                        "--no-cache " +
                        "--shm-size 1G " +
                        "--build-arg BUILD_ENV=acc " +
                        "--target application " +
                        " src")
                    image.push()
                }
            }
        }

        String BRANCH = "${env.BRANCH_NAME}"

        if (BRANCH == "master") {

            stage('Push acceptance image') {
                tryStep "image tagging", {
                    docker.withRegistry("${DOCKER_REGISTRY_HOST}",'docker_registry_auth') {
                        def image = docker.image("${DOCKER_IMAGE_NAME}")
                        image.pull()
                        image.push("acceptance")
                    }
                }
            }

            stage("Deploy to ACC") {
                tryStep "deployment", {
                    build job: 'Subtask_Openstack_Playbook',
                        parameters: [
                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy.yml'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOKPARAMS', value: "-e cmdb_id=app_gob-export"],
                        ]
                }
            }
        }
    }
}
