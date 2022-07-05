#!/usr/local/bin/perl

#┌─────────────────────────────
#│ WEB PROTECT : manager.cgi - 2011/10/02
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────

our %cf;
BEGIN {
	# 設定ファイル取り込み
	require './init.cgi';
	%cf = &init;
}

use strict;
use CGI::Carp qw(fatalsToBrowser);
use Encode qw();
use File::Basename;
use File::Spec;
use JSON::XS;
use lib qq($main::cf{webpatio_lib_path});
use HistoryCookie;
use UniqueCookie;

# データ受理
my %in = &parse_form;

# 処理分岐
if ($in{mode} eq "new_user") { &new_user; }
if ($in{mode} eq "chg_pwd") { &chg_pwd; }
&error("不正なアクセスです");

#-----------------------------------------------------------
#  ユーザ登録
#-----------------------------------------------------------
sub new_user {
	my ($regist_log_fh, $pwd_fh, $mem_fh, $history_log_folder_number_log_fh, $history_logfile_count_log_fh, $history_log_fh);
	my @opened_fh;

	# 発行制限
	if ($cf{pwd_regist} > 1) { &error("不正なアクセスです"); }

	# チェック
	my $err;
	if (length($in{id}) < 4 || length($in{id}) > 8) {
		$err .= "書込IDは4～8文字で入力してください<br>";
	}
	if ($in{id} =~ /\W/) {
		$err .= "書込IDに英数字以外の文字が含まれています<br>";
	}
	if ($err) { &error($err); }

	# 時刻取得
	my ($time) = get_time();

	# ホスト名を取得
	my ($host,$addr) = &get_host;
	&deny_host($host,$addr);

	# 全てのCookieを取得
	my %cookies;
	foreach my $set (split(/; */, $ENV{'HTTP_COOKIE'})) {
		my ($key, $val) = split(/=/, $set);
		$cookies{$key} = $val;
	}

	# ユニークCookieAを取得
	my $cookie_a = do {
		my $instance = UniqueCookie->new($cf{webpatio_cookie_current_dirpath});
		$instance->value() || '-';
	};

	# 登録IDを取得
	my $user_id_on_cookie = do {
		# データをURLデコードして復元
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}";
		my @webpatio_cookie;
		foreach my $val (split(/<>/, $cookies{$cookie_name})) {
			$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
			push(@webpatio_cookie, $val);
		}
		$webpatio_cookie[5] || '-';
	};

	# 書込IDを取得
	my $history_cookie = HistoryCookie->new();
	my $chistory_id = $history_cookie->get_history_id();

	# 連続書込ID発行チェック
	my $repeatitive_regist_boundary_time = $time - $cf{wait_regist};
	my $is_exempt_host = scalar(grep { index($host, $_) != -1 } @{$cf{wait_regist_exempt_hosts}}) > 0; # 除外ホストかどうか
	if (!open($regist_log_fh, '+<', $cf{regist_log})) {
		close($_) foreach @opened_fh;
		&error("open err: $cf{regist_log}");
	}
	push(@opened_fh, $regist_log_fh);
	if (!flock($regist_log_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{regist_log}");
	}
	seek($regist_log_fh, 0, 0);
	while (<$regist_log_fh>) {
		# 判定一致フラッグ
		my $flg = 0;

		# ログ行読み取り
		my ($r_host, $r_cookie_a, $r_user_id, $r_history_id, $r_time) = split(/<>/);
		# 連続発行制限時間内でなければスキップ
		if ($r_time < $repeatitive_regist_boundary_time) {
			next;
		}
		# ホスト一致判定
		$flg ||= !$is_exempt_host && $r_host eq $host;
		# CookieA一致判定
		$flg ||= $r_cookie_a ne '-' && $r_cookie_a eq $cookie_a;
		# 登録ID一致判定
		$flg ||= $r_user_id ne '-' && $r_user_id eq $user_id_on_cookie;
		# 書込ID一致判定
		$flg ||= defined($chistory_id) && $r_history_id eq $chistory_id;

		# いずれかの判定で一致した場合
		if ($flg) {
			close($_) foreach @opened_fh;
			&error('連続登録はもうしばらく時間をおいて下さい');
		}
	}

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
			&error("既に使用されている書込IDです");
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
		if ($read_line ne '') {
			$read_line;
		} else {
			truncate($history_log_folder_number_log_fh, 0);
			seek($history_log_folder_number_log_fh, 0, 0);
			print $history_log_folder_number_log_fh "01";
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
		if ($read_logfile_count eq '') {
			# 履歴ログ保存フォルダ内履歴ログ数ログファイル 新規作成時は0とする
			truncate($history_logfile_count_log_fh, 0);
			seek($history_logfile_count_log_fh, 0, 0);
			print $history_logfile_count_log_fh "0";
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
		print $history_log_folder_number_log_fh "$history_log_folder_number_str";

		# 履歴ログ保存フォルダ内履歴ログ数カウントを初期化して、ログファイルに保存
		$history_logfile_count = 0;
		truncate($history_logfile_count_log_fh, 0);
		seek($history_logfile_count_log_fh, 0, 0);
		print $history_logfile_count_log_fh "$history_logfile_count";
	}

	# ID発行
	my $id = "${history_log_folder_number_str}_$in{id}";

	# パス発行
	my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
	my $pw;
	srand;
	foreach (1 .. 8) {
		$pw .= $char[int(rand(@char))];
	}

	# 履歴ログ保存フォルダを必要に応じて作成
	my $save_history_dir = File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{history_logdir})), $history_log_folder_number_str);
	if (!-d $save_history_dir) {
		if (!mkdir($save_history_dir)) {
			close($_) foreach @opened_fh;
			error("Create Error: HistoryLog SaveFolder");
		}
	}

	# Cookieに保存していた各種設定を読み取り、書込IDログに記録
	# 書込IDログファイルオープン
	if (!open($history_log_fh, '>', File::Spec->catfile($save_history_dir, "$id.log"))) {
		close($_) foreach @opened_fh;
		error("Open Error: HistoryLog");
	}
	push(@opened_fh, $history_log_fh);
	if (!flock($history_log_fh, 6)) {
		# 複数のプロセスからこの箇所で同時オープンすることはないので、
		# ロック検知時は0を返す
		close($_) foreach @opened_fh;
		error("Lock Error: HistoryLog");
	}
	# 存在するコピー対象のCookie設定を読み取り、JSONを構築
	my $json = JSON::XS->new();
	my %copy_settings;
	## 文字列を期待する設定値のコピー
	foreach my $cookie_suffix ('NGThread', 'NGID_LIST', 'NGNAME_LIST', 'NGWORD_LIST') {
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}_$cookie_suffix";
		if (exists($cookies{$cookie_name}) && $cookies{$cookie_name} ne '') {
			my $load_value = do {
				my $urldecoded_value = $cookies{$cookie_name};
				$urldecoded_value =~ s/\+/ /g;
				$urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack("H2", $1)/eg;
				$urldecoded_value = Encode::decode('UTF-8', $urldecoded_value);
				$json->utf8(0)->decode($urldecoded_value);
			};
			$copy_settings{$cookie_suffix} = $load_value;
		}
	}
	## 数値によるフラグ(0/1)を期待する設定値のコピー
	foreach my $cookie_suffix ('CHAIN_NG', 'HIGHLIGHT_NAME') {
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}_$cookie_suffix";
		if (exists($cookies{$cookie_name}) && ($cookies{$cookie_name} eq '0' || $cookies{$cookie_name} eq '1')) {
			$copy_settings{$cookie_suffix} = int($cookies{$cookie_name});
		}
	}

	# 書込IDログファイルに書き込み
	print $history_log_fh $json->utf8(1)->encode(\%copy_settings);

	# 履歴ログ保存フォルダ内履歴ログ数をカウントアップ
	$history_logfile_count++;

	# 履歴ログ保存フォルダ内履歴ログ数をログファイルに保存
	truncate($history_logfile_count_log_fh, 0);
	seek($history_logfile_count_log_fh, 0, 0);
	print $history_logfile_count_log_fh "$history_logfile_count";

	# パスワードファイル ユーザー行作成
	my $crypt = encrypt($pw); # パスワード暗号化
	my $hash = saltedhash_encrypt("$id$pw"); # ハッシュを作成
	push(@data,"$id:$crypt:$hash\n");

	# パスワードファイル更新
	seek($pwd_fh, 0, 0);
	print $pwd_fh @data;
	truncate($pwd_fh, tell($pwd_fh));

	# 会員ファイル更新
	print $mem_fh "$id<><><><>\n";

	# 書込ID発行ログファイル更新
	seek($regist_log_fh, 0, 0);
	my @regist_log_write_tmp = ("$host<>$cookie_a<>$user_id_on_cookie<>$id<>$time<>\n");
	while (<$regist_log_fh>) {
		my $r_time = (split(/<>/))[4];
		if ($r_time < $repeatitive_regist_boundary_time) {
			last;
		}
		push(@regist_log_write_tmp, $_);
	}
	seek($regist_log_fh, 0, 0);
	print $regist_log_fh @regist_log_write_tmp;
	truncate($regist_log_fh, tell($regist_log_fh));

	# 各ファイルハンドルクローズ
	close($_) foreach @opened_fh;

	# 発行完了時にログイン
	$history_cookie->login($id, $pw);

	# 完了画面
	my $msg = qq|書込IDと履歴パスワードを発行しました。<br><br>書込ID：$id<br>パスワード：$pw|;
	&message("書込ID・履歴パスワード発行完了", $msg);
}

#-----------------------------------------------------------
#  ユーザPW変更
#-----------------------------------------------------------
sub chg_pwd {
	# 発行制限
	if ($cf{pwd_regist} > 2) { &error("不正なアクセスです"); }

	# ホスト名を取得
	my ($host,$addr) = &get_host;
	&deny_host($host,$addr);

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

	# チェック
	my $err;
	if ($login_id eq "") { $err .= "書込IDが入力モレです<br>"; }
	if ($in{pw} eq "") { $err .= "旧パスワードが入力モレです<br>"; }
	if ($in{pw1} eq "") { $err .= "新パスワードが入力モレです<br>"; }
	if ($in{pw1} ne $in{pw2}) { $err .= "新パスワードで再度入力分が異なります<br>";	}
	if (length($in{pw1}) > 8) { $err .= "新パスワードは8文字以内です<br>"; }
	if ($in{pw1} =~ /[^\w_]/) { $err .= "パスワードは英数字と_(アンダースコア)のみ使用可能です<br>"; }
	if ($err) { &error($err); }

	# IDチェック
	my ($flg, $new_user_hash, @data);
	open(DAT,"+< $cf{pwdfile}") or &error("open err: $cf{pwdfile}");
	flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
	while (<DAT>) {
		my ($id,$crypt) = split(/:/);

		if ($login_id eq $id) {
			$flg++;
			# 照合
			chomp($crypt);
			if ($in{pw} ne decrypt($crypt)) {
				close(DAT);
				&error("認証できません");
			}
			$new_user_hash = saltedhash_encrypt("$id$in{pw1}");
			$_ = "$id:" . encrypt($in{pw1}) . ":$new_user_hash\n";
		}
		push(@data,$_);
	}

	if (!$flg) {
		close(DAT);
		&error("認証できません");
	}

	# パスファイル更新
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 更新した情報で再度ログイン
	my $history_cookie = HistoryCookie->new();
	$history_cookie->logout();
	$history_cookie->login($login_id, $in{pw1});

	# 完了画面
	&message("履歴パスワード変更完了", "履歴パスワードを変更しました。");
}

#-----------------------------------------------------------
#  アクセス制限
#-----------------------------------------------------------
sub deny_host {
	my ($host,$addr) = @_;

	my $flg;
	foreach ( split(/\s+/, $cf{deny}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		if ($host =~ /$_/i || $addr =~ /$_/i) {
			$flg++;
			last;
		}
	}
	if ($flg) { &error("現在登録休止中です"); }
}
