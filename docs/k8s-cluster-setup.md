# Kubernetes cluster setup: kubeadm, CRI-O и Calico

Документ описывает учебный, но реалистичный путь подготовки Kubernetes-кластера для
`ops-weather-platform`. Целевая версия: Kubernetes 1.28+, CRI-O 1.28+, Calico как CNI.

## Топология

Пример:

- `k8s-master-01` — control plane;
- `k8s-worker-01`, `k8s-worker-02` — worker-ноды;
- Ubuntu Server 22.04/24.04;
- доступ по SSH с sudo;
- открытая связность между нодами.

## Ручная подготовка узлов

На всех нодах:

```bash
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

sudo sysctl --system
```

Установить CRI-O и Kubernetes-пакеты из официальных репозиториев `pkgs.k8s.io`,
затем включить сервисы:

```bash
sudo systemctl enable --now crio
sudo systemctl enable kubelet
sudo apt-mark hold kubelet kubeadm kubectl
```

## Инициализация control plane

На `k8s-master-01`:

```bash
sudo kubeadm init \
  --cri-socket=unix:///var/run/crio/crio.sock \
  --pod-network-cidr=192.168.0.0/16

mkdir -p "$HOME/.kube"
sudo cp /etc/kubernetes/admin.conf "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"
```

Установить Calico:

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.3/manifests/calico.yaml
```

Команда `kubeadm init` выведет `kubeadm join ...`. Ее нужно выполнить на worker-нодах.

## Ansible-assisted путь

В репозитории есть Ansible-структура:

- `ansible/inventory/hosts.yml` — пример inventory;
- `ansible/group_vars/all.yml` — версии Kubernetes/CRI-O и pod CIDR;
- `roles/k8s_prereqs` — swap, modules, sysctl, базовые пакеты;
- `roles/crio` — установка и запуск CRI-O;
- `roles/k8s_packages` — kubeadm, kubelet, kubectl.

Запуск:

```bash
cd ansible
ansible-playbook playbooks/prepare-k8s.yml
```

После этого инициализация control plane и `kubeadm join` выполняются осознанно вручную:
так проще контролировать токены, сертификаты и итоговую топологию.

## Деплой приложения

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

Проверки:

```bash
kubectl get nodes
kubectl get pods -A
kubectl -n ops-weather get deploy,svc,ingress
kubectl -n ops-weather port-forward svc/ops-weather-api 8000:80
curl http://127.0.0.1:8000/health
```

Проверка сетевой связности из пода:

```bash
kubectl run netcheck --rm -it --image=busybox:1.36 --restart=Never -- ping -c 3 8.8.8.8
```

