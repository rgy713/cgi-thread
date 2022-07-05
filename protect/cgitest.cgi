#!/usr/local/bin/perl

## cgitest.cgi - 2011/05/29
## created by (c) KentWeb

BEGIN {
	use CGI::Carp qw(carpout fatalsToBrowser);
	carpout(STDOUT);
}

# モジュール取り込み
require './cgiprot.cgi';
&cgiprot::check;

# テスト画面
print <<EOM;
Content-type: text/html

<html>
This is test.
</html>
EOM

