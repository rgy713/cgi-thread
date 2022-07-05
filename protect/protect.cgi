#!/usr/local/bin/perl

#┌─────────────────────────────
#│ WEB PROTECT : protect.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

# アクセス認証
&cert_access;

#-----------------------------------------------------------
#  アクセス認証
#-----------------------------------------------------------
sub cert_access {
	# セッション認識
	my $ses = CGI::Session->load(undef, undef, {Directory => $cf{sesdir}});

	# ログアウト
	if ($in{mode} eq 'logout') {
		$ses->delete();

		# 入室画面に戻る
		&redirect($cf{enter_cgi});
	}

	# 期限切れ
	if ( $ses->is_expired || $ses->is_empty ) {
		my $data = qq|<p>[<a href="$cf{enter_cgi}">ログインする</a>]</p>|;
		&error("タイムアウトです。再度ログインしてください。", $data);
   	}

	# 隠しファイル出力
	&open_file;
}

#-----------------------------------------------------------
#  認証ページ表示
#-----------------------------------------------------------
sub open_file {
	# バイナリファイル
	my %bin = %{$cf{binary}};
	my ($flg,$key,$val);
	foreach ( keys(%in) ) {
		if (defined($bin{$_})) {
			$flg++;
			$key = $_;
			$val = $in{$_};
			last;
		}
	}
	if ($flg) { &bin_out($key,$val); }

	# 対象ファイル定義
	my $page = $in{page} || '0';
	my $target = ${$cf{secret}}[$page];

	# CGIファイルならリダイレクト
	if ($target =~ m|https?://|) {
		&redirect($target);

	# HTMLファイルなら読み出し
	} else {
		open(IN,"$cf{prvdir}/$target") or &error("open err: $target");
		print "Content-type: text/html\n\n";
		print <IN>;
		close(IN);

		exit;
	}
}

#-----------------------------------------------------------
#  バイナリ出力
#-----------------------------------------------------------
sub bin_out {
	my ($key,$val) = @_;

	# ヘッダー/拡張子
	my ($head,$ext) = split(/,/, ${$cf{binary}}{$key});

	# 読み出し
	open(IN,"$cf{prvdir}/$val.$ext") || die;
	print "Content-type: $head\n";
	print "Content-Disposition: attachment; filename=\"$val.$ext\"\n\n";
	binmode(IN);
	binmode(STDOUT);
	print <IN>;
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  リダイレクト
#-----------------------------------------------------------
sub redirect {
	my $uri = shift;

	# PerlIS対応
	if ($ENV{PERLXS} eq "PerlIS") {
		print "HTTP/1.0 302 Temporary Redirection\r\n";
		print "Content-type: text/html\n";
	}
	# リダイレクト
	print "Location: $uri\n\n";
	exit;
}

