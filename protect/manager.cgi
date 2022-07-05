#!/usr/local/bin/perl

#┌─────────────────────────────
#│ WEB PROTECT : manager.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Jcode;
use WebProtectAuth;

# 設定ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

# 処理分岐
if ($in{mode} eq "new_user") { &new_user; }
if ($in{mode} eq "chg_pwd") { &chg_pwd; }
if ($in{mode} eq "del_user") { &del_user; }
&error("不正なアクセスです");

#-----------------------------------------------------------
#  ユーザ登録
#-----------------------------------------------------------
sub new_user {
	# 発行制限
	if ($cf{pwd_regist} > 1) { &error("不正なアクセスです"); }

	# ホスト名を取得
	my ($host,$addr) = &get_host;

	# チェック
	my $err;
	if ($in{name} eq "") { $err .= "名前が入力モレです<br>"; }
	if ($in{eml1} ne $in{eml2}) { $err .= "メールの再入力内容が異なります<br>"; }
	if ($in{eml1} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,}$/) {
		$err .= "電子メールの入力内容が不正です<br>";
	}
	if (length($in{id}) < 4 || length($in{id}) > 8) {
		$err .= "ログインIDは4～8文字で入力してください<br>";
	}
	if ($in{id} =~ /\W/) {
		$err .= "ログインIDに英数字以外の文字が含まれています<br>";
	}
	if ($err) { &error($err); }

	# 新規ユーザー登録
	my @regist_result = WebProtectAuth::create($in{id}, undef, $in{name}, $in{eml1}, undef, 1);
	if($regist_result[0] != WebProtectAuth::SUCCESS) {
		if($regist_result[0] == WebProtectAuth::IS_DENY_HOST) {
			&error("現在登録休止中です");
		} elsif($regist_result[0] == WebProtectAuth::REGIST_LOG_FILE_OPEN_ERROR) {
			&error("open err: $cf{regist_log}");
		} elsif($regist_result[0] == WebProtectAuth::REPEATITIVE_REGIST_LIMIT) {
			&error("連続登録はもうしばらく時間をおいて下さい");
		} elsif($regist_result[0] == WebProtectAuth::IS_DENY_EMAIL_ADDRESS) {
			&error("登録するメールアドレスとして使用できない文字列が含まれています");
		} elsif($regist_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($regist_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("write err: $cf{memfile}");
		} else {
			my @err_msg;
			if($regist_result[0] & WebProtectAuth::ID_EXISTS) {
				push(@err_msg, "$in{id}は既に発行済です。他のIDをご指定ください");
			}
			if($regist_result[0] & WebProtectAuth::DUPLICATE_EMAIL_ADDRESS) {
				push(@err_msg, "$in{eml1}は別のIDで登録されています。<br>他のメールアドレスをご指定ください");
			}
			&error(join("<br><br>", @err_msg));
		}
	}

	# メール本文テンプレ用
	my %m;
	$m{date}  = $regist_result[2];
	$m{name}  = $in{name};
	$m{email} = $in{eml1};
	$m{host}  = $host;
	$m{id} = $in{id};
	$m{pw} = $regist_result[1];
	$m{master} = $cf{master};

	# メール本文テンプレ
	my $mbody;
	open(IN,"$cf{tmpldir}/mail.txt") or &error("open err: mail.txt");
	while(<IN>) {
		s/!(\w+)!/$m{$1}/;

		$mbody .= $_;
	}
	close(IN);

	# 本文をコード変換
	Jcode::convert(\$mbody, 'jis', 'sjis');

	# 件名をMIMEエンコード
	my $msub = Jcode->new("登録のご案内")->mime_encode;

	# sendmailコマンド
	my $scmd = "$cf{sendmail} -t -i";
	if ($cf{sendm_f} == 1) {
		$scmd .= " -f $cf{master}";
	}

	# sendmail送信
	open(MAIL,"| $scmd") or &error("メール送信失敗");
	print MAIL "To: $in{eml1}\n";
	print MAIL "From: $cf{master}\n";
	print MAIL "Cc: $cf{master}\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $cf{version}\n\n";
	print MAIL "$mbody\n";
	close(MAIL);

	# 完了画面
	my $msg = qq|ログインIDとパスワード情報は<br><b>$in{eml1}</b><br>へ送信しました。|;
	&message("新規登録完了", $msg);
}

#-----------------------------------------------------------
#  ユーザPW変更
#-----------------------------------------------------------
sub chg_pwd {
	# 発行制限
	if ($cf{pwd_regist} > 2) { &error("不正なアクセスです"); }

	# チェック
	my $err;
	if ($in{id} eq "") { $err .= "ログインIDが入力モレです<br>"; }
	if ($in{pw} eq "") { $err .= "旧パスワードが入力モレです<br>"; }
	if ($in{pw1} eq "") { $err .= "新パスワードが入力モレです<br>"; }
	if ($in{pw1} ne $in{pw2}) { $err .= "新パスワードで再度入力分が異なります<br>";	}
	if (length($in{pw1}) > 8) { $err .= "新パスワードは英数字8文字以内です<br>"; }
	if ($in{pw1} =~ /\W/) { $err .= "パスワードは英数字のみです<br>"; }
	if ($err) { &error($err); }

	# パスワード変更
	my @update_result = WebProtectAuth::update_password($in{id}, $in{pw}, $in{pw1}, 0);
	if($update_result[0] == WebProtectAuth::IS_DENY_HOST) {
		&error("現在登録休止中です");
	} elsif($update_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
		&error("open err: $cf{pwdfile}");
	} elsif($update_result[0] == WebProtectAuth::ID_NOTFOUND) {
		&error("認証できません");
	} elsif($update_result[0] == WebProtectAuth::PASS_MISMATCH) {
		&error("認証できません$in{pw}, $update_result[1]"); 
	}

	# 完了画面
	&message("パスワード変更完了", "ご利用をありがとうございました。");
}

#-----------------------------------------------------------
#  ユーザ削除
#-----------------------------------------------------------
sub del_user {
	# 発行制限
	if ($cf{pwd_regist} > 2) { &error("不正なアクセスです"); }

	# チェック
	if ($in{id} eq "" || $in{pw} eq "") {
		&error("IDまたはパスワードが入力モレです");
	}

	# 確認画面
	if ($in{job} eq "") { &del_form; }

	# ユーザー削除
	my $delete_result = WebProtectAuth::delete($in{id}, $in{pw}, 0);
	if($delete_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
		&error("open err: $cf{pwdfile}");
	} elsif($delete_result == WebProtectAuth::ID_NOTFOUND) {
		&error("認証できません");
	} elsif($delete_result == WebProtectAuth::PASS_MISMATCH) {
		&error("認証できません");
	} elsif($delete_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
		&error("open errr: $cf{memfile}");
	}

	# 完了画面
	&message("登録ID削除完了", "これまでのご利用をありがとうございました。");
}

#-----------------------------------------------------------
#  削除確認画面
#-----------------------------------------------------------
sub del_form {

	open(IN,"$cf{tmpldir}/conf.html") or &error("open err: conf.html");
	print "Content-type: text/html\n\n";
	while(<IN>) {
		s/!id!/$in{id}/g;
		s/!pw!/$in{pw}/g;
		s/!manager_cgi!/$cf{manager_cgi}/g;

		print;
	}
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  完了画面
#-----------------------------------------------------------
sub message {
	my ($ttl,$msg) = @_;

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/message.html") or &error("open err: message.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 置き換え
	$tmpl =~ s/!page_ttl!/$ttl/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!back_url!/$cf{back_url}/g;

	# 表示
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

