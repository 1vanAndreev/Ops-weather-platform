pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'], description: 'Target environment')
        booleanParam(name: 'RUN_DEPLOY', defaultValue: false, description: 'Run manual deployment stage')
    }

    environment {
        IMAGE_NAME = 'ops-weather-platform'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('lint') {
            steps {
                sh 'python3 -m pip install -r requirements-dev.txt'
                sh 'python3 -m ruff check app tests'
            }
        }

        stage('test') {
            steps {
                sh 'python3 -m pytest -q'
            }
        }

        stage('build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('deploy') {
            when {
                allOf {
                    expression { params.RUN_DEPLOY == true }
                    anyOf {
                        branch 'main'
                        branch 'master'
                    }
                }
            }
            steps {
                input message: "Deploy ${IMAGE_NAME}:${IMAGE_TAG} to ${params.DEPLOY_ENV}?"
                sh 'echo Deploying ${IMAGE_NAME}:${IMAGE_TAG} to ${DEPLOY_ENV}'
            }
        }
    }
}
