CCP examples
============
Some examples for Openstack CCP.

Expose Horizon
==============

* Get nodePort of Horizon service:
```bash
echo $(kubectl --namespace=ccp get svc/horizon -o go-template='{{(index .spec.ports 0).nodePort}}')
```

* NAT on your router/jump-box to any k8s minion public IP and nodePort to provide external access:
```bash
iptables -t nat -I PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 10.210.0.12:32643
iptables -t nat -I POSTROUTING -d 10.210.0.12 ! -s 10.210.0.0/24 -j MASQUERADE
iptables -I FORWARD -d 10.210.0.12 -j ACCEPT
```

Where `10.210.0.12` is IP of one of your k8s minions and `32643` is nodePort of Horizon service.

* You can do the same for novnc:
```bash
echo $(kubectl --namespace=ccp get svc/nova-novncproxy -o go-template='{{(index .spec.ports 0).nodePort}}')
```
