#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ WEB PROTECT : check.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;

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
	pwdfile    => 'パスワードファイル',
	logfile    => 'アクセス履歴ファイル',
	memfile    => '会員ファイル',
	regist_log => '書込IDログファイル',
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
	);
foreach ( keys(%dir) ) {
	if (-d $cf{$_}) {
		print "$dir{$_}位置 : OK<br>\n";
	} else {
		print "$dir{$_}位置 : NG<br>\n";
	}
}

# テンプレートファイルチェック
my %tmpl = (
	issue_or_login => '書込ID発行/書込ID認証フォーム ページテンプレート',
	account_info   => 'アカウント情報/パスワード変更フォーム ページテンプレート',
	message        => '完了画面 ページテンプレート',
	error          => 'エラー画面 ページテンプレート',
	);
foreach ( keys(%tmpl) ) {
	if (-r File::Spec->catfile($cf{tmpldir}, "$_.html")) {
		print "$tmpl{$_}読み込み : OK<br>\n";
	} else {
		print "$tmpl{$_}読み込み : NG<br>\n";
	}
}

print "</body></html>\n";
exit;

