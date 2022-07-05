#!/usr/local/bin/perl

#┌─────────────────────────────
#│ WEB PROTECT : admin.cgi - 2013/04/06
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;
use File::Basename;
use lib "./lib";
use Jcode;

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
	<td>書込ID発行</td>
</tr><tr>
	<th><input type="submit" name="data_mente" value="選択"></th>
	<td>書込IDメンテナンス（修正・削除）</td>
</tr><tr>
	<th><input type="submit" name="look_log" value="選択"></th>
	<td>アクセスログ閲覧</td>
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
	<th>書込ID [必須]</th>
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
	<th>名前</th>
	<td><input type="text" name="name" size="40" value="$nam"></td>
</tr>
<tr>
	<th>E-mail</th>
	<td><input type="text" name="email" size="40" value="$eml"></td>
</tr>
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
	my ($pwd_fh, $mem_fh, $history_log_folder_number_log_fh, $history_logfile_count_log_fh);
	my @opened_fh;

	# チェック
	my $err;
	if ($in{id} eq "") {
		$err .= "書込IDが未入力です<br>";
	} else {
		if (length($in{id}) < 4 || length($in{id}) > 8) {
			$err .= "書込IDは4～8文字で入力してください<br>";
		}
		if ($in{id} =~ /\W/) {
			$err .= "書込IDに英数字以外の文字が含まれています<br>";
		}
	}
	if ($in{pw} eq "") {
		$err .= "パスワードが未入力です<br>";
	} else {
		if ($in{pw} =~ /[^\w_]/) {
			$err .= "パスワードに英数字と_(アンダースコア)以外の文字が含まれています<br>";
		}
	}
	if ($err) { &error($err); }

	# パスワードファイルオープン
	if (!open($pwd_fh, '+<', $cf{pwdfile})) {
		close($_) foreach @opened_fh;
		&error("open err: $cf{pwdfile}");
	}
	push(@opened_fh, $pwd_fh);
	if (!flock($pwd_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{pwdfile}");
	}

	# IDの重複チェック
	my @data;
	while (<$pwd_fh>) {
		my ($r_history_id) = split(/:/);

		# ID先頭の分割フォルダナンバー部を取り除く
		$r_history_id =~ s/^[0-9][0-9]_//o;

		if ($in{id} eq $r_history_id) {
			close($_) foreach @opened_fh;
			&error("<b>$in{id}</b>は既に発行済です");
		}
		push(@data,$_);
	}

	# 会員ファイルオープン
	if (!open($mem_fh, '>>', $cf{memfile})) {
		close($_) foreach @opened_fh;
		&error("write err: $cf{memfile}");
	}
	push(@opened_fh, $mem_fh);
	if (!flock($mem_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{memfile}");
	}

	# 履歴ログ分割保存フォルダ番号ログファイルオープン
	if (!open($history_log_folder_number_log_fh, '+>>', $cf{history_logdir_number})) {
		close($_) foreach @opened_fh;
		error('Open Error: HistoryLog SaveFolderNumber Log');
	}
	push(@opened_fh, $history_log_folder_number_log_fh);
	if (!flock($history_log_folder_number_log_fh, 2)) {
		close($_) foreach @opened_fh;
		error('Lock Error: HistoryLog SaveFolderNumber Log');
	}
	seek($history_log_folder_number_log_fh, 0, 0);

	# 履歴ログ分割保存フォルダ番号読み取り
	my $history_log_folder_number_str = do {
		my $read_line = <$history_log_folder_number_log_fh>;
		chomp($read_line);
		if ($read_line ne '') {
			$read_line;
		} else {
			truncate($history_log_folder_number_log_fh, 0);
			seek($history_log_folder_number_log_fh, 0, 0);
			print $history_log_folder_number_log_fh "01\n";
			'01';
		}
	};

	# 履歴ログ保存フォルダ内履歴ログ数ログファイルをオープン
	if (!open($history_logfile_count_log_fh, '+>>', $cf{history_logfile_count})) {
		close($_) foreach @opened_fh;
		error("Open Error: HistoryLog Count Log");
	}
	push(@opened_fh, $history_logfile_count_log_fh);
	if (!flock($history_logfile_count_log_fh, 2)) {
		close($_) foreach @opened_fh;
		error("Lock Error: HistoryLog Count Log");
	}
	seek($history_logfile_count_log_fh, 0, 0);

	# 履歴ログ保存フォルダ内履歴ログ数を読み取り
	my $history_logfile_count = do {
		my $read_logfile_count = <$history_logfile_count_log_fh>;
		chomp($read_logfile_count);
		if ($read_logfile_count eq '') {
			# 履歴ログ保存フォルダ内履歴ログ数ログファイル 新規作成時は0とする
			truncate($history_logfile_count_log_fh, 0);
			seek($history_logfile_count_log_fh, 0, 0);
			print $history_logfile_count_log_fh "0\n";
			0;
		} else {
			# 履歴ログ保存フォルダ内履歴ログ数を読み取る
			int($read_logfile_count);
		}
	};
	if ($history_logfile_count >= $cf{number_of_logfile_in_history_logdir}) {
		# 履歴ログ保存フォルダ内履歴ログ上限数超過の場合、
		# 履歴ログ分割保存フォルダ番号をカウントアップして、ログファイルに保存
		my $new_history_log_folder_number = int($history_log_folder_number_str) + 1;
		if ($new_history_log_folder_number > 99) {
			$new_history_log_folder_number = 1;
		}
		$history_log_folder_number_str = sprintf('%02d', $new_history_log_folder_number);
		truncate($history_log_folder_number_log_fh, 0);
		seek($history_log_folder_number_log_fh, 0, 0);
		print $history_log_folder_number_log_fh "$history_log_folder_number_str\n";

		# 履歴ログ保存フォルダ内履歴ログ数カウントを初期化して、ログファイルに保存
		$history_logfile_count = 0;
		truncate($history_logfile_count_log_fh, 0);
		seek($history_logfile_count_log_fh, 0, 0);
		print $history_logfile_count_log_fh "$history_logfile_count\n";
	}

	# 履歴ログ保存フォルダを必要に応じて作成
	{
		my $save_history_dir = File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{history_logdir})), $history_log_folder_number_str);
		if (!-d $save_history_dir) {
			if (!mkdir($save_history_dir)) {
				close($_) foreach @opened_fh;
				error("Create Error: HistoryLog SaveFolder");
			}
		}
	}

	# 履歴ログ保存フォルダ内履歴ログ数をカウントアップ
	$history_logfile_count++;

	# 履歴ログ保存フォルダ内履歴ログ数をログファイルに保存
	truncate($history_logfile_count_log_fh, 0);
	seek($history_logfile_count_log_fh, 0, 0);
	print $history_logfile_count_log_fh "$history_logfile_count\n";

	# ID発行
	my $id = "${history_log_folder_number_str}_$in{id}";

	# パスワードファイル ユーザー行作成
	my $crypt = encrypt($in{pw}); # パスワード暗号化
	my $hash = saltedhash_encrypt("$id$in{pw}"); # ハッシュ作成
	push(@data,"$id:$crypt:$hash\n");

	# パスワードファイル更新
	seek($pwd_fh, 0, 0);
	print $pwd_fh @data;
	truncate($pwd_fh, tell($pwd_fh));

	# 会員ファイル更新
	print $mem_fh "$id<><><>$in{memo}<>\n";

	# 各ファイルハンドルクローズ
	close($_) foreach @opened_fh;

	$in{name}  ||= '名前なし';
	$in{name}  ||= 'E-mailなし';
	$in{memo}  ||= 'なし';

	&header;
	print <<EOM;
<h4>▽以下のとおり発行しました。</h4>
<dl>
<dt>【書込ID】<dd>$id
<dt>【履歴パスワード】<dd>$in{'pw'}
<dt>【名前】<dd>$in{'name'}
<dt>【E-mail】<dd>$in{'email'}
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

		# 会員ファイル
		my @log;
		open(IN,"$cf{memfile}") or &error("open err: $cf{memfile}");
		while (<IN>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);

			if ($in{id} eq $id) {
				@log = ($id,$nam,$eml,$memo);
				last;
			}
		}
		close(IN);

		&data_new(@log);

	# --- 修正実行
	} elsif ($in{job} eq "edit2") {

		# パスワード変更
		if ($in{pwchg} == 1) {
			my $err;
			if ($in{pw} eq "") {
				$err .= "パスワードが未入力です<br>";
			} else {
				if ($in{pw} =~ /\W/) {
					$err .= "パスワードに英数字以外の文字が含まれています<br>";
				}
			}
			if ($err) { &error($err); }

			# パスワードファイル
			my @data;
			open(DAT, '+<', $cf{pwdfile}) or &error("open err: $cf{pwdfile}");
			flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
			while (<DAT>) {
				my ($id,$pw) = split(/:/);
				if ($in{id} eq $id) {
					my $crypt = encrypt($in{pw}); # パスワード暗号化
					my $hash = saltedhash_encrypt("$id$in{pw}"); # ハッシュ作成
					$_ = "$in{id}:$crypt:$hash\n";
				}
				push(@data,$_);
			}
			seek(DAT, 0, 0);
			print DAT @data;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# 会員ファイル
		my @data;
		open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
		flock(DAT, 2) or &error("lock err: $cf{memfile}");
		while (<DAT>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);

			if ($in{id} eq $id) {
				$_ = "$id<>$in{name}<>$in{email}<>$in{memo}<>\n";
			}
			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		&msg_edit;

	# --- 削除
	} elsif ($in{job} eq "dele" && $in{id}) {

		# パスワードファイル
		my @data;
		open(DAT,"+< $cf{pwdfile}") or &error("open err: $cf{pwdfile}");
		flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
		while (<DAT>) {
			my ($id,$pw) = split(/:/);
			next if ($in{id} eq $id);

			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 会員ファイル
		@data = ();
		open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
		flock(DAT, 2) or &error("lock err: $cf{memfile}");
		while (<DAT>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);
			next if ($in{id} eq $id);

			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	# ページ数認識
	$in{page} ||= 0;
	foreach ( keys(%in) ) {
		if (/^page:(\d+)$/) {
			$in{page} = $1;
			last;
		}
	}

	&header("メニューTOP ＞ 書込IDメンテナンス");
	&back_btn;
	print <<EOM;
<b class="ttl">■書込IDメンテナンス</b>
<hr class="ttl" size="1">
<p>処理を選択して送信ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="page" value="$in{page}">
処理 : <select name="job">
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
EOM

	my $i = 0;
	open(IN,"$cf{memfile}") or &error("open err: $cf{memfile}");
	flock(IN, 1)  or &error("lock err: $cf{memfile}");
	while (<IN>) {
		$i++;
		next if ($i < $in{page} + 1);
		next if ($i > $in{page} + $cf{pg_max});

		my ($id,$nam,$eml,$memo) = split(/<>/);
		$nam ||= '名前なし';
		$eml &&= "<a href=\"mailto:$eml\">$nam</a>";
		$memo =~ s/<br>/ /g;

		print qq|<hr><input type="radio" name="id" value="$id">\n|;
		print qq|<b>$id</b> [名前] $nam [備考] $memo\n|;
	}
	close(IN);

	print "<hr>\n";

	my $next = $in{page} + $cf{pg_max};
	my $back = $in{page} - $cf{pg_max};
	if ($back >= 0) {
		print qq|<input type="submit" name="page:$back" value="前の$cf{pg_max}件">\n|;
	}
	if ($next < $i) {
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