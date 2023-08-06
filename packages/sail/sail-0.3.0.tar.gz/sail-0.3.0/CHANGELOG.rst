Changelog
=========

0.3.0 (2015-03-03)
------------------

- [feat] compose: up from local docker-compose.yml
- [feat] compose: export compose from deployed services
- [feat] edit link when redeploying
- [feat] custom volumes endpoints and sizes
- [fix] explicits message for 409 HTTP errors

0.2.4 (2015-01-14)
------------------

- [feat] attached domains
- [feat] IPs whitelist
- [feat] add --batch option on create/start/redeploy/scale to avoid streaming
- [feat] add number of containers in "services ps"


0.2.3 (2014-11-13)
------------------

- [feat] account ACLs edition
- [feat] account informations
- [feat] application details

0.2.2 (2014-11-03)
------------------

- [feat] port publishing support

0.2.1 (2014-10-21)
------------------

- [fix] passwords with ':' character

0.2.0 (2014-10-21)
-----------

- [feature] enable streaming on service start
- [feature] display container ips in service ps
- [feature] external repositories
- [feature] private networks management
- [feature] container as network gateway
- [fix] service links aliases
- [fix] fix streaming when adding service on different namespace

0.1.3.1 (2014-10-10)
--------------------

- [fix] redeploy "command" and "entrypoint" arguments split

0.1.3 (2014-10-10)
------------------

- [feature] streaming service creation and redeploy

0.1.2 (2014-09-26)
------------------

- [feature] restart policies
- [feature] private networks
- [enhancement] error feedback (authentication, network, ...)
- [fix] first install fail

0.1.1 (2014-09-12)
------------------

- [feature] autocompletion

0.1.0 (2014-09-05)
------------------

Initial release


