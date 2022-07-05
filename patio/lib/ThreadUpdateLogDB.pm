package ThreadUpdateLogDB;

use strict;
use File::Basename qw/basename dirname/;
use File::Find::Rule;
use File::Spec;
use DBI;

# コンストラクタ
sub new {
	my($class, $sqlite_filename) = @_;
	if(!defined($sqlite_filename)) {
		Carp::croak("sqlite_filename is required.")
	}
	my $basedir = File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/../'));
	my $self = {
		DBH => DBI->connect("dbi:SQLite:dbname=$basedir/$sqlite_filename", { RaiseError => 1, PrintError => 0, AutoCommit => 0 }), # データベース接続
		TABLE_NAME => "thread_updatelog",
		TRANSACTION => 0,
		CLOSE => 0
	};
	bless ($self, $class);
	return $self;
}

# デストラクタ
sub DESTROY {
	my $self = shift;
	$self->close(0);
}

sub create_threadinfo {
	my $self = shift;
	my ($thread_no, $datetime_epoch, $current_log_flg) = @_;

	# 必要に応じてトランザクション処理開始
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# スレッド情報を追加
	$self->{DBH}->do("INSERT INTO $self->{TABLE_NAME} VALUES ($thread_no, $datetime_epoch, " . ($current_log_flg ? "1" : "0") . ")");
	if($self->{DBH}->err) { $self->close(1); }
}

sub update_threadinfo {
	my $self = shift;
	my ($thread_no, $datetime_epoch, $current_log_flg) = @_;

	# 必要に応じてトランザクション処理開始
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# スレッド情報を更新
	my $set = "";
	if(defined($datetime_epoch)) {
		$set .= "last_update_datetime = $datetime_epoch";
	}
	if(defined($current_log_flg)) {
		if($set ne "") { $set .= ", "; }
		$set .= "current_log_flg = " . ($current_log_flg ? "1" : "0");
	}
	$self->{DBH}->do("UPDATE $self->{TABLE_NAME} SET $set WHERE thread_no = $thread_no");
	if($self->{DBH}->err) { $self->close(1); }
}

sub delete_threadinfo {
	my $self = shift;
	my ($thread_no) = @_;

	# 必要に応じてトランザクション処理開始
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# スレッド情報を削除
	$self->{DBH}->do("DELETE FROM $self->{TABLE_NAME} WHERE thread_no = $thread_no");
	if($self->{DBH}->err) { $self->close(1); }
}

sub find_threads_by_period {
	my $self = shift;
	my ($from, $to, $current_log_hash_size, $past_log_hash_size) = @_;

	# ハッシュ メモリ確保
	my %result;
	keys(%{$result{current}}) = $current_log_hash_size;
	keys(%{$result{past}}) = $past_log_hash_size;

	# 検索条件を作成
	my $where = "";
	if(defined($from) && defined($to)) {
		$where .= "last_update_datetime BETWEEN " . $from->epoch() . " AND " . $to->epoch();
	} elsif(defined($from)) {
		$where .= "last_update_datetime >= " . $from->epoch();
	} elsif(defined($to)) {
		$where .= "last_update_datetime <= " . $to->epoch();
	}
	if($current_log_hash_size == 0 || $past_log_hash_size == 0) {
		if($where) { $where .= " AND "; }
		$where .= "current_log_flg = " . ($current_log_hash_size > 0 ? "1" : "0");
	}
	if($where) { $where = "WHERE $where"; }

	# 検索実行
	my ($thread_no, $current_log_flg);
	my $select_statement = $self->{DBH}->prepare("SELECT thread_no, current_log_flg FROM $self->{TABLE_NAME} $where");
	$select_statement->execute() || return {};
	$select_statement->bind_columns(\$thread_no, \$current_log_flg);
	while($select_statement->fetch()) {
		my $type = $current_log_flg eq "1" ? "current" : "past";
		$result{$type}{$thread_no} = undef;
	}
	$select_statement->finish();

	# ハッシュのリファレンスで返す
	return \%result;
}

# データベース再構築処理
sub rebuild_database {
	my $self = shift;
	my ($logdir) = @_;

	# 排他トランザクション処理開始
	$self->{DBH}->do("BEGIN EXCLUSIVE TRANSACTION");
	$self->{TRANSACTION} = 1;

	# 既存のテーブルを破棄し、新たに作成
	$self->{DBH}->do("DROP INDEX IF EXISTS last_update_datetime_index");
	$self->{DBH}->do("DROP TABLE IF EXISTS $self->{TABLE_NAME}");
	$self->{DBH}->do("CREATE TABLE $self->{TABLE_NAME} (
		thread_no INTEGER UNIQUE NOT NULL,
		last_update_datetime INTEGER  NOT NULL,
		current_log_flg INTEGER NOT NULL
	)");
	$self->{DBH}->do("CREATE INDEX last_update_datetime_index ON $self->{TABLE_NAME} (last_update_datetime)");

	# INSERT Prepare Statementを作成
	my $insert_statement = $self->{DBH}->prepare("INSERT INTO $self->{TABLE_NAME} VALUES (?, ?, ?)");

	# ログフォルダ内のすべてのログファイルを読み込み、
	# フォーマットに異常がなければ、最終更新日時と比較
	my @loglist = do {
		# スレッドログファイル リスト取得
		my @log_paths = File::Find::Rule->file->name(qr/^\d*\.cgi$/)->in($logdir);
		# スレッド番号 => ファイルパス リストインデックス のハッシュを作り、
		# キー(スレッド番号)で昇順ソート、対応するインデックスから
		# 昇順ソートしたスレッドログファイル リストを返す
		my %log_number_array_index_hash = map { basename($log_paths[$_], '.cgi') => $_ } 0 .. $#log_paths;
		map { $log_paths[$log_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%log_number_array_index_hash);
	};
	foreach my $logfile_path (@loglist) {
		open(DAT, $logfile_path);
		my @top = split(/<>/, <DAT>);
		if(scalar(@top) < 4) { next; } # 異常ログは読み飛ばし
		my $thread_no = $top[0];
		my $current_log_flg = $top[3] == 1 ? "1" : "0";
		my $lastupdate_datetime = "-1";

		# レスログ行読み込み
		while (<DAT>){
			chomp($_);
			my @low = split(/<>/);
			if(scalar(@low) < 12) { next; } # 異常行は読み飛ばし
			my $datetime = (split(/<>/))[11];
			if($datetime > $lastupdate_datetime) { $lastupdate_datetime = $datetime; }
		}
		close(DAT);

		# スレッド番号・最終更新日時・スレッド状態を記録
		if ($lastupdate_datetime != -1) {
			$insert_statement->execute(($thread_no, $lastupdate_datetime, $current_log_flg));
		}
	}

	# エラーがあればロールバック
	if($self->{DBH}->err) { $self->close(1); }
}

# 必要に応じてコミット/ロールバックを行い、データベース接続を切断
sub close {
	my $self = shift;
	my ($rollback) = @_;
	if(!defined($rollback)) { $rollback = 0; }

	if($self->{CLOSE} == 0) {
		if($self->{TRANSACTION}) {
			if($rollback == 0) {
				$self->{DBH}->do("COMMIT");
			} else {
				$self->{DBH}->do("ROLLBACK");
			}
		}
		$self->{DBH}->disconnect();
		$self->{CLOSE} = 1;
	}
}

1;
