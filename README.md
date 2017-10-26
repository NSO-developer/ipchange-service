# ipchange-service
NSO service that changes the device ip-address (in NSO) before pushing the service config and then changing it back to the old.

It works by augmenting a leaf secondary-ipaddress and an oper leaf original-ipaddress under /devices/device. Then when you want you service to use the secondary-ipaddress for a commit you set the service leaf use-secondary-ipaddress. After using the secondary-ipaddress a kicker that executes the action set-original-ip will change the /devices/device/address back to what was stored in original-ipaddress.


Something like:
```
$ ifconfig
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
    ether 6c:40:08:8a:ac:3a
    inet6 fe80::1047:639d:14d1:86e0%en0 prefixlen 64 secured scopeid 0x4
    inet 192.168.216.123 netmask 0xffffff00 broadcast 192.168.216.255
    nd6 options=201<PERFORMNUD,DAD>
    media: autoselect
    status: active

$ make all start
$ ncs_cli -u admin
admin@ncs> configure
admin@ncs% unhide debug
admin@ncs% show kickers
data-kicker ipchange {
    monitor     /ipchange:ipchange/ipchange:use-secondary-ipaddress;
    kick-node   current()/..;
    action-name set-original-ip;
}
admin@ncs% set devices device c0 secondary-ipaddress 192.168.216.123
admin@ncs% commit
admin@ncs% set devices device c0 address 1.1.1.1
admin@ncs% commit
admin@ncs% set ipchange c0-change device c0
admin@ncs% commit
Aborted: Failed to connect to device c0: connection refused: The kexTimeout (20000 ms) expired.
[error][2017-10-26 08:59:51]

[edit]
admin@ncs% *** ALARM connection-failure: Failed to connect to device c0: connection refused: The kexTimeout (20000 ms) expired.
admin@ncs% set ipchange c0-change device c0 use-secondary-ipaddress
admin@ncs% commit dry-run
cli {
    local-node {
        data  devices {
                  device c0 {
             -        address 1.1.1.1;
             +        address 192.168.216.123;
                      config {
             +            ios:hostname CE0;
                      }
                  }
              }
             +ipchange c0-change {
             +    device c0;
             +    use-secondary-ipaddress;
             +}
    }
}
admin@ncs% commit
Commit complete.
admin@ncs% show ipchange
ipchange c0-change {
    device c0;
}
admin@ncs% show devices device c0 address
address 1.1.1.1;
admin@ncs% show devices device c0 secondary-ipaddress
secondary-ipaddress 192.168.216.123;
admin@ncs%
```
