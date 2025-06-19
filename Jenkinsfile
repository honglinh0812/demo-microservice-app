pipeline {
    agent any
    environment {
        DOCKER_HUB_USERNAME = 'linhx021' 
        DOCKER_HUB_REPO = 'linhx021' 
        CONFIG_REPO_URL = 'https://github.com/honglinh0812/CD-VDT.git' // Thay thế bằng URL config repo của bạn
        CONFIG_REPO_BRANCH = 'main' 
        FRONTEND_SOURCE_PATH = '/microservices-frontend'
        BACKEND_SOURCE_PATH = '/microservices-backend' 
        FRONTEND_HELM_CHART_PATH = '/app/frontend-chart' 
        BACKEND_HELM_CHART_PATH = '/app/backend-chart' 
        VALUES_FILE = 'values.yaml'
        }
    stages {
        stage('Checkout source code') {
            steps {
                script {
                    def tagName = env.GIT_BRANCH?.replaceAll('refs/tags/', '')
                    if (!tagName) {
                        error 'GIT_BRANCH does not contain tag name. Make sure this job is triggered by a tag.'
                    }
                    echo "Building for tag: ${tagName}"
                    checkout scm
                }
            }
        }
        stage('Build and push Docker images') {
            steps {
                script {
                    def tagName = env.TAG_NAME
                    def frontendImage = "${DOCKER_HUB_REPO}/microservices-frontend:${tagName}"
                    def backendImage = "${DOCKER_HUB_REPO}/microservices-backend:${tagName}"
                    withCredentials([usernamePassword(credentialsId: 'dockerhubcredentials', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                        sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"

                        echo "Building Docker image: ${frontendImage}"
                        dir(FRONTEND_SOURCE_PATH) {
                            sh "docker build -t ${frontendImage} ."
                        }
                        sh "docker push ${frontendImage}"
                        echo "Docker image ${frontendImage} pushed to Docker Hub."

                        echo "Building Docker image: ${backendImage}"
                        dir(BACKEND_SOURCE_PATH) {
                            sh "docker build -t ${backendImage} ."
                        }
                        sh "docker push ${backendImage}"
                        echo "Docker image ${backendImage} pushed to Docker Hub."
                    }
                }
            }
        }
        stage('Update config repository') {
            steps {
                script {
                    def tagName = env.TAG_NAME
                    def configRepoDir = "config-repo"

                    withCredentials([usernamePassword(credentialsId: 'git-config-repo-credentials', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
                        sh "git config --global user.email 'jenkins@example.com'"
                        sh "git config --global user.name 'Jenkins CI'"
                        sh "git clone ${CONFIG_REPO_URL} ${configRepoDir}"
                        dir(configRepoDir) {
                            sh "git checkout ${CONFIG_REPO_BRANCH}"

                            def frontendValuesFilePath = "${FRONTEND_HELM_CHART_PATH}/${VALUES_FILE}"
                            sh "sed -i 's|tag: ".*"|tag: \"${tagName}\"|g' ${frontendValuesFilePath}"
                            echo "Updated ${frontendValuesFilePath} with image tag: ${tagName}"

                            def backendValuesFilePath = "${BACKEND_HELM_CHART_PATH}/${VALUES_FILE}"
                            sh "sed -i 's|tag: ".*"|tag: \"${tagName}\"|g' ${backendValuesFilePath}"
                            echo "Updated ${backendValuesFilePath} with image tag: ${tagName}"

                            sh "git add ${frontendValuesFilePath}"
                            sh "git add ${backendValuesFilePath}"
                            sh "git commit -m 'CI: Update frontend and backend image tags to ${tagName}'"
                            sh "git push origin ${CONFIG_REPO_BRANCH}"
                        }
                    }
                    echo "Config repository updated successfully."
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}