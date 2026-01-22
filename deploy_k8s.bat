@echo off
echo Deploying PromptShield to Kubernetes...

kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/prometheus.yaml

echo.
echo Deployment applied!
echo Backend: http://localhost:8003 (via Service/Ingress setup required or port-forward)
echo Frontend: http://localhost:3000
echo Prometheus: http://localhost:9090
echo.
echo To expose services locally if using Minikube:
echo minikube service promptshield-frontend
echo minikube service prometheus
echo.
pause
