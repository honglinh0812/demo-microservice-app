pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: jnlp
      image: jenkins/inbound-agent:alpine-jdk11
      args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
      workingDir: /home/jenkins/agent
      volumeMounts:
        - name: workspace-volume
          mountPath: /home/jenkins/agent

    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      imagePullPolicy: Always
      command: [sleep]
      args: ["9999999"]
      volumeMounts:
        - name: workspace-volume
          mountPath: /home/jenkins/agent
        - name: docker-config
          mountPath: /kaniko/.docker/
  volumes:
    - name: workspace-volume
      emptyDir: {}
    - name: docker-config
      secret:
        secretName: dockerhub-credentials
        items:
          - key: .dockerconfigjson
            path: config.json
"""
        }
    }

    environment {
        DOCKER_HUB_USERNAME = 'linhx021' 
        DOCKER_HUB_REPO = 'linhx021' 
        CONFIG_REPO_URL = 'https://github.com/honglinh0812/CD-VDT.git' // Thay thế bằng URL config repo của bạn
        CONFIG_REPO_BRANCH = 'main' 
        FRONTEND_SOURCE_PATH = 'microservices-frontend'
        BACKEND_SOURCE_PATH = 'microservices-backend' 
        FRONTEND_HELM_CHART_PATH = '/app/frontend-chart' 
        BACKEND_HELM_CHART_PATH = '/app/backend-chart' 
        VALUES_FILE = 'values.yaml'
        }
    stages {
        stage('Checkout source code') {
            steps {
                script {
                    def tagName = ""
                    checkout scm
                    
                    def currentCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    echo "Current commit hash: ${currentCommit}"

                    try {
                        tagName = sh(returnStdout: true, script: "git describe --tags --exact-match ${currentCommit}").trim()
                    } catch (Exception e) {
                        echo "Cảnh báo: Lệnh `git describe --exact-match` thất bại cho commit ${currentCommit}. Lỗi: ${e.getMessage()}"
                        try {
                            tagName = sh(returnStdout: true, script: 'git describe --tags --abbrev=0').trim()
                        } catch (Exception e2) {
                            echo "Cảnh báo: Lệnh `git describe --abbrev=0` thất bại. Lỗi: ${e2.getMessage()}"
                            if (env.TAG_NAME) {
                                tagName = env.TAG_NAME
                            } else if (env.GIT_BRANCH && env.GIT_BRANCH.startsWith('tags/')) {
                                tagName = env.GIT_BRANCH.substring(env.GIT_BRANCH.lastIndexOf('/') + 1)
                            } else if (env.GIT_TAG) {
                                tagName = env.GIT_TAG
                            }
                        }
                    }

                    if (!tagName) {
                        error 'Không thể xác định tên tag. Đảm bảo job được kích hoạt bởi một Git tag và repository có tag.'
                    }
                    echo "Đang build cho tag: ${tagName}"
                }
            }
        }

        stage('Build and Push Frontend Image with Kaniko') {
            steps {
                script {
                    def gitCommit = sh(script: 'git rev-parse HEAD', returnStdout: true).trim().substring(0, 8)
                    def dockerImageTag = "microservice-frontend:${gitCommit}"
                    container('kaniko') {
                        echo "Đang build và push image với Kaniko: ${dockerImageTag}"
                        sh """
                        /kaniko/executor \
                            --context `pwd`/microservices-frontend \
                            --dockerfile `pwd`/microservices-frontend/Dockerfile \
                            --destination docker.io/${DOCKER_HUB_REPO}/${dockerImageTag}
                        """
                    }
                }
            }
        }


        stage('Build and Push Backend Image with Kaniko') {
            steps {
                script {
                    def gitCommit = sh(script: 'git rev-parse HEAD', returnStdout: true).trim().substring(0, 8)
                    def dockerImageTag = "microservice-backend:${gitCommit}"
                    container('kaniko') {
                        sh """
                        /kaniko/executor \
                            --dockerfile `pwd`/microservices-backend/Dockerfile \
                            --context `pwd`/microservices-backend \
                            --destination=docker.io/${DOCKER_HUB_REPO}/${dockerImageTag}
                        """     
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
                            sh "sed -i 's|tag: \\\".*\\\"|tag: \\\"${tagName}\\\"|g' ${frontendValuesFilePath}"
                            echo "Updated ${frontendValuesFilePath} with image tag: ${tagName}"

                            def backendValuesFilePath = "${BACKEND_HELM_CHART_PATH}/${VALUES_FILE}"
                            sh "sed -i 's|tag: \\\".*\\\"|tag: \\\"${tagName}\\\"|g' ${backendValuesFilePath}"
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
            script {
                node {
                    cleanWs()
                }
            }
        }
    }
}
