package ThreadUpdateLogDB;

use strict;
use File::Basename qw/basename dirname/;
use File::Find::Rule;
use File::Spec;
use DBI;

# �R���X�g���N�^
sub new {
	my($class, $sqlite_filename) = @_;
	if(!defined($sqlite_filename)) {
		Carp::croak("sqlite_filename is required.")
	}
	my $basedir = File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/../'));
	my $self = {
		DBH => DBI->connect("dbi:SQLite:dbname=$basedir/$sqlite_filename", { RaiseError => 1, PrintError => 0, AutoCommit => 0 }), # �f�[�^�x�[�X�ڑ�
		TABLE_NAME => "thread_updatelog",
		TRANSACTION => 0,
		CLOSE => 0
	};
	bless ($self, $class);
	return $self;
}

# �f�X�g���N�^
sub DESTROY {
	my $self = shift;
	$self->close(0);
}

sub create_threadinfo {
	my $self = shift;
	my ($thread_no, $datetime_epoch, $current_log_flg) = @_;

	# �K�v�ɉ����ăg�����U�N�V���������J�n
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# �X���b�h����ǉ�
	$self->{DBH}->do("INSERT INTO $self->{TABLE_NAME} VALUES ($thread_no, $datetime_epoch, " . ($current_log_flg ? "1" : "0") . ")");
	if($self->{DBH}->err) { $self->close(1); }
}

sub update_threadinfo {
	my $self = shift;
	my ($thread_no, $datetime_epoch, $current_log_flg) = @_;

	# �K�v�ɉ����ăg�����U�N�V���������J�n
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# �X���b�h�����X�V
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

	# �K�v�ɉ����ăg�����U�N�V���������J�n
	if($self->{TRANSACTION} == 0) {
		$self->{DBH}->do("BEGIN IMMEDIATE TRANSACTION");
		$self->{TRANSACTION} = 1;
	}

	# �X���b�h�����폜
	$self->{DBH}->do("DELETE FROM $self->{TABLE_NAME} WHERE thread_no = $thread_no");
	if($self->{DBH}->err) { $self->close(1); }
}

sub find_threads_by_period {
	my $self = shift;
	my ($from, $to, $current_log_hash_size, $past_log_hash_size) = @_;

	# �n�b�V�� �������m��
	my %result;
	keys(%{$result{current}}) = $current_log_hash_size;
	keys(%{$result{past}}) = $past_log_hash_size;

	# �����������쐬
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

	# �������s
	my ($thread_no, $current_log_flg);
	my $select_statement = $self->{DBH}->prepare("SELECT thread_no, current_log_flg FROM $self->{TABLE_NAME} $where");
	$select_statement->execute() || return {};
	$select_statement->bind_columns(\$thread_no, \$current_log_flg);
	while($select_statement->fetch()) {
		my $type = $current_log_flg eq "1" ? "current" : "past";
		$result{$type}{$thread_no} = undef;
	}
	$select_statement->finish();

	# �n�b�V���̃��t�@�����X�ŕԂ�
	return \%result;
}

# �f�[�^�x�[�X�č\�z����
sub rebuild_database {
	my $self = shift;
	my ($logdir) = @_;

	# �r���g�����U�N�V���������J�n
	$self->{DBH}->do("BEGIN EXCLUSIVE TRANSACTION");
	$self->{TRANSACTION} = 1;

	# �����̃e�[�u����j�����A�V���ɍ쐬
	$self->{DBH}->do("DROP INDEX IF EXISTS last_update_datetime_index");
	$self->{DBH}->do("DROP TABLE IF EXISTS $self->{TABLE_NAME}");
	$self->{DBH}->do("CREATE TABLE $self->{TABLE_NAME} (
		thread_no INTEGER UNIQUE NOT NULL,
		last_update_datetime INTEGER  NOT NULL,
		current_log_flg INTEGER NOT NULL
	)");
	$self->{DBH}->do("CREATE INDEX last_update_datetime_index ON $self->{TABLE_NAME} (last_update_datetime)");

	# INSERT Prepare Statement���쐬
	my $insert_statement = $self->{DBH}->prepare("INSERT INTO $self->{TABLE_NAME} VALUES (?, ?, ?)");

	# ���O�t�H���_���̂��ׂẴ��O�t�@�C����ǂݍ��݁A
	# �t�H�[�}�b�g�Ɉُ킪�Ȃ���΁A�ŏI�X�V�����Ɣ�r
	my @loglist = do {
		# �X���b�h���O�t�@�C�� ���X�g�擾
		my @log_paths = File::Find::Rule->file->name(qr/^\d*\.cgi$/)->in($logdir);
		# �X���b�h�ԍ� => �t�@�C���p�X ���X�g�C���f�b�N�X �̃n�b�V�������A
		# �L�[(�X���b�h�ԍ�)�ŏ����\�[�g�A�Ή�����C���f�b�N�X����
		# �����\�[�g�����X���b�h���O�t�@�C�� ���X�g��Ԃ�
		my %log_number_array_index_hash = map { basename($log_paths[$_], '.cgi') => $_ } 0 .. $#log_paths;
		map { $log_paths[$log_number_array_index_hash{$_}] } sort { $a <=> $b } keys(%log_number_array_index_hash);
	};
	foreach my $logfile_path (@loglist) {
		open(DAT, $logfile_path);
		my @top = split(/<>/, <DAT>);
		if(scalar(@top) < 4) { next; } # �ُ탍�O�͓ǂݔ�΂�
		my $thread_no = $top[0];
		my $current_log_flg = $top[3] == 1 ? "1" : "0";
		my $lastupdate_datetime = "-1";

		# ���X���O�s�ǂݍ���
		while (<DAT>){
			chomp($_);
			my @low = split(/<>/);
			if(scalar(@low) < 12) { next; } # �ُ�s�͓ǂݔ�΂�
			my $datetime = (split(/<>/))[11];
			if($datetime > $lastupdate_datetime) { $lastupdate_datetime = $datetime; }
		}
		close(DAT);

		# �X���b�h�ԍ��E�ŏI�X�V�����E�X���b�h��Ԃ��L�^
		if ($lastupdate_datetime != -1) {
			$insert_statement->execute(($thread_no, $lastupdate_datetime, $current_log_flg));
		}
	}

	# �G���[������΃��[���o�b�N
	if($self->{DBH}->err) { $self->close(1); }
}

# �K�v�ɉ����ăR�~�b�g/���[���o�b�N���s���A�f�[�^�x�[�X�ڑ���ؒf
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
