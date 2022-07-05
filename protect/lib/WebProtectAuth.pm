# パッケージ名宣言
package WebProtectAuth;

# モジュール宣言
use strict;
use File::Basename qw/dirname/;
use File::Spec;
use File::ReadBackwards;

# WebProtectディレクトリ 実行パスからの相対パス取得
my $basedir = File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/../'));

# 設定ファイル取り込み
require "$basedir/init.cgi";
my %cf = &init;

# ログパスをWebProtect相対パスに置換
my @path_replace = ('pwdfile','memfile','regist_log');
for my $key (@path_replace) {
	if(!File::Spec->file_name_is_absolute($cf{$key})) {
		$cf{$key} = File::Spec->canonpath("$basedir/$cf{$key}");
	}
}

# 処理結果定数定義
use constant {
	SUCCESS                     =>  0,
	ID_FILE_OPEN_ERROR          =>  1,
	MEMBER_FILE_OPEN_ERROR      =>  1 << 1,
	REGIST_LOG_FILE_OPEN_ERROR  =>  1 << 2,
	IS_DENY_HOST                =>  1 << 3,
	ID_NOTFOUND                 =>  1 << 4,
	PASS_MISMATCH               =>  1 << 5,
	ID_EXISTS                   =>  1 << 6,
	REPEATITIVE_REGIST_LIMIT    =>  1 << 7,
	DUPLICATE_EMAIL_ADDRESS     =>  1 << 8,
	IS_DENY_EMAIL_ADDRESS       =>  1 << 9
};

# ユーザ登録アクセス制限ホストであるかどうか(プライベート関数)
my $isDenyHost = sub {
	shift;
	my ($host,$addr) = @_;

	foreach ( split(/\s+/, $cf{deny}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		if ($host =~ /$_/i || $addr =~ /$_/i) {
			return 1;
		}
	}

	return 0;
};

# 禁止ワードを含むメールアドレスであるかどうか(プライベート関数)
my $isDenyEMailAddress = sub {
	shift;
	my ($eml) = @_;
	my @deny_words = split(/,/, $cf{deny_email});

	for my $word (@deny_words) {
		if($eml =~ /\Q$word/i) {
			return 1;
		}
	}

	return 0;
};

# ユーザー認証
sub authenticate {
	my ($id,$pw) = @_;

	# パスファイルオープン
	my $crypt;
	open(IN,"$cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	while (<IN>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$crypt = $r_pw;
			last;
		}
	}
	close(IN);

	# ID不一致の場合
	chomp($crypt);
	if (!$crypt) { return ID_NOTFOUND; }

	# 照合処理
	if (&decrypt($pw, $crypt) != 1) { return PASS_MISMATCH; }
	
	# 認証成功
	return SUCCESS;
}

# 新規ユーザー登録
sub create {
	my ($id,$pw,$name,$eml,$memo,$notadmin_regist) = @_;
	my ($host,$addr) = &get_host;
	my ($time,$date) = &get_time;
	my $repeatitive_regist_boundary_time = $time - $cf{wait_regist};

	# ユーザー登録制限ホストチェック
	if($pw eq "" && self->$isDenyHost($host,$addr)) { return IS_DENY_HOST; }

	# 連続新規ユーザー登録チェック
	if($notadmin_regist == 1) {
		open(REGISTLOG,"< $cf{regist_log}") or return REGIST_LOG_FILE_OPEN_ERROR;
		while (<REGISTLOG>) {
			my ($r_host,$r_time) = split(/<>/);
			if ($r_host eq $host && $r_time >= $repeatitive_regist_boundary_time) {
				close(REGISTLOG);
				return REPEATITIVE_REGIST_LIMIT;
			}
		}
		close(REGISTLOG);
	}

	# 禁止ワードを含むメールアドレスであるかどうかチェック
	if($notadmin_regist == 1 && self->$isDenyEMailAddress($eml)) { return IS_DENY_EMAIL_ADDRESS; }

	# コード変換
	Jcode::convert($name, 'sjis');

	# 会員ファイル ID・メールアドレスの重複チェック
	my @data = ("$id<>$name<>$eml<>$memo<>\n");
	my $flg = SUCCESS;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id, $r_eml) = (split(/<>/))[0,2];
		# IDの重複チェック
		if($r_id eq $id) {
			$flg |= ID_EXISTS;
		}
		# メールアドレスの重複チェック(管理者による登録の場合チェックしない)
		if($notadmin_regist == 1 && $r_eml eq $eml) {
			$flg |= DUPLICATE_EMAIL_ADDRESS;
		}
		# 全てのエラーフラグが立っている時にはループ脱出
		if($flg == (ID_EXISTS | DUPLICATE_EMAIL_ADDRESS) || $notadmin_regist != 1 && $flg == ID_EXISTS) {
			last;
		}
		push(@data, $_);
	}
	if($flg == SUCCESS) {
		# 重複が無かった場合に書き込み 
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
	}
	close(DAT);
	if($flg != SUCCESS) { return $flg; };

	# パス発行
	if($pw eq "") {
		my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
		srand;
		foreach (1 .. 8) {
			$pw .= $char[int(rand(@char))];
		}
	}

	# 暗号化
	my $crypt = &encrypt($pw);

	# パスワードファイル更新
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	seek(DAT, 0, 2);
	print DAT "$id:$crypt\n";
	close(DAT);

	# 新規ユーザー登録 ログ記録
	if($notadmin_regist == 1) {
		my @tmp = ("$host<>$time<>\n");
		open(REGISTLOG,"+< $cf{regist_log}") or return REGIST_LOG_FILE_OPEN_ERROR;
		while (<REGISTLOG>) {
			my $r_time = (split(/<>/))[1];
			if ($r_time < $repeatitive_regist_boundary_time) {
				last;
			}
			push(@tmp, $_);
		}
		seek(REGISTLOG, 0, 0);
		print REGISTLOG @tmp;
		truncate(REGISTLOG, tell(REGISTLOG));
		close(REGISTLOG);
	}

	return (SUCCESS, $pw, $date);
}

# ユーザー情報取得
sub read {
	my ($id) = @_;

	# 会員ファイル
	my (@log, $flg);
	open(IN,"$cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	while (<IN>) {
		my ($r_id,$nam,$eml,$memo) = split(/<>/);

		if ($r_id eq $id) {
			@log = ($id,$nam,$eml,$memo);
			$flg = 1;
			last;
		}
	}
	close(IN);
	
	if($flg) {
		return (SUCCESS, @log);
	} else {
		return ID_NOTFOUND;
	}
}

# 複数ユーザー情報取得
sub multiread {
	my ($page, $descending) = @_;
	my @results;

	my $i = 0;
	if($descending == 0) {
		# ユーザー登録が古い順
		my $fh = File::ReadBackwards->new("$cf{memfile}", "\n") or return MEMBER_FILE_OPEN_ERROR;
		until($fh->eof()) {
			my $line = $fh->readline();
			$i++;
			next if ($i < $page + 1);
			next if ($i > $page + $cf{pg_max});
	
			my @result = split(/<>/, $line);
			push(@results, \@result);
		}
		$fh->close();
	} else {
		# ユーザー登録が新しい順
		open(IN,"$cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
		while (<IN>) {
			$i++;
			next if ($i < $page + 1);
			next if ($i > $page + $cf{pg_max});
	
			my @result = split(/<>/);
			push(@results, \@result);
		}
		close(IN);
	}

	return (SUCCESS, $i, @results);
}

# パスワード変更
sub update_password {
	my ($id, $pw, $new_pw, $force) = @_;
	my ($host,$addr) = &get_host;

	# ユーザー登録制限ホストチェック
	if($force != 1 && self->$isDenyHost($host,$addr)) { return IS_DENY_HOST; }

	# 暗号化
	my $pwd = &encrypt($new_pw);

	# IDチェック
	my ($flg, $crypt, @data);
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$flg++;
			$crypt = $r_pw;
			$_ = "$id:$pwd\n";
		}
		push(@data,$_);
	}

	if (!$flg) {
		close(DAT);
		return ID_NOTFOUND;
	}

	# 照合
	if($force != 1) {
		chomp($crypt);
		if ( &decrypt($pw, $crypt) != 1 ) {
			close(DAT);
			return (PASS_MISMATCH, $crypt);
		}
	}

	# パスファイル更新
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

# ユーザー情報変更
sub update_userinfo {
	my ($id, $name, $email, $memo) = @_;

	# 会員ファイル
	my @data;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id) = split(/<>/);

		if ($r_id eq $id) {
			$_ = "$r_id<>$name<>$email<>$memo<>\n";
		}
		push(@data,$_);
	}
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

sub delete {
	my ($id, $pw, $force) = @_;

	# IDチェック
	my ($flg, $crypt, @data);
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$flg++;
			$crypt = $r_pw;
			next;
		}
		push(@data,$_);
	}
	if (!$flg) {
		close(DAT);
		return ID_NOTFOUND;
	}

	# 照合
	if($force != 1) {
		chomp($crypt);
		if (&decrypt($pw, $crypt) != 1) {
			close(DAT);
			return PASS_MISMATCH;
		}
	}

	# パスファイル更新
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 会員ファイル
	my @data;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	while (<DAT>) {
		my ($r_id) = split(/<>/);
		next if ($r_id eq $id);

		push(@data,$_);
	}
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

1;
