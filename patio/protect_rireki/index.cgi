#!/usr/local/bin/perl

#┌─────────────────────────────
#│ Web Protect : enter.cgi (Original) - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Encode qw();
use HistoryCookie;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

# 書込ID Cookie
my $cookie = HistoryCookie->new();

# ログイン認証実施
if ($in{login}) {
	login();
}

# ログイン認証を行わない時の表示
if (!defined($cookie->('HISTORY_ID'))) {
	# 未ログイン時に、書込ID発行/書込ID認証フォーム表示
	issue_or_login_form();
} else {
	# 既にログインしている時に、アカウント情報/パスワード変更フォーム表示
	account_info();
}

#-----------------------------------------------------------
#  ログイン認証
#-----------------------------------------------------------
sub login {
	# ID3文字目の分割フォルダナンバーとユーザーネームのセパレーターを_に変換したIDを取得
	my $login_id = do {
		# マルチバイト文字が入ることも考慮し、内部エンコードに変換
		my $enc_cp932 = Encode::find_encoding('cp932');
		my $orig_id = $enc_cp932->decode($in{id});

		# 入力ID先頭・末尾のホワイトスペースを除去
		$orig_id =~ s/^\W+|\W+$//g;

		# ID先頭の分割フォルダナンバー部を取得し、整形
		my $folder_number = sprintf('%02d', int(substr($orig_id, 0, 2)));

		# ID後半のユーザーネーム部を取得し、整形
		my $username = substr($orig_id, 3);
		$username =~ s/[^0-9a-zA-Z]//g;

		# 分割フォルダナンバーとユーザーネームに_をつけてIDを再構成
		"${folder_number}_${username}";
	};

	$in{pw} =~ s/\W//g;

	# 未入力の場合
	if ($login_id eq "" || $in{pw} eq "") { &error("書込IDと履歴パスワードが一致しません。"); }

	# 認証実行
	if (!$cookie->login($login_id, $in{pw})) {
		&error("書込IDと履歴パスワードが一致しません。")
	}

	# ログ記録
	&save_log($login_id);

	# 認証完了メッセージ表示
	message('書込ID認証完了', '認証に成功しました。');
}

#-----------------------------------------------------------
#  書込ID発行/ログイン画面
#-----------------------------------------------------------
sub issue_or_login_form {
	open(IN,"$cf{tmpldir}/issue_or_login.html") or &error("open err: issue_or_login.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 置き換え
	$tmpl =~ s/!manager_cgi!/$cf{manager_cgi}/g;
	$tmpl =~ s/!enter_cgi!/$cf{enter_cgi}/g;

	# 表示
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  ログイン済みアカウント情報画面
#-----------------------------------------------------------
sub account_info {
	open(IN,"$cf{tmpldir}/account_info.html") or &error("open err: account_info.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 書込ID/パスワード取得
	my $history_id = $cookie->('HISTORY_ID');
	my $history_password = $cookie->('HISTORY_PASSWORD');

	# 置き換え
	$tmpl =~ s/!manager_cgi!/$cf{manager_cgi}/g;
	$tmpl =~ s/!user_id!/$history_id/g;
	$tmpl =~ s/!user_password!/$history_password/g;

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
