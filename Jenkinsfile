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
                    def tagName = ""
                    // Đảm bảo đã checkout mã nguồn đầy đủ để có thông tin Git
                    checkout scm
                    // Lấy commit hash hiện tại
                    def currentCommit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                    echo "Current commit hash: ${currentCommit}"

                    // Cố gắng lấy tên tag chính xác cho commit hiện tại
                    try {
                        // Lệnh này sẽ chỉ trả về tag nếu commit hiện tại chính xác là một tag
                        tagName = sh(returnStdout: true, script: "git describe --tags --exact-match ${currentCommit}").trim()
                    } catch (Exception e) {
                        echo "Cảnh báo: Lệnh `git describe --exact-match` thất bại cho commit ${currentCommit}. Lỗi: ${e.getMessage()}"
                        // Nếu không phải là exact match tag, thử tìm tag gần nhất hoặc từ biến môi trường
                        try {
                            tagName = sh(returnStdout: true, script: 'git describe --tags --abbrev=0').trim()
                        } catch (Exception e2) {
                            echo "Cảnh báo: Lệnh `git describe --abbrev=0` thất bại. Lỗi: ${e2.getMessage()}"
                            // Phương án dự phòng cuối cùng: lấy từ biến môi trường của Jenkins
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
        stage('Build and push Docker images') {
            steps {
                script {
                    def tagName = env.TAG_NAME
                    def frontendImage = "${DOCKER_HUB_REPO}/microservices-frontend:${tagName}"
                    def backendImage = "${DOCKER_HUB_REPO}/microservices-backend:${tagName}"
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
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
            cleanWs()
        }
    }
}
