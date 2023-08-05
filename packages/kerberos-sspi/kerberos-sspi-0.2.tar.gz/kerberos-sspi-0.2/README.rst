kerberos-sspi
=============

This Python package is API level equivalent to the kerberos python
package but instead of using the MIT krb5 package it uses the windows
sspi functionality. That allows your server and/or client that uses the
kerberos package to run under windows by alternatively loading
kerberos-sspi instead of the kerberos package.

(If you use python with cygwin you probably just use the original
kerberos package with a compiled MIT kerberos package.)

How to use it
=============

Here is an example:

.. code:: python


    try:
        import kerberos as k
    except:
        import kerberos_sspi as k

    from base64 import encodestring, decodestring

    flags=k.GSS_C_CONF_FLAG|k.GSS_C_INTEG_FLAG|k.GSS_C_MUTUAL_FLAG|k.GSS_C_SEQUENCE_FLAG

    errc, client = k.authGSSClientInit("test@vm-win7-kraemer", gssflags=flags)

    # to run a kerberos enabled server under my account i do as domain admin:
    #  setspn -A test/vm-win7-kraemer MYDOMAIN\kraemer
    # (might have to wait a few minutes before all DCs in active directory pick it up)
    errs, server = k.authGSSServerInit("test@vm-win7-kraemer")

    cres = sres= k.AUTH_GSS_CONTINUE
    response = ""
    round = 0
    while sres == k.AUTH_GSS_CONTINUE or cres == k.AUTH_GSS_CONTINUE:

        if cres == k.AUTH_GSS_CONTINUE:
            cres = k.authGSSClientStep(client, response)
            if cres == -1:
                print( "clientstep error")
                break
            response = k.authGSSClientResponse(client)
        if sres == k.AUTH_GSS_CONTINUE:
            sres = k.authGSSServerStep(server, response)
            if sres == -1:
                print( "serverstep error")
                break
            response = k.authGSSServerResponse(server)

        print( "round:", round)
        print( "server status :", sres)
        print( "client status :", cres)
        round += 1

    if sres == k.AUTH_GSS_COMPLETE and cres == k.AUTH_GSS_COMPLETE:
        print( "client: my username:", k.authGSSClientUserName(client))
        print( "server: who authenticated to me:", k.authGSSServerUserName(server))
        print( "server: my spn:", k.authGSSServerTargetName(server))
    else:
	print("failed!")

What's not working
==================

The methods:

-  changePassword
-  getServerPrincipalDetails

are not implemented and throw an exception

The flags:

-  GSS\_C\_ANON\_FLAG
-  GSS\_C\_PROT\_READY\_FLAG
-  GSS\_C\_TRANS\_FLAG

are not supported (and are not defined either so aceessing them will
throw an exception as well). Why? I couldn't find corresponding
ISC\_REQ\_\* for these flags...
