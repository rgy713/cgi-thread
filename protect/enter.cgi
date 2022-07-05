#!/usr/local/bin/perl

#┌─────────────────────────────
#│ Web Protect : enter.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session;
use WebProtectAuth;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

if ($in{login}) { &login; }
&enter_form;

#-----------------------------------------------------------
#  ログイン認証
#-----------------------------------------------------------
sub login {
	$in{id} =~ s/\W//g;
	$in{pw} =~ s/\W//g;

	# 未入力の場合
	if ($in{id} eq "" || $in{pw} eq "") { &error("認証できません"); }

	# 認証処理
	my $auth_result = WebProtectAuth::authenticate($in{id}, $in{pw});
	if($auth_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
	} elsif($auth_result != WebProtectAuth::SUCCESS) {
			&error("認証できません");
	}

	# 新規セッション発行
	my $ses = new CGI::Session(undef, undef, {Directory => $cf{sesdir}}) or die CGI::Session->errstr;

	# 有効時間
	my $jobtime = $cf{job_time} * 60;
	$ses->expire($jobtime);

	# セッションID
	my $sid = $ses->id();

	# ログ記録
	&save_log($in{id});

	# リダイレクト
	# PerlIS対応
	if ($ENV{PERLXS} eq "PerlIS") {
		print "HTTP/1.0 302 Temporary Redirection\r\n";
		print "Content-type: text/html\n";
	}
	print "Set-Cookie: CGISESSID=$sid;\n";
	print "Location: $cf{protect_cgi}\n\n";
	exit;
}

#-----------------------------------------------------------
#  認証画面
#-----------------------------------------------------------
sub enter_form {
	open(IN,"$cf{tmpldir}/enter.html") or &error("open err: enter.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 置き換え
	$tmpl =~ s/!enter_cgi!/$cf{enter_cgi}/;

	# 表示
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  ログ記録
#-----------------------------------------------------------
sub save_log {
	my $id = shift;

	# 時間/ホスト取得
	my ($time,$date) = &get_time;
	my ($host,$addr) = &get_host;

	# ブラウザ情報
	my $agent = $ENV{HTTP_USER_AGENT};
	$agent =~ s/[<>&"']//g;

	# ログファイル更新
	my $i = 0;
	my @data;
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		$i++;
		push(@data,$_);

		# 最大保存数
		last if ($i >= $cf{max_log} - 1);
	}
	seek(DAT, 0, 0);
	print DAT "$id<>$date<>$host<>$agent<>$time<>\n";
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);
}


