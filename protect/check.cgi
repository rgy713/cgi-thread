#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ WEB PROTECT : check.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定データ認識
require "./init.cgi";
my %cf = &init;

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM


# ファイルチェック
my %name = (
	pwdfile => 'パスワードファイル',
	logfile => 'アクセス履歴ファイル',
	memfile => '会員ファイル',
	regist_log => '連続ユーザー登録制限チェックログファイル'
	);
foreach ( keys(%name) ) {
	if (-f $cf{$_}) {
		print "$name{$_}位置: OK<br>\n";

		if (-r $cf{$_} && -w $cf{$_}) {
			print "$name{$_}パーミッション: OK<br>\n";
		} else {
			print "$name{$_}パーミッション: NG<br>\n";
		}
	} else {
		print "$name{$_}位置: NG<br>\n";
	}
}

# フォルダ位置
my %dir = (
	tmpldir => 'テンプレートディレクトリ',
	prvdir  => '隠しディレクトリ',
	sesdir  => 'セッションディレクトリ',
	);
foreach ( keys(%dir) ) {
	if (-d $cf{$_}) {
		print "$dir{$_}位置 : OK<br>\n";

		# セッションディレクトリはパーミッション確認
		if ($_ eq 'sesdir') {
			if (-r "$cf{$_}" && -r "$cf{$_}" && -r "$cf{$_}") {
				print "$dir{$_}パーミッション : OK<br>\n";
			} else {
				print "$dir{$_}パーミッション : NG<br>\n";
			}
		}

	} else {
		print "$dir{$_}位置 : NG<br>\n";
	}
}

# sendmail
if (-e $cf{sendmail}) {
	print "sendmail位置 : OK<br>\n";
} else {
	print "sendmail位置 : NG<br>\n";
}

print "</body></html>\n";
exit;

