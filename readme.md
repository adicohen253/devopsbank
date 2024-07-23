# Python flask Devopsbank application
This project is a standalone bank application written using flask framework and hosted in local kubernetes cluster
The application provides a banking platform for users, designed to handle various banking operations and transactions like deposit, withdraw, view monthly history and statistics and more.
The application also includes input validation in both client and server side and works as a statefull application by using session and storing
them in the database (enabling the application to scale without disturbing user experience)

## Architecture
The architecture of this project is based on a standalone setup, which means it can run independently without any external dependencies and services.
The cluster contains the following technologies installed using helm charts:
- **Mongodb**: instance (installed in default namespace)
- **Devopsbank**: flask based application (installed in default namespace), the chart is accessible in the following link: https://github.com/adicohen253/devopsbank-chart
- **Jenkins**: for CI pipeline automation (installed in jenkins namespace)
- **Argocd**: for CD deployment automation (installed in argocd namespace)
- **Prometheus + Grafana stack**: for monitoring the application and other cluster components (installed in monitoring namespace)

## Set up
### Requirements
For setting up the cluster ensure you have the following installed:
1. **kubectl**
2. **helm**
3. **Kubernetes Cluster implementation (Minikube, Kind, Docker Desktop etc')**
4. **Git configured**: for forking the project configuration files using the following command:
   - (You can skip this and install them manually)
    ```
    git clone https://github.com/adicohen253/devopsbank
    
    ```
5. **Namespaces**: apply the following commands the create the required namespace for this project:
   ```
   kubectl create namespace jenkins
   kubectl create namespace argocd
   kubectl create namespace monitoring
   ```
  
### Dependencies
The project was built using helm charts with custom configuration files located in the appropriate directories inside the project.
Assuming you have helm and kubectl configured to your cluster.

and use the following commands to install the dependencies
1. **Mongodb**
   ```
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm install mongodb bitnami/mongodb --version 15.6.12 -f mongodb/mongodb-values.yaml
   ```
2. **Jenkins**
   ```
   helm repo add jenkins https://charts.jenkins.io/
   helm install jenkins jenkins/jenkins --version 5.4.2 -n jenkins -f jenkins/jenkins-values.yaml
   ```
3. **Argocd**
   ```
   helm repo add argo https://argoproj.github.io/argo-helm
   helm install argocd argo/argo-cd --version 7.3.6 -n argocd -f argocd/argocd-values.yaml
   ```
   After that apply the application yaml file so that argocd will deploy the changes of the applizcation automatically:
   ```
   sh kubectl apply -f argocd/devopsbank.yaml
   
   ```
4. **Prometheus stack**
   ```
   helm repo add prometheus https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack --version 61.2.0 -n monitoring
   ```
   After that apply the rule yaml file to let prometheus monitor and alert whenever the application's pod number is falling down from 3 pods:
   ```
   kubectl apply -f prometheus/application-pod-rule.yaml
   
   ```
## CI/CD Pipeline
### CI proccess
The project is using two branches: feature and main. those branches are tracked by jenkins multi-branch pipeline which is executing the CI proccess on a runner pod within the cluster (Check jenkins/runner.yaml for more details)
#### Feature Branch
1. **Run Tests**
    - Tests are executed using pytest.
2. **Build Application image**
    - Builds the application image and tag it with the current build number.
3. **Merge Request**
    - Sends a merge request to the main branch.

#### Master Branch
1. **Run Tests**
    - Tests are executed using pytest.
2. **Build Application image**
    - Builds the application image and tag it with the current build number.
3. **Push Application image**
    - Pushes the application image to docker hub (See https://hub.docker.com/r/adi253/devopsbank-app/tags)
2. **Update Helm Chart**
    - Retrives the application helm chart from its git repository and sets the chart and image version of the deployment to the current build number (To match step 2)
3. **Commit Helm Chart update**
    - Commits the updated helm chart back to its repository

### CD process
Assuming new changes are passing the CI build process successfully, they are deployed to the cluster by argocd which tracks the helm chart repo for updates On a minute interval

## Accessing softwares
### Tunneling software services
If you are not using Docker implementation for kubernetes cluster you will need to use port forwarding to access the services of the software resides within the cluster:
1. **Devopsbank**:
    ```
    kubectl port-forward service/devopsbank 5000:5000
    
      ```
2. **Jenkins**:
    ```
    kubectl port-forward -n jenkins service/jenkins 8080:8080
    
    ```
3. **Argocd**:
    ```
    kubectl port-forward -n argocd service/argocd-server 8000:443
    
    ```
4. **Prometheus**:
    ```
    kubectl port-forward -n monitoring service/prometheus-kube-prometheus-prometheus 9090:9090
    
    ```
5. **Grafana**:
    ```
    kubectl port-forward -n monitoring service/prometheus-grafana 80:80
    
    ```
Note that the shells running this commands needs to stay open
### Accessing software services
1. **Devopsbank Application**
    - URL: http://localhost:5000

2. **Jenkins**
    - URL: http://localhost:8080
    - Use the username "admin" and run the following command the get the password to jenkins
      ```
      kubectl get secret jenkins -n jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode
      
      ```
    - Setup your Jenkinsfile for CI/CD

3. **ArgoCD**
    - URL: https://localhost:8000 (username: admin, password: 1234QWER)
    - Monitor application deployments
4. **Prometheus**
   - URL: http://localhost:9090
   - Watch the "DevopsbankPodCount" alert to make it works properly
5. **Grafana**
    - URL: http://localhost:80 (username: admin, password: prom-operator)
    - Visualize cluster metrics
    - **Note**: in the project/prometheus directory there are json files containing the grafana dashboard of the project, you can import them to your grafana instance after access it.