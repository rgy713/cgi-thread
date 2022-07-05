#!/usr/local/bin/perl

#┌─────────────────────────────
#│ WEB PROTECT : admin.cgi - 2013/04/06
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session::ExpireSessions;
use Jcode;
use WebProtectAuth;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

# 認証
&check_passwd;

# 処理分岐
if ($in{data_new}) { &data_new; }
if ($in{data_mente}) { &data_mente; }
if ($in{look_log}) { &look_log; }
if ($in{exp_ses}) { &exp_ses; }

# メニュー画面
&menu_html;

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	&header("メニューTOP");

	print <<EOM;
<div align="center">
<p>選択ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table border="1" cellpadding="5" cellspacing="0">
<tr>
	<th bgcolor="#cccccc">選択</th>
	<th bgcolor="#cccccc" width="250">処理メニュー</th>
</tr><tr>
	<th><input type="submit" name="data_new" value="選択"></th>
	<td>新規会員登録作成</td>
</tr><tr>
	<th><input type="submit" name="data_mente" value="選択"></th>
	<td>会員登録メンテナンス（修正・削除）</td>
</tr><tr>
	<th><input type="submit" name="look_log" value="選択"></th>
	<td>アクセスログ閲覧</td>
</tr><tr>
	<th><input type="submit" name="exp_ses" value="選択"></th>
	<td>セッションファイル掃除</td>
</tr><tr>
	<th><input type="button" value="選択" onclick="javascript:window.location='$cf{admin_cgi}'"></th>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  登録フォーム
#-----------------------------------------------------------
sub data_new {
	my ($id,$nam,$eml,$memo) = @_;

	# 新規記事追加
	if ($in{job} eq "new") {
		&data_add;
	}

	# パラメータ指定
	my ($mode,$job);
	if ($in{data_new}) {
		$mode = "data_new";
		$job = "new";
	} else {
		$mode = "data_mente";
		$job = "edit2";
	}

	&header("メニューTOP ＞ 登録フォーム");
	&back_btn;
	print <<EOM;
<b class="ttl">■登録フォーム</b>
<hr class="ttl" size="1">
<p>各項目を入力して送信ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="$mode" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="job" value="$job">
<table border="1" cellspacing="0" cellpadding="5" class="form">
<tr>
	<th>名前</th>
	<td><input type="text" name="name" size="40" value="$nam"></td>
</tr><tr>
	<th>E-mail</th>
	<td><input type="text" name="email" size="40" value="$eml"></td>
</tr><tr>
	<th>ユーザーID [必須]</th>
EOM

	# 新規フォーム
	if ($id eq "") {
		print qq|<td class="ttl"><input type="text" name="id" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|（英数字8文字以内）</td></tr>\n|;
		print qq|<tr><th>パスワード [必須]</th>\n|;
  		print qq|<td class="ttl"><input type="text" name="pw" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|（英数字8文字以内）</td></tr>\n|;

	# 修正フォーム
	} else {
		print qq|<td><b>$id</b></td></tr>\n|;
		print qq|<tr><th>パスワード</th>\n|;
  		print qq|<td class="ttl"><input type="text" name="pw" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|（英数字8文字以内）<br>\n|;
		print qq|<input type="checkbox" name="pwchg" value="1"> 強制変更の場合のみチェックし、新パスワードを入力</td></tr>\n|;
		print qq|<input type="hidden" name="id" value="$in{id}">\n|;
	}

	print <<EOM;
<tr>
	<th>備考</th>
	<td><textarea name="memo" cols="42" rows="2">$memo</textarea></td>
</tr>
</table>
<br>
<input type="submit" value="送信する">
<input type="reset" value="リセット">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  データ追加
#-----------------------------------------------------------
sub data_add {
	# チェック
	if ($in{id} eq "" || $in{pw} eq "") {
		&error("IDまたはパスワードが未入力です");
	}
	if ($in{id} =~ /\W/ || $in{pw} =~ /\W/) {
		&error("IDまたはパスワードに英数字以外の文字が入力されています");
	}

	# 新規ユーザー登録
	my @regist_result = WebProtectAuth::create($in{id}, $in{pw}, $in{name}, $in{email}, $in{memo}, 0);
	if($regist_result[0] != WebProtectAuth::SUCCESS) {
		if($regist_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($regist_result[0] == WebProtectAuth::ID_EXISTS) {
			&error("<b>$in{id}</b>は既に発行済です");
		} elsif($regist_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("write err: $cf{memfile}");
		}
	}

	$in{name}  ||= '名前なし';
	$in{email} ||= 'E-mailなし';
	$in{memo}  ||= 'なし';

	&header;
	print <<EOM;
<h4>▽以下のとおり発行しました。</h4>
<dl>
<dt>【名前】<dd>$in{'name'}
<dt>【E-mail】<dd>$in{'email'}
<dt>【ユーザID】<dd>$in{'id'}
<dt>【パスワード】<dd>$in{'pw'}
<dt>【備考】<dd>$in{'memo'}
</dl>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_new" value="1">
<input type="submit" value="登録フォーム">
</form>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="管理メニュー">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  会員登録メンテナンス
#-----------------------------------------------------------
sub data_mente {
	# --- 修正フォーム
	if ($in{job} eq "edit" && $in{id}) {

		# 会員ファイル読み込み
		my @read_result = WebProtectAuth::read($in{id});
		if($read_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		} elsif($read_result[0]  == WebProtectAuth::ID_NOTFOUND) {
			&error("会員ファイル $cf{memfile} で $in{id} が見つかりませんでした。");
		} else {
			shift(@read_result);
		}

		&data_new(@read_result);

	# --- 修正実行
	} elsif ($in{job} eq "edit2") {

		# パスワード変更
		if ($in{pwchg} == 1) {
			if ($in{pw} eq "" || $in{pw} =~ /\W/) {
				&error("パスワードの指定が不正です");
			}

			my $update_result = WebProtectAuth::update_password($in{id}, undef, $in{pw}, 1);
			if($update_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
				&error("open err: $cf{pwdfile}");
			}
		}

		# 会員ファイル
		my $update_result = WebProtectAuth::update_userinfo($in{id}, $in{name}, $in{email}, $in{memo});
		if($update_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		}

		&msg_edit;

	# --- 削除
	} elsif ($in{job} eq "dele" && $in{id}) {

		# ユーザー削除
		my $delete_result = WebProtectAuth::delete($in{id}, undef, 1);
		if($delete_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($delete_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		}
	}

	# ページ数認識
	$in{page} ||= 0;
	foreach ( keys(%in) ) {
		if (/^page:(\d+)$/) {
			$in{page} = $1;
			last;
		}
	}

	# ユーザー並び順
	foreach ( keys(%in) ) {
		if (/^desc:(\d+)$/) {
			$in{desc} = $1;
			last;
		}
	}
	if(!exists($in{desc})) { $in{desc} = 1; }

	&header("メニューTOP ＞ 会員登録メンテナンス");
	&back_btn;
	print <<EOM;
<form action="$cf{admin_cgi}" method="post" name="order">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
EOM
	print '<input type="hidden" name="desc" value="' . int(!$in{desc}) . "\">\n";
	print "<b class=\"ttl\">■会員登録メンテナンス</b>\n";
	print '<span style="margin-left:1em;"><a href="javascript:void(0)" onclick="javascript:order.submit()">[登録が' . ($in{desc} ? "古" : "新し") . "い順に並び替え]</a></span>\n";
	print <<EOM;
</form>
<hr class="ttl" size="1">
<p>処理を選択して送信ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="page" value="$in{page}">
<input type="hidden" name="desc" value="$in{desc}">
処理 : <select name="job">
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
EOM

	my @read_results = WebProtectAuth::multiread($in{page}, $in{desc});
	my $last;
	if($read_results[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
		&error("open err: $cf{memfile}");
	} else {
		shift(@read_results);
		$last = shift(@read_results);
	}

	for(my $i=0; $i<scalar(@read_results); $i++) {
		my ($id,$nam,$eml,$memo) = @{$read_results[$i]};

		$nam ||= '名前なし';
		$eml ||= 'メールアドレスなし';
		$memo =~ s/<br>/ /g;

		print qq|<hr><input type="radio" name="id" value="$id">\n|;
		print qq|<b>$id</b> [名前] $nam [備考] $memo [メール] $eml\n|;
	}

	print "<hr>\n";

	my $next = $in{page} + $cf{pg_max};
	my $back = $in{page} - $cf{pg_max};
	if ($back >= 0) {
		print qq|<input type="submit" name="page:$back" value="前の$cf{pg_max}件">\n|;
	}
	if ($next < $last) {
		print qq|<input type="submit" name="page:$next" value="次の$cf{pg_max}件">\n|;
	}

	print "</form>\n";
	print "</body></html>\n";
	exit;
}

#-----------------------------------------------------------
#  ログ閲覧
#-----------------------------------------------------------
sub look_log {
	if (!$in{list} && !$in{calc}) { $in{list} = 1; }
	my %btn = ('list' => '一覧', 'calc' => '集計');

	&header("メニューTOP ＞ アクセスログ閲覧");
	&back_btn;
	print <<EOM;
<b class="ttl">■アクセスログ閲覧</b>
<hr class="ttl" size="1">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="look_log" value="1">
EOM

	foreach ( 'list', 'calc' ) {
		if ($in{$_}) {
			print qq|<input type="submit" name="$_" value="$btn{$_}" disabled>\n|;
		} else {
			print qq|<input type="submit" name="$_" value="$btn{$_}">\n|;
		}
	}

	print "</form>\n";

	# ログ一覧の場合
	if ($in{list}) {
		print "<dl><dt>▼<b>ログ一覧</b>\n";

		open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
		while (<IN>) {
			my ($id,$date,$host,$agent) = split(/<>/);

			print "<dt><hr><b>$id</b> - $date 【$host】\n";
			print "<dd>$agent\n";
		}
		close(IN);

		print "<dt><hr></dl>\n";

	# ログ集計の場合
	} else {
		my ($i, %log);
		open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
		while (<IN>) {
			my ($id,$date,$host,$agent) = split(/<>/);

			$log{$id}++;
			$i++;
		}
		close(IN);

		print qq|<p>▼<b>ログ集計</b> (直近 : $i回)</p>\n|;
		print qq|<table border="1" cellpadding="3" cellspacing="0" class="form">\n|;
		print qq|<tr><th>ユーザID</th>\n|;
		print qq|<th>アクセス数</th></tr>\n|;

		# ソート
		foreach ( sort { $log{$b} <=> $log{$a} }keys(%log) ) {
			print qq|<tr><td nowrap>$_<br></td>\n|;
			print qq|<td align="center">$log{$_}</td></tr>\n|;
		}
		print "</table>\n";
	}

	print "</body></html>\n";
	exit;
}

#-----------------------------------------------------------
#  セッションファイル掃除
#-----------------------------------------------------------
sub exp_ses {
	# 実行
	if ($in{submit}) {
		# チェック
		$in{delta} =~ s/\D//g;
		if ($in{delta} eq '') { &error("時間数の指定が不正です。半角数字で指定してください。"); }

		# 秒数に直す
		$in{delta} *= 60;

		# 期限切れファイルを削除
		CGI::Session::ExpireSessions -> new(temp_dir => $cf{sesdir}, delta => $in{delta}) -> expire_file_sessions();

		# 完了画面
		&msg_expses;
	}

	# デフォルト
	my $delta = $cf{job_time} + 10;

	&header("メニューTOP ＞ セッションファイル掃除");
	&back_btn;
	print <<EOM;
<b class="ttl">■セッションファイル掃除</b>
<hr class="ttl" size="1">
<p>
	利用者がログイン後、ログアウトせずにブラウザを閉じると、不要なセッションファイルが蓄積されます。<br>
	定期的に、不要なセッションファイルを掃除するようにしましょう。<br>
</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="exp_ses" value="1">
<table border="1" cellspacing="0" cellpadding="5" class="form">
<tr>
	<th>未更新ファイル：</th>
	<td nowrap>
		<input type="text" name="delta" size="5" value="$delta"> 分以上のものを削除<br>
		（ログイン認証後の設定時間<b>$cf{job_time}</b>分以上で設定すること）
	</td>
</tr>
</table>
<br>
<input type="submit" name="submit" value=" 実行する ">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		&enter_form;

	# パスワード認証
	} elsif ($in{pass} ne $cf{password}) {
		&error("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	&header("入室画面");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:70px;">
<tr>
	<td height="40" align="center">
		<fieldset><legend>管理パスワード入力</legend>
		<br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" 認証 ">
		<br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  戻りボタン
#-----------------------------------------------------------
sub back_btn {
	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; メニュー">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  修正完了メッセージ
#-----------------------------------------------------------
sub msg_edit {
	&header("修正完了");
	print <<EOM;
<b class="ttl">■修正完了</b>
<hr class="ttl" size="1">
<h4>修正を完了しました</h4>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_mente" value="1">
<input type="submit" value="メンテナンス画面" style="width:150px;">
</form>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="管理メニュー" style="width:150px;">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub msg_expses {
	&header("掃除完了");
	print <<EOM;
<b class="ttl">■掃除完了</b>
<hr class="ttl" size="1">
<h4>不要なセッションファイルの削除を完了しました</h4>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="管理メニュー" style="width:100px;">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダ
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print "Content-type: text/html\n\n";
	print <<EOM;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,th,td { font-size:80%; background:#fff; }
.ttl { color:green; }
.msg { background:#ddd; }
table.form th { background:#ccc; white-space:nowrap; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}