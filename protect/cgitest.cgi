#!/usr/local/bin/perl

## cgitest.cgi - 2011/05/29
## created by (c) KentWeb

BEGIN {
	use CGI::Carp qw(carpout fatalsToBrowser);
	carpout(STDOUT);
}

# ���W���[����荞��
require './cgiprot.cgi';
&cgiprot::check;

# �e�X�g���
print <<EOM;
Content-type: text/html

<html>
This is test.
</html>
EOM

