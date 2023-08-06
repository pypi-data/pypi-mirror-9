changelog
=========

* 0.3.5
    * netns: #90 -- netns setns support
    * generic: #99 -- support custom basic netlink socket classes
    * proxy-ng: #106 -- provide more diagnostics
    * nl80211: initial nl80211 support, iwutil module added
* 0.3.4
    * ipdb: #92 -- route metrics support
    * ipdb: #85 -- broadcast address specification
    * ipdb, rtnl: #84 -- veth support
    * ipdb, rtnl: tuntap support
    * netns: #84 -- network namespaces support, NetNS class
    * rtnl: proxy-ng API
    * pypi: #91 -- embed docs into the tarball
* 0.3.3
    * ipdb: restart on error
    * generic: handle non-existing family case
    * [fix]: #80 -- Python 2.6 unicode vs -O bug workaround
* 0.3.2
    * simple socket architecture
    * all the protocols now are based on NetlinkSocket, see examples
    * rpc: deprecated
    * iocore: deprecated
    * iproute: single-threaded socket object
    * ipdb: restart on errors
    * rtnl: updated ifinfmsg policies
* 0.3.1
    * module structure refactored
    * new protocol: ipq
    * new protocol: nfnetlink / nf-queue
    * new protocol: generic
    * threadless sockets for all the protocols
* 0.2.16
    * prepare the transition to 0.3.x
* 0.2.15
    * ipdb: fr #63 -- interface settings freeze
    * ipdb: fr #50, #51 -- bridge & bond options (initial version)
    * RHEL7 support
    * [fix]: #52 -- HTB: correct rtab compilation
    * [fix]: #53 -- RHEL6.5 bridge races
    * [fix]: #55 -- IPv6 on bridges
    * [fix]: #58 -- vlans as bridge ports
    * [fix]: #59 -- threads sync in iocore
* 0.2.14
    * [fix]: #44 -- incorrect netlink exceptions proxying
    * [fix]: #45 -- multiple issues with device targets
    * [fix]: #46 -- consistent exceptions
    * ipdb: LinkedSet cascade updates fixed
    * ipdb: allow to reuse existing interface in `create()`
* 0.2.13
    * [fix]: #43 -- pipe leak in the main I/O loop
    * tests: integrate examples, import into tests
    * iocore: use own TimeoutException instead of Queue.Empty
    * iproute: default routing table = 254
    * iproute: flush_routes() routine
    * iproute: fwmark parameter for rule() routine
    * iproute: destination and mask for rules
    * docs: netlink development guide
* 0.2.12
    * [fix]: #33 -- release resources only for bound sockets
    * [fix]: #37 -- fix commit targets
    * rtnl: HFSC support
    * rtnl: priomap fixed
* 0.2.11
    * ipdb: watchdogs to sync on RTNL events
    * ipdb: fix commit errors
    * generic: NLA operations, complement and intersection
    * docs: more autodocs in the code
    * tests: -W error: more strict testing now
    * tests: cover examples by the integration testing cycle
    * with -W error many resource leaks were fixed
* 0.2.10
    * ipdb: command chaining
    * ipdb: fix for RHEL6.5 Python "optimizations"
    * rtnl: support TCA_U32_ACT
    * [fix]: #32 -- NLA comparison
* 0.2.9
    * ipdb: support bridges and bonding interfaces on RHEL
    * ipdb: "shadow" interfaces (still in alpha state)
    * ipdb: minor fixes on routing and compat issues
    * ipdb: as a separate package (sub-module)
    * docs: include ipdb autodocs
    * rpc: include in setup.py
* 0.2.8
    * netlink: allow multiple NetlinkSocket allocation from one process
    * netlink: fix defragmentation for netlink-over-tcp
    * iocore: support forked IOCore and IOBroker as a separate process
    * ipdb: generic callbacks support
    * ipdb: routing support
    * rtnl: #30 -- support IFLA_INFO_DATA for bond interfaces
* 0.2.7
    * ipdb: use separate namespaces for utility functions and other stuff
    * ipdb: generic callbacks (see also IPDB.wait_interface())
    * iocore: initial multipath support 
    * iocore: use of 16byte uuid4 for packet ids
* 0.2.6
    * rpc: initial version, REQ/REP, PUSH/PULL
    * iocore: shared IOLoop
    * iocore: AddrPool usage
    * iproute: policing in FW filter
    * python3 compatibility issues fixed
* 0.2.4
    * python3 compatibility issues fixed, tests passed
* 0.2.3
    * [fix]: #28 -- bundle issue
* 0.2.2
    * iocore: new component
    * iocore: separate IOCore and IOBroker
    * iocore: change from peer-to-peer to flat addresses
    * iocore: REP/REQ, PUSH/PULL
    * iocore: support for UDP PUSH/PULL
    * iocore: AddrPool component for addresses and nonces
    * generic: allow multiple re-encoding
* 0.1.12
    * ipdb: transaction commit callbacks
    * iproute: delete root qdisc (@chantra)
    * iproute: netem qdisc management (@chantra)
* 0.1.11
    * netlink: get qdiscs for particular interface
    * netlink: IPRSocket threadless objects
    * rtnl: u32 policy setup
    * iproute: filter actions, such as `ok`, `drop` and so on
    * iproute: changed syntax of commands, `action` → `command`
    * tests: htb, tbf tests added
* 0.1.10
    * [fix]: #8 -- default route fix, routes filtering
    * [fix]: #9 -- add/delete route routine improved
    * [fix]: #10 -- shutdown sequence fixed
    * [fix]: #11 -- close IPC pipes on release()
    * [fix]: #12 -- stop service threads on release()
    * netlink: debug mode added to be used with GUI
    * ipdb: interface removal
    * ipdb: fail on transaction sync timeout
    * tests: R/O mode added, use `export PYROUTE2_TESTS_RO=True`
* 0.1.9
    * tests: all races fixed
    * ipdb: half-sync commit(): wait for IPs and ports lists update
    * netlink: use pipes for in-process communication
    * Python 2.6 compatibility issue: remove copy.deepcopy() usage
    * QPython 2.7 for Android: works
* 0.1.8
    * complete refactoring of class names
    * Python 2.6 compatibility issues
    * tests: code coverage, multiple code fixes
    * plugins: ptrace message source
    * packaging: RH package
* 0.1.7
    * ipdb: interface creation: dummy, bond, bridge, vlan
    * ipdb: if\_slaves interface obsoleted
    * ipdb: 'direct' mode
    * iproute: code refactored
    * examples: create() examples committed
* 0.1.6
    * netlink: tc ingress, sfq, tbf, htb, u32 partial support
    * ipdb: completely re-implemented transactional model (see docs)
    * generic: internal fields declaration API changed for nlmsg
    * tests: first unit tests committed
* 0.1.5
    * netlink: dedicated io buffering thread
    * netlink: messages reassembling
    * netlink: multi-uplink remote
    * netlink: masquerade remote requests
    * ipdb: represent interfaces hierarchy
    * iproute: decode VLAN info
* 0.1.4
    * netlink: remote netlink access
    * netlink: SSL/TLS server/client auth support
    * netlink: tcp and unix transports
    * docs: started sphinx docs
* 0.1.3
    * ipdb: context manager interface
    * ipdb: [fix] correctly handle ip addr changes in transaction
    * ipdb: [fix] make up()/down() methods transactional [#1]
    * iproute: mirror packets to 0 queue
    * iproute: [fix] handle primary ip address removal response
* 0.1.2
    * initial ipdb version
    * iproute fixes
* 0.1.1
    * initial release, iproute module

